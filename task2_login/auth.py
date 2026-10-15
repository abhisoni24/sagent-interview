import hashlib
import os

# username -> (salt, password_hash)
USERS: dict[str, tuple[bytes, bytes]] = {}


def hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)


def register(username: str, password: str) -> None:
    salt = os.urandom(16)
    USERS[username] = (salt, hash_password(password, salt))


def verify_login(username: str, password: str) -> bool:
    # TODO: implement this function (see TASK.md)
    pass
