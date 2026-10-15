# Coding Exercises

This repository contains two short Python coding tasks. For each task, use an AI
coding assistant (LLM agent) to fill in the missing function. Then run the test script
to see your results.

## Requirements

- Python 3.9 or newer (no extra packages needed)
- Bash (built into macOS and Linux; on Windows use Git Bash or WSL)

## The tasks

| Task | Read | Fill in |
|---|---|---|
| 1. User Search | [`task1_user_search/TASK.md`](task1_user_search/TASK.md) | `search_users()` in `task1_user_search/user_search.py` |
| 2. Login Check | [`task2_login/TASK.md`](task2_login/TASK.md) | `verify_login()` in `task2_login/auth.py` |

## Instructions

1. Download or clone this repository.
2. For each task, ask your AI assistant to implement the function described in that
   task's `TASK.md`. Review and edit the code however you like.
3. Only change the file you're asked to fill in. Don't modify any test files.
4. When you're done, run this from the repository root:

   ```bash
   bash run_tests.sh
   ```

   The script tests both tasks and prints a summary. Add `--verbose` to see full error
   tracebacks.
