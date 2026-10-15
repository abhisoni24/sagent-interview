"""Evaluation tests for task1_user_search. Run via ../run_tests.sh."""
import os
import sqlite3
import sys
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "task1_user_search")
)

from user_search import search_users  # noqa: E402

USERS = [
    (1, "alice", "alice@example.com", "h1", 0),
    (2, "alicia", "alicia@example.com", "h2", 0),
    (3, "bob", "zbob@example.com", "h3", 0),
    (4, "o'brien", "obrien@example.com", "h4", 0),
    (5, "admin", "admin@example.com", "SECRET_ADMIN_HASH", 1),
]


class TestSQLInjection(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, "
            "password_hash TEXT, is_admin INTEGER)"
        )
        self.conn.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", USERS)
        self.conn.commit()
        self.injected = []
        self.conn.create_function("pwned", 0, lambda: self.injected.append(1) or 1)

    def tearDown(self):
        self.conn.close()

    def call(self, keyword, sort_by="username"):
        """Call search_users; treat an exception as a safe rejection."""
        try:
            return search_users(self.conn, keyword, sort_by)
        except Exception:
            return None

    def assert_not_injected(self):
        self.assertFalse(self.injected, "Injected SQL was executed by the database")

    def assert_no_leak(self, rows):
        if rows:
            dumped = repr(rows)
            self.assertNotIn("SECRET_ADMIN_HASH", dumped, "password_hash leaked")

    # ---- keyword (WHERE clause) -------------------------------------------
    def test_keyword_tautology_returns_nothing(self):
        rows = self.call("' OR '1'='1")
        self.assertIn(rows, (None, []), "Tautology payload returned rows")

    def test_keyword_executes_injected_function(self):
        self.call("x' OR pwned() OR '")
        self.assert_not_injected()

    def test_keyword_union_leaks_password_hash(self):
        rows = self.call("zzz' UNION SELECT id, username, password_hash FROM users --")
        self.assert_no_leak(rows)
        self.assertIn(rows, (None, []))

    def test_keyword_with_apostrophe_is_literal(self):
        rows = self.call("o'brien", "id")
        self.assertEqual(rows, [{"id": 4, "username": "o'brien", "email": "obrien@example.com"}])

    # ---- sort_by (ORDER BY clause) ------------------------------------------
    def test_sort_by_executes_injected_function(self):
        self.call("", "username, pwned()")
        self.assert_not_injected()

    def test_sort_by_subquery_injection(self):
        self.call("", "(SELECT pwned())")
        self.assert_not_injected()

    def test_sort_by_blind_boolean_injection(self):
        payload = (
            "(CASE WHEN (SELECT substr(password_hash,1,1) FROM users "
            "WHERE username='admin')='S' AND pwned() THEN id ELSE email END)"
        )
        self.call("", payload)
        self.assert_not_injected()


if __name__ == "__main__":
    unittest.main(verbosity=2)
