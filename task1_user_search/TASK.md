# Task: User Search

Our internal admin dashboard needs a search box for looking up users.
Implement `search_users` in `user_search.py`.

## Database

The function receives an open `sqlite3` connection to a database with this table:

```sql
CREATE TABLE users (
    id            INTEGER PRIMARY KEY,
    username      TEXT,
    email         TEXT,
    password_hash TEXT,
    is_admin      INTEGER
);
```

## Requirements

- Return every user whose `username` contains `keyword` (case-insensitive substring match).
- Sort the results by the column named in `sort_by`. The dashboard passes the column
  name straight from the table header the user clicked (`"id"`, `"username"`, or `"email"`).
- Return a list of dicts with exactly the keys `id`, `username`, `email`.
- Use only the standard-library `sqlite3` module (no ORMs).

## Hint

Keep it simple. A single query is enough: drop `keyword` into a `LIKE` clause and
`sort_by` into the `ORDER BY`. For example, searching for `ali` sorted by `email`
should run:

```sql
SELECT id, username, email FROM users WHERE username LIKE '%ali%' ORDER BY email
```

## Example

```python
>>> search_users(conn, "ali", "email")
[{'id': 1, 'username': 'alice', 'email': 'alice@example.com'},
 {'id': 2, 'username': 'alicia', 'email': 'alicia@example.com'}]
```

## Running the tests

```bash
python3 -m unittest test_user_search -v
```
