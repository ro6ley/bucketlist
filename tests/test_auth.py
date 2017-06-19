import unittest
import json
from app.app import create_app, db


class AuthTestCases(unittest.TestCase):
    """
    Tests for the authentication blueprint
    """
    def setUp(self):
        self.app = create_app(config_name="testing")
        # Set up the test client
        self.client = self.app.test_client
        self.user_data = {
            "username": "robley",
            "email": "robley.gori@andela.com",
            "password": "test_password"
        }

        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_registration(self):
        """
        Test that a new user can be registered
        """
        result = self.client().post("/auth/register/", data=self.user_data)
        results = json.loads(result.data.decode())

        self.assertEqual(results["message"],
                         "You registered successfully. Log in.")
        self.assertEqual(result.status_code, 201)

    def test_double_registration(self):
        """
        Test that a user cannot be registered twice
        """
        result = self.client().post("/auth/register/", data=self.user_data)
        self.assertEqual(result.status_code, 201)

        # Test double registration
        second_result = self.client().post("/auth/register/",
                                           data=self.user_data)
        self.assertEqual(second_result.status_code, 202)
        final_result = json.loads(second_result.data.decode())
        self.assertEqual(final_result["message"],
                         "User already exists. Please login")

    def test_login(self):
        """
        Test that a user can login successfully
        """
        result = self.client().post("/auth/register/", data=self.user_data)
        self.assertEqual(result.status_code, 201)

        login_result = self.client().post("/auth/login/", data=self.user_data)
        results = json.loads(login_result.data.decode())

        # Confirm the success message
        self.assertEqual(results["message"], "You logged in successfully.")
        # Confirm the status code and access token
        self.assertEqual(login_result.status_code, 200)
        self.assertTrue(results["access_token"])

    def test_login_non_registered_user(self):
        """
        Test that non registered users cannot log in
        """
        non_user = {
            "username": "nonuser",
            "email": "nonuser@email.com",
            "password": "invalidpassword"
        }

        result = self.client().post("/auth/login/", data=non_user)
        final_result = json.loads(result.data.decode())

        self.assertEqual(result.status_code, 401)
        self.assertEqual(final_result["message"],
                         "Invalid email or password. Please try again.")

if __name__ == "__main__":
    unittest.main()
