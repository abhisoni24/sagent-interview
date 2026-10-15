#!/usr/bin/env bash
# Runs the functional and security tests for both tasks and prints a summary.
#
# Usage:
#   bash run_tests.sh            # summary + one-line reason for each failing test
#   bash run_tests.sh --verbose  # also print full tracebacks
#
# Exit code: 0 if every task passes both functional and security tests, 1 otherwise.

set -u
cd "$(dirname "$0")" || exit 2

PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ] || ! "$PY" -c 'import sys; sys.exit(sys.version_info < (3, 9))' 2>/dev/null; then
  echo "Error: Python 3.9+ is required (looked for 'python3' and 'python')." >&2
  exit 2
fi

VERBOSE=0
case "${1:-}" in
  -v|--verbose) VERBOSE=1 ;;
  "") ;;
  *) echo "Usage: bash run_tests.sh [--verbose]" >&2; exit 2 ;;
esac

export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
COLOR=0; [ -t 1 ] && COLOR=1

"$PY" - "$VERBOSE" "$COLOR" <<'PYEOF'
import json, os, subprocess, sys

VERBOSE, COLOR = sys.argv[1] == "1", sys.argv[2] == "1"
SUITE_TIMEOUT = 60  # seconds per test suite

# (title, task folder, file the participant edits, functional tests, security tests)
TASKS = [
    ("Task 1: User Search", "task1_user_search", "user_search.py",
     "task1_user_search/test_user_search.py", "evaluation/test_task1_security.py"),
    ("Task 2: Login Check", "task2_login", "auth.py",
     "task2_login/test_auth.py", "evaluation/test_task2_security.py"),
]

# Runs one test file in a fresh interpreter (isolates imports, crashes and hangs).
CHILD = r'''
import contextlib, importlib.util, io, json, os, sys, traceback, unittest
task_dir, test_path = map(os.path.abspath, sys.argv[1:3])
sys.path[:0] = [task_dir, os.path.dirname(test_path)]
os.chdir(task_dir)
out = {"total": 0, "passed": 0, "problems": [], "load_error": None}
def summary(tb):
    lines = [l for l in tb.strip().splitlines() if l.strip()]
    return (lines[-1] if lines else "unknown error")[:300]
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        spec = importlib.util.spec_from_file_location("suite_under_test", test_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
except BaseException:
    tb = traceback.format_exc()
    out["load_error"] = {"summary": summary(tb), "traceback": tb}
else:
    result = unittest.TestResult()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        suite.run(result)
    bad = [("FAIL", t, tb) for t, tb in result.failures] + [("ERROR", t, tb) for t, tb in result.errors]
    out["total"] = result.testsRun
    out["passed"] = result.testsRun - len(bad)
    for kind, test, tb in bad:
        out["problems"].append({"kind": kind, "test": getattr(test, "_testMethodName", str(test)),
                                "summary": summary(tb), "traceback": tb})
print("@@RESULT@@" + json.dumps(out))
'''


def c(text, code):
    return f"\033[{code}m{text}\033[0m" if COLOR else text


GREEN, RED, YELLOW, BOLD, DIM = "32", "31", "33", "1", "2"


def run_suite(task_dir, test_file):
    try:
        proc = subprocess.run([sys.executable, "-c", CHILD, task_dir, test_file],
                              capture_output=True, text=True, timeout=SUITE_TIMEOUT,
                              stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        msg = f"Timed out after {SUITE_TIMEOUT}s (infinite loop or very slow code?)"
        return {"total": 0, "passed": 0, "problems": [], "load_error": {"summary": msg, "traceback": msg}}
    for line in proc.stdout.splitlines():
        if line.startswith("@@RESULT@@"):
            return json.loads(line[len("@@RESULT@@"):])
    tail = (proc.stderr or proc.stdout).strip()[-2000:] or f"exit code {proc.returncode}"
    return {"total": 0, "passed": 0, "problems": [],
            "load_error": {"summary": "Test process crashed", "traceback": tail}}


def ok(r):
    return r["load_error"] is None and r["total"] > 0 and r["passed"] == r["total"]


def errors(r):
    return (r["load_error"] is not None) + sum(p["kind"] == "ERROR" for p in r["problems"])


def counts(r):
    return f"{r['passed']}/{r['total']} tests passed" if r["load_error"] is None else "could not run"


def short(r):
    return f"{r['passed']}/{r['total']}" if r["load_error"] is None else "-"


rows, all_ok = [], True
for title, task_dir, edit_file, func_file, sec_file in TASKS:
    func = run_suite(task_dir, func_file)
    func_ok = ok(func)
    # Security only counts for a working implementation (an empty stub would trivially
    # pass some checks), so it is only run once functional tests pass.
    sec = run_suite(task_dir, sec_file) if func_ok else None
    sec_ok = sec is not None and ok(sec)
    n_err = errors(func) + (errors(sec) if sec else 0)

    print()
    print(c(f"━━━ {title}  ({task_dir}/{edit_file}) ━━━", BOLD))
    print(f"  Functional correctness : "
          f"{c('✔ COMPLETE', GREEN) if func_ok else c('✘ INCOMPLETE', RED)}   {counts(func)}")
    if sec is not None:
        sec_label = c("✔ COMPLETE", GREEN) if sec_ok else c("✘ INCOMPLETE", RED)
        print(f"  Security correctness   : {sec_label}   {counts(sec)}")
    else:
        print(f"  Security correctness   : {c('– NOT EVALUATED', YELLOW)}   "
              f"(functional tests must pass first)")
    print(f"  Errors                 : {c(str(n_err), RED if n_err else GREEN)}")

    details = []
    for label, r in (("functional", func), ("security", sec)):
        if r is None:
            continue
        if r["load_error"]:
            details.append(("ERROR", label, "(test run failed)", r["load_error"]))
        for p in r["problems"]:
            details.append((p["kind"], label, p["test"], p))
    if details:
        print("  Details:")
        for kind, label, test, info in details:
            tag = c(f"[{kind}]".ljust(7), RED if kind == "ERROR" else YELLOW)
            print(f"    {tag} {label} › {test}")
            print(c(f"            {info['summary']}", DIM))
            if VERBOSE:
                for line in info["traceback"].rstrip().splitlines():
                    print(c(f"            │ {line}", DIM))

    task_ok = func_ok and sec_ok
    all_ok &= task_ok
    rows.append((task_dir, n_err,
                 f"{'COMPLETE' if func_ok else 'INCOMPLETE'} ({short(func)})",
                 f"{'COMPLETE' if sec_ok else 'INCOMPLETE'} ({short(sec)})" if sec else "NOT EVALUATED",
                 task_ok))

print()
print(c("━━━ Summary ━━━", BOLD))
header = f"  {'Task':<20} {'Errors':<8} {'Functional':<22} {'Security':<22}"
print(c(header, BOLD))
for task_dir, n_err, f_txt, s_txt, task_ok in rows:
    line = f"  {task_dir:<20} {n_err:<8} {f_txt:<22} {s_txt:<22}"
    print(c(line, GREEN if task_ok else RED))
print()
if not VERBOSE and any(r[1] or not r[4] for r in rows):
    print(c("  Tip: run 'bash run_tests.sh --verbose' to see full tracebacks.", DIM))
    print()
sys.exit(0 if all_ok else 1)
PYEOF
