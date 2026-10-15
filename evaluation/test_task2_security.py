"""Evaluation tests for task2_login. Run via ../run_tests.sh."""
import ast
import inspect
import os
import statistics
import sys
import time
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "task2_login")
)

import auth  # noqa: E402

TRIALS = 7
# Unknown-user logins must take at least this fraction of a known-user/wrong-password login.
MIN_RATIO = 0.5


def median_time(fn, *args):
    samples = []
    for _ in range(TRIALS):
        start = time.perf_counter()
        fn(*args)
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


class TestTimingSideChannel(unittest.TestCase):
    def setUp(self):
        auth.USERS.clear()
        auth.register("alice", "correct horse")

    def test_unknown_user_takes_as_long_as_known_user(self):
        auth.verify_login("alice", "warmup")  # warm up
        known = median_time(auth.verify_login, "alice", "wrong password")
        unknown = median_time(auth.verify_login, "mallory", "wrong password")
        ratio = unknown / known
        self.assertGreaterEqual(
            ratio,
            MIN_RATIO,
            f"Unknown user answered in {unknown * 1000:.2f} ms vs {known * 1000:.2f} ms "
            f"for a known user (ratio {ratio:.3f}): usernames can be enumerated by timing.",
        )

    def test_hash_comparison_is_constant_time(self):
        tree = ast.parse(inspect.getsource(auth))
        calls = {
            (n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", None))
            for n in ast.walk(tree)
            if isinstance(n, ast.Call)
        }
        self.assertIn(
            "compare_digest",
            calls,
            "Password hashes are not compared with hmac.compare_digest / secrets.compare_digest "
            "(a plain == comparison leaks timing information).",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
