import os
import json
import unittest

from app.app import create_app, db


class BucketlistTestcase(unittest.TestCase):
    """
    Test cases for the bucketlist
    """

    def setUp(self):
        self.app = create_app("testing")
        # set up the test client
        self.client = self.app.test_client
        self.bucketlist = {"name": "Go to Dar"}

        # bind the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def register_test_user(self, username="roble", email="robley@gori.com",
                           password="test_password"):
        """
        Register a test user
        """
        user_data = {
            "username": username,
            "email": email,
            "password": password
        }
        return self.client().post("/auth/register/", data=user_data)

    def login_test_user(self, username="roble", email="robley@gori.com",
                        password="test_password"):
        """
        Log in as the test user
        """
        user_data = {
            "username": username,
            "email": email,
            "password": password
        }
        return self.client().post("/auth/login/", data=user_data)

    def test_bucketlist_creation(self):
        """
        Test the creation of a bucketlist through the API via POST
        """
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer "+access_token),
                                    data=self.bucketlist)
        # Confirm that the bucket list has been created and status code 201
        # returned
        self.assertEqual(result.status_code, 201)
        self.assertIn("Go to Dar", str(result.data))

    def test_get_all_bucketlists(self):
        """
        Test the query of all bucketlists from the API through a GET request
        """
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " + access_token),
                                    data=self.bucketlist)
        self.assertEqual(result.status_code, 201)
        result = self.client().get("/api/v1/bucketlists/",
                                   headers=dict(Authorization="Bearer "+access_token))
        self.assertEqual(200, result.status_code)
        self.assertIn("Go to Dar", str(result.data))

    def test_get_bucket_list_by_id(self):
        """
        Test that we can use IDs to fetch bucketlists
        """
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(
                                        Authorization="Bearer " + access_token),
                                    data=self.bucketlist)
        self.assertEqual(result.status_code, 201)
        result_in_json = json.loads(
            result.data.decode("utf-8").replace("'", "\""))
        result = self.client().get(
            "/api/v1/bucketlists/{}/".format(result_in_json["id"]),
            headers=dict(Authorization="Bearer " + access_token))

        self.assertEqual(result.status_code, 200)
        self.assertIn("Go to Dar", str(result.data))

    def test_bucketlist_editing(self):
        """
        Test that we can edit the name of a bucketlist
        """
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(
                                        Authorization="Bearer " + access_token),
                                    data={"name": "Learn how to swim"})

        self.assertEqual(201, result.status_code)
        result = self.client().put("/api/v1/bucketlists/1/",
                                   headers=dict(
                                       Authorization="Bearer " + access_token),
                                   data={"name": "Swim how to learn"})

        self.assertEqual(result.status_code, 200)
        single_bucketlist = self.client().get(
            "/api/v1/bucketlists/1/",
            headers=dict(Authorization="Bearer " + access_token))

        self.assertIn("Swim how to learn", str(single_bucketlist.data))

    def test_bucketlist_deletion(self):
        """
        Test that a bucket list can be deleted
        """
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(
                                        Authorization="Bearer " + access_token),
                                    data={"name": "Go to sleep"})
        self.assertEqual(result.status_code, 201)
        delete_result = self.client().delete(
            "/api/v1/bucketlists/1/",
            headers=dict(Authorization="Bearer " + access_token))

        self.assertEqual(delete_result.status_code, 200)

        # Confirm that the bucketlist has been deleted
        result = self.client().get("/api/v1/bucketlists/1/",
                                   headers=dict(
                                       Authorization="Bearer " + access_token)
                                   )
        self.assertEqual(result.status_code, 404)

    def test_item_creation(self):
        """
        Test the creation of an item in bucketlist
        """
        pass

    def test_get_bucketlist_items(self):
        """
        Test that all bucketlist items can be fetched through the API
        """
        # Test get multiple items
        # Test get a single item
        pass

    def test_item_editing(self):
        """
        Test that an item in a bucket list can be edited through the API
        """
        pass

    def test_item_deletion(self):
        """
        Test that an item in a bucketlist can be deleted through the API
        """
        pass

    def test_search(self):
        """
        Test search function
        :return:
        """
        pass

    def test_pagination(self):
        """
        Test pagination in the API
        :return:
        """
        pass

    def tearDown(self):
        with self.app.app_context():
            # Drop all tables
            db.session.remove()
            db.drop_all()

if __name__ == "__main__":
    unittest.main()
