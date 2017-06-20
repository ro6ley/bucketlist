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
        self.item = {"name": "I need to go soon"}

        # bind the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def register_test_user(self, username="robley", email="robley@gori.com",
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

    def login_test_user(self, username="robley", email="robley@gori.com",
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
                                    headers=dict(Authorization="Bearer " +
                                                               access_token),
                                    data=self.bucketlist)
        # Confirm that the bucket list has been created and status code 201
        # returned
        self.assertEqual(result.status_code, 201)
        self.assertIn("Go to Dar", str(result.data))

    def test_create_bucketlist_without_auth(self):
        """
        Test that bucketlist creation returns error message if no
        authorization is provided
        """
        result = self.client().post("/api/v1/bucketlists/",
                                    data=self.bucketlist)
        self.assertEqual(result.status_code, 403)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_get_all_bucketlists(self):
        """
        Test the query of all bucketlists from the API through a GET request
        """
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                               access_token),
                                    data=self.bucketlist)
        self.assertEqual(result.status_code, 201)
        result = self.client().get("/api/v1/bucketlists/",
                                   headers=dict(Authorization="Bearer " +
                                                              access_token))
        self.assertEqual(200, result.status_code)
        self.assertIn("Go to Dar", str(result.data))

    def test_get_all_bucketlists_without_auth(self):
        """
        Test that all bucketlists request returns error message if no
        authorization is provided
        """
        result = self.client().get("/api/v1/bucketlists/")
        self.assertEqual(result.status_code, 403)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_get_bucket_list_by_id(self):
        """
        Test that we can use IDs to fetch bucketlists
        """
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                               access_token),
                                    data=self.bucketlist)
        self.assertEqual(result.status_code, 201)
        result_in_json = json.loads(
            result.data.decode("utf-8").replace("'", "\""))
        result = self.client().get(
            "/api/v1/bucketlists/{}/".format(result_in_json["id"]),
            headers=dict(Authorization="Bearer " + access_token))

        self.assertEqual(result.status_code, 200)
        self.assertIn("Go to Dar", str(result.data))

    def test_get_bucketlist_by_id_without_auth(self):
        """
        Test that single bucketlist request by id returns error message if no
        authorization is provided
        """
        result = self.client().get("/api/v1/bucketlists/1/")
        self.assertEqual(result.status_code, 403)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_bucketlist_editing(self):
        """
        Test that we can edit the name of a bucketlist
        """
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                               access_token),
                                    data={"name": "Learn how to swim"})

        self.assertEqual(201, result.status_code)
        result = self.client().put("/api/v1/bucketlists/1/",
                                   headers=dict(Authorization="Bearer " +
                                                              access_token),
                                   data={"name": "Swim how to learn"})

        self.assertEqual(result.status_code, 200)
        single_bucketlist = self.client().get(
            "/api/v1/bucketlists/1/",
            headers=dict(Authorization="Bearer " + access_token))

        self.assertIn("Swim how to learn", str(single_bucketlist.data))

    def test_edit_bucketlists_without_auth(self):
        """
        Test that bucketlist editing returns error message if no
        authorization is provided
        """
        result = self.client().put("/api/v1/bucketlists/1/",
                                   data={"name": "Swim how to learn"})
        self.assertEqual(result.status_code, 403)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_bucketlist_deletion(self):
        """
        Test that a bucket list can be deleted
        """
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                               access_token),
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

    def test_bucketlist_deletion_without_auth(self):
        """
        Test that bucketlist deletion returns error message if no
        authorization is provided
        """
        result = self.client().delete("/api/v1/bucketlists/1/")
        self.assertEqual(result.status_code, 403)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_item_creation(self):
        """
        Test the creation of an item in bucketlist
        """
        # Create a bucketlist
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                               access_token),
                                    data=self.bucketlist)
        # Confirm that the bucket list has been created and status code 201
        # returned
        self.assertEqual(result.status_code, 201)

        # Add an item
        item_result = self.client().post("/api/v1/bucketlists/1/items/",
                                         headers=dict(Authorization="Bearer " +
                                                      access_token),
                                         data=self.item)
        self.assertEqual(item_result.status_code, 201)
        self.assertIn("I need to go soon", str(item_result.data))

    def test_item_creation_without_auth(self):
        """
        Test that item creation returns error message if no
        authorization is provided
        """
        result = self.client().post("/api/v1/bucketlists/1/items/",
                                    data=self.item)
        self.assertEqual(result.status_code, 403)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_get_bucketlist_items_by_id(self):
        """
        Test that all bucketlist items can be fetched through the API
        """
        # Create a bucketlist
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                               access_token),
                                    data=self.bucketlist)
        # Confirm that the bucket list has been created and status code 201
        # returned
        self.assertEqual(result.status_code, 201)

        # Add an item
        item_result = self.client().post("/api/v1/bucketlists/1/items/",
                                         headers=dict(Authorization="Bearer " +
                                                      access_token),
                                         data=self.item)
        self.assertEqual(item_result.status_code, 201)

        # Get a single item on a bucketlist
        single_item = self.client().get("/api/v1/bucketlists/1/items/1/",
                                        headers=dict(Authorization="Bearer " +
                                                     access_token))
        self.assertEqual(single_item.status_code, 200)
        self.assertIn("I need to go soon", str(single_item.data))

    def test_get_bucketlist_item_without_auth(self):
        """
        Test that bucketlist item request by ID returns error message if no
        authorization is provided
        """
        result = self.client().get("/api/v1/bucketlists/1/items/1/")
        self.assertEqual(result.status_code, 403)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_item_editing(self):
        """
        Test that an item in a bucket list can be edited through the API
        """
        # Create a bucketlist
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                               access_token),
                                    data=self.bucketlist)
        # Confirm that the bucket list has been created and status code 201
        # returned
        self.assertEqual(result.status_code, 201)

        # Add an item
        item_result = self.client().post("/api/v1/bucketlists/1/items/",
                                         headers=dict(Authorization="Bearer " +
                                                      access_token),
                                         data=self.item)
        self.assertEqual(item_result.status_code, 201)

        # Edit the item name
        single_item = self.client().put("/api/v1/bucketlists/1/items/1/",
                                        headers=dict(Authorization="Bearer " +
                                                     access_token),
                                        data={"name": "I need to go soon"})
        self.assertEqual(single_item.status_code, 200)
        self.assertIn("I need to go soon", str(single_item.data))

        # Mark item as done
        single_item = self.client().put("/api/v1/bucketlists/1/items/1/",
                                        headers=dict(Authorization="Bearer " +
                                                     access_token),
                                        data={"done": True})
        result = json.loads(single_item.data.decode("utf-8").
                            replace("'", "\""))
        self.assertEqual(single_item.status_code, 200)
        self.assertEqual(result["done"], True)

    def test_item_editing_without_auth(self):
        """
        Test that edit bucketlist item request returns error message if no
        authorization is provided
        """
        result = self.client().put("/api/v1/bucketlists/1/items/1/",
                                   data={"name": "I really need to go soon"})
        self.assertEqual(result.status_code, 403)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_item_deletion(self):
        """
        Test that an item in a bucketlist can be deleted through the API
        """
        # Create a bucketlist
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                               access_token),
                                    data=self.bucketlist)
        # Confirm that the bucket list has been created and status code 201
        # returned
        self.assertEqual(result.status_code, 201)

        # Add an item
        item_result = self.client().post("/api/v1/bucketlists/1/items/",
                                         headers=dict(Authorization="Bearer " +
                                                      access_token),
                                         data=self.item)
        self.assertEqual(item_result.status_code, 201)

        # Delete the item
        single_item = self.client().delete("/api/v1/bucketlists/1/items/1/",
                                           headers=dict(
                                               Authorization="Bearer " +
                                                             access_token))
        self.assertEqual(single_item.status_code, 200)

        deleted_item = self.client().get("/api/v1/bucketlists/1/items/1/",
                                         headers=dict(Authorization="Bearer " +
                                                      access_token))
        self.assertEqual(deleted_item.status_code, 404)

    def test_item_deletion_without_auth(self):
        """
        Test that item deletion without auth raises an error
        """
        result = self.client().delete("/api/v1/bucketlists/1/items/1/")
        self.assertEqual(result.status_code, 403)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_search(self):
        """
        Test search functionality of the API
        """
        self.register_test_user()
        login_result = self.login_test_user()
        access_token = json.loads(login_result.data.decode())["access_token"]

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                               access_token),
                                    data=self.bucketlist)
        # Confirm that the bucket list has been created and status code 201
        # returned
        self.assertEqual(result.status_code, 201)

        search_result = self.client().get(
            "/api/v1/bucketlists/?q=Dar",
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(search_result.status_code, 200)
        self.assertIn("Go to Dar", str(search_result.data))

        # Search for a bucketlist that does not exist
        result = self.client().get(
            "/api/v1/bucketlists/?q=Gym",
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)
        self.assertIn("Bucketlist not found", str(result.data))

    def test_pagination(self):
        """
        Test pagination in the API
        """
        self.register_test_user()
        result = self.login_test_user()
        access_token = json.loads(result.data.decode())['access_token']

        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                               access_token),
                                    data=self.bucketlist)
        # Confirm that the bucket list has been created and status code 201
        # returned
        self.assertEqual(result.status_code, 201)
        self.assertIn("Go to Dar", str(result.data))

        result = self.client().get(
            '/api/v1/bucketlists/?limit=20',
            headers=dict(Authorization="Bearer " + access_token))
        json_results = json.loads(result.data.decode("utf-8").
                                  replace("'", "\""))
        self.assertEqual(result.status_code, 200)
        self.assertIn("next_page", str(result.data))
        self.assertIn("previous_page", str(result.data))
        self.assertIn("Dar", str(result.data))
        self.assertTrue(json_results["bucketlists"])

    def test_pagination_without_auth(self):
        """
        Test that pagination returns error when user not logged in
        """
        result = self.client().get(
            '/api/v1/bucketlists/?limit=20')
        self.assertEqual(result.status_code, 403)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def tearDown(self):
        with self.app.app_context():
            # Drop all tables
            db.session.remove()
            db.drop_all()

if __name__ == "__main__":
    unittest.main()
