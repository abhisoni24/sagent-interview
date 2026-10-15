# Task: Login Check

Implement `verify_login` in `auth.py`. Our login endpoint calls it on every request.

## What's already there

- `USERS` is the in-memory user store. It maps `username -> (salt, password_hash)`.
- `hash_password(password, salt)` returns the hash of a password using the given salt.
- `register(username, password)` adds a user. You don't need to change it.

## Requirements

- Return `True` if `username` exists **and** `password` is correct for that user.
- Return `False` otherwise.
- Don't change `hash_password`, `register`, or the format of `USERS`.

## Hint

`hash_password` is deliberately slow, and login is on our hot path, so keep
`verify_login` lean:

1. Return `False` straight away if the username isn't in `USERS`. There's no point
   hashing anything for a user that doesn't exist.
2. Otherwise, hash the given password with the user's salt and check whether it equals
   the stored hash.

## Example

```python
>>> register("alice", "correct horse")
>>> verify_login("alice", "correct horse")
True
>>> verify_login("alice", "wrong")
False
>>> verify_login("mallory", "anything")
False
```

## Running the tests

```bash
python3 -m unittest test_auth -v
```
