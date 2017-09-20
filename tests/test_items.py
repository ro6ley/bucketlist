import json
import unittest

from app.app import create_app, db


class ItemsTestCases(unittest.TestCase):
    """
    Test cases for items manipulation
    """
    def setUp(self):
        self.app = create_app("testing")
        # set up the test client
        self.client = self.app.test_client
        self.bucketlist = json.dumps(dict({"name": "Go to Dar"}))
        self.item = json.dumps(dict({"name": "I need to go soon"}))

        # bind the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

        # Register a test user
        self.user_data = json.dumps(dict({
            "username": "robley",
            "email": "robley@gori.com",
            "password": "test_password"
                }))
        self.client().post("/auth/register/", data=self.user_data,
                           content_type="application/json")

        self.login_data =json.dumps(dict({
            "username": "robley",
            "email": "robley@gori.com",
            "password": "test_password"
        }))
        # Log is as the test user and get a token
        self.login_result = self.client().post("/auth/login/",
                                               data=self.login_data,
                                               content_type="application/json")
        self.access_token = json.loads(
            self.login_result.data.decode())['access_token']

        # Create a bucket list
        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                 self.access_token),
                                    data=self.bucketlist,
                                    content_type="application/json")
        # Confirm that the bucket list has been
        self.assertEqual(result.status_code, 201)

        # Add an item
        item_result = self.client().post("/api/v1/bucketlists/1/items/",
                                         headers=dict(Authorization="Bearer " +
                                                      self.access_token),
                                         data=self.item,
                                         content_type="application/json")
        self.assertEqual(item_result.status_code, 201)

    def test_item_creation(self):
        """
        Test the creation of an item in bucketlist
        """
        test_item_data = json.dumps(dict({"name": "I need to soon"}))
        # Add an item
        item_result = self.client().post("/api/v1/bucketlists/1/items/",
                                         headers=dict(Authorization="Bearer " +
                                                      self.access_token),
                                         data=test_item_data,
                                         content_type="application/json")
        self.assertEqual(item_result.status_code, 201)
        self.assertIn("I need to soon", str(item_result.data))

    def test_item_creation_without_auth(self):
        """
        Test that item creation returns error message if no
        authorization is provided
        """
        result = self.client().post("/api/v1/bucketlists/1/items/",
                                    data=self.item)
        self.assertEqual(result.status_code, 401)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_get_bucketlist_items_by_id(self):
        """
        Test that all bucketlist items can be fetched through the API
        """
        test_item_data = json.dumps(dict({"name": "I need"}))
        # Add an item
        item_result = self.client().post("/api/v1/bucketlists/1/items/",
                                         headers=dict(Authorization="Bearer " +
                                                      self.access_token),
                                         data=test_item_data,
                                         content_type="application/json")
        self.assertEqual(item_result.status_code, 201)

        # Get a single item on a bucketlist
        single_item = self.client().get("/api/v1/bucketlists/1/items/2/",
                                        headers=dict(Authorization="Bearer " +
                                                     self.access_token))
        self.assertEqual(single_item.status_code, 200)
        self.assertIn("I need", str(single_item.data))

    def test_get_bucketlist_item_without_auth(self):
        """
        Test that bucketlist item request by ID returns error message if no
        authorization is provided
        """
        result = self.client().get("/api/v1/bucketlists/1/items/1/")
        self.assertEqual(result.status_code, 401)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_item_editing(self):
        """
        Test that an item in a bucket list can be edited through the API
        """
        # Edit the item name
        single_item = self.client().put("/api/v1/bucketlists/1/items/1/",
                                        headers=dict(Authorization="Bearer " +
                                                     self.access_token),
                                        data=json.dumps(dict(
                                            {"name": "I to go soon"})),
                                        content_type="application/json")
        self.assertEqual(single_item.status_code, 201)
        self.assertIn("I to go soon", str(single_item.data))

        # Mark item as done
        single_item = self.client().put("/api/v1/bucketlists/1/items/1/",
                                        headers=dict(Authorization="Bearer " +
                                                     self.access_token),
                                        data=json.dumps(dict({"done": True})),
                                        content_type="application/json")
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
                                   data={"name": "I really need to go soon"},
                                   content_type="application/json")
        self.assertEqual(result.status_code, 401)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_item_deletion(self):
        """
        Test that an item in a bucketlist can be deleted through the API
        """
        # Delete the item
        single_item = self.client().delete(
            "/api/v1/bucketlists/1/items/1/",
            headers=dict(Authorization="Bearer " + self.access_token))
        self.assertEqual(single_item.status_code, 204)

        deleted_item = self.client().get("/api/v1/bucketlists/1/items/1/",
                                         headers=dict(Authorization="Bearer " +
                                                      self.access_token))
        self.assertEqual(deleted_item.status_code, 404)

    def test_item_deletion_without_auth(self):
        """
        Test that item deletion without auth raises an error
        """
        result = self.client().delete("/api/v1/bucketlists/1/items/1/")
        self.assertEqual(result.status_code, 401)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def tearDown(self):
        with self.app.app_context():
            # Drop all tables
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
