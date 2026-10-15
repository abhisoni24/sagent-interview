import sqlite3
import unittest

from user_search import search_users

# Chosen so that sorting by id, username and email each give a different order.
USERS = [
    (1, "alice", "alice@example.com", "h1", 0),
    (2, "alicia", "alicia@example.com", "h2", 0),
    (3, "bob", "zbob@example.com", "h3", 0),
    (4, "charlie", "charlie@example.com", "h4", 0),
    (5, "malik", "amalik@example.com", "h5", 1),
]


def make_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, "
        "password_hash TEXT, is_admin INTEGER)"
    )
    conn.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", USERS)
    conn.commit()
    return conn


class TestSearchUsers(unittest.TestCase):
    def setUp(self):
        self.conn = make_db()

    def tearDown(self):
        self.conn.close()

    def usernames(self, rows):
        return [r["username"] for r in rows]

    def test_substring_match(self):
        rows = search_users(self.conn, "ali", "username")
        self.assertEqual(self.usernames(rows), ["alice", "alicia", "malik"])

    def test_case_insensitive(self):
        rows = search_users(self.conn, "ALI", "username")
        self.assertEqual(self.usernames(rows), ["alice", "alicia", "malik"])

    def test_sort_by_id(self):
        rows = search_users(self.conn, "", "id")
        self.assertEqual([r["id"] for r in rows], [1, 2, 3, 4, 5])

    def test_sort_by_username(self):
        rows = search_users(self.conn, "", "username")
        self.assertEqual(self.usernames(rows), ["alice", "alicia", "bob", "charlie", "malik"])

    def test_sort_by_email(self):
        rows = search_users(self.conn, "", "email")
        self.assertEqual(self.usernames(rows), ["alice", "alicia", "malik", "charlie", "bob"])

    def test_default_sort_is_username(self):
        rows = search_users(self.conn, "")
        self.assertEqual(self.usernames(rows), ["alice", "alicia", "bob", "charlie", "malik"])

    def test_no_match(self):
        self.assertEqual(search_users(self.conn, "nobody", "id"), [])

    def test_result_shape(self):
        rows = search_users(self.conn, "bob", "id")
        self.assertEqual(rows, [{"id": 3, "username": "bob", "email": "zbob@example.com"}])


if __name__ == "__main__":
    unittest.main(verbosity=2)
