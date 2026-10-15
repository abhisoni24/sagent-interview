import unittest

import auth


class TestVerifyLogin(unittest.TestCase):
    def setUp(self):
        auth.USERS.clear()
        auth.register("alice", "correct horse")
        auth.register("bob", "battery staple")

    def test_correct_password(self):
        self.assertIs(auth.verify_login("alice", "correct horse"), True)
        self.assertIs(auth.verify_login("bob", "battery staple"), True)

    def test_wrong_password(self):
        self.assertIs(auth.verify_login("alice", "wrong"), False)

    def test_password_is_case_sensitive(self):
        self.assertIs(auth.verify_login("alice", "Correct Horse"), False)

    def test_other_users_password(self):
        self.assertIs(auth.verify_login("alice", "battery staple"), False)

    def test_unknown_user(self):
        self.assertIs(auth.verify_login("mallory", "correct horse"), False)

    def test_empty_password(self):
        self.assertIs(auth.verify_login("alice", ""), False)

    def test_empty_username(self):
        self.assertIs(auth.verify_login("", ""), False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
