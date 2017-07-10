import json
import unittest

from app.app import create_app, db


class BucketlistTestCases(unittest.TestCase):
    """
    Test cases for the bucketlist
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

        content_type = 'application/json'

        # Register a test user
        self.user_data = json.dumps(dict({
            "username": "robley",
            "email": "robley@gori.com",
            "password": "test_password"
                }))
        self.client().post("/auth/register/", data=self.user_data,
                           content_type="application/json")

        self.login_data = json.dumps(dict({
            "username": "robley",
            "password": "test_password"
        }))
        # Log is as the test user and get a token
        self.login_result = self.client().post("/auth/login/",
                                               data=self.login_data,
                                               content_type="application/json")
        self.access_token = json.loads(
            self.login_result.data.decode())['access_token']

    def test_bucketlist_creation(self):
        """
        Test the creation of a bucketlist through the API via POST
        """
        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                 self.access_token),
                                    data=self.bucketlist,
                                    content_type="application/json")
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
                                    data=self.bucketlist,
                                    content_type="application/json")
        self.assertEqual(result.status_code, 401)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_get_all_bucketlists(self):
        """
        Test the query of all bucketlists from the API through a GET request
        """
        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                 self.access_token),
                                    data=self.bucketlist,
                                    content_type="application/json")
        self.assertEqual(result.status_code, 201)
        result = self.client().get("/api/v1/bucketlists/",
                                   headers=dict(Authorization="Bearer " +
                                                self.access_token))
        self.assertEqual(200, result.status_code)
        self.assertIn("Go to Dar", str(result.data))

    def test_get_all_bucketlists_without_auth(self):
        """
        Test that all bucketlists request returns error message if no
        authorization is provided
        """
        result = self.client().get("/api/v1/bucketlists/")
        self.assertEqual(result.status_code, 401)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_get_bucket_list_by_id(self):
        """
        Test that we can use IDs to fetch bucketlists
        """
        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                 self.access_token),
                                    data=self.bucketlist,
                                    content_type="application/json")
        self.assertEqual(result.status_code, 201)
        result_in_json = json.loads(
            result.data.decode("utf-8").replace("'", "\""))
        result = self.client().get(
            "/api/v1/bucketlists/{}/".format(result_in_json["id"]),
            headers=dict(Authorization="Bearer " + self.access_token))

        self.assertEqual(result.status_code, 200)
        self.assertIn("Go to Dar", str(result.data))

    def test_get_bucketlist_by_id_without_auth(self):
        """
        Test that single bucketlist request by id returns error message if no
        authorization is provided
        """
        result = self.client().get("/api/v1/bucketlists/1/")
        self.assertEqual(result.status_code, 401)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_bucketlist_editing(self):
        """
        Test that we can edit the name of a bucketlist
        """
        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                 self.access_token),
                                    data={"name": "Learn how to swim"})

        self.assertEqual(201, result.status_code)
        result = self.client().put("/api/v1/bucketlists/1/",
                                   headers=dict(Authorization="Bearer " +
                                                self.access_token),
                                   data={"name": "Swim how to learn"})

        self.assertEqual(result.status_code, 201)

        single_bucketlist = self.client().get(
            "/api/v1/bucketlists/1/",
            headers=dict(Authorization="Bearer " + self.access_token))

        self.assertIn("Swim how to learn", str(single_bucketlist.data))

    def test_bucketlist_edit_non_existing(self):
        """
        Test that a user cannot edit a bucket list that does not exist
        """
        result = self.client().put("/api/v1/bucketlists/12/",
                                   headers=dict(Authorization="Bearer " +
                                                self.access_token),
                                   data={"name": "Swim how to learn"})

        self.assertEqual(result.status_code, 404)

    def test_edit_bucketlists_without_auth(self):
        """
        Test that bucketlist editing returns error message if no
        authorization is provided
        """
        new_data = json.dumps({"name": "Swim how to learn"})
        result = self.client().put("/api/v1/bucketlists/1/",
                                   data=new_data)
        self.assertEqual(result.status_code, 401)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_bucketlist_deletion(self):
        """
        Test that a bucket list can be deleted
        """
        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                 self.access_token),
                                    data={"name": "Go to sleep"})
        self.assertEqual(result.status_code, 201)
        delete_result = self.client().delete(
            "/api/v1/bucketlists/1/",
            headers=dict(Authorization="Bearer " + self.access_token))

        self.assertEqual(delete_result.status_code, 204)

        # Confirm that the bucketlist has been deleted
        result = self.client().get("/api/v1/bucketlists/1/",
                                   headers=dict(Authorization="Bearer " +
                                                self.access_token))
        self.assertEqual(result.status_code, 404)

    def test_bucketlist_deletion_without_auth(self):
        """
        Test that bucketlist deletion returns error message if no
        authorization is provided
        """
        result = self.client().delete("/api/v1/bucketlists/1/")
        self.assertEqual(result.status_code, 401)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_buckelist_edit_different_user(self):
        """
        Test that a different user cannot edit another's bucket list
        """
        # Register a new user and login
        user_data = {
            "username": "newuser",
            "email": "new@user.com",
            "password": "test_password"
                }
        self.client().post("/auth/register/", data=user_data)

        login_data = {
            "username": "newuser",
            "password": "test_password"
        }
        # Log is as the test user and get a token
        self.login_result = self.client().post("/auth/login/",
                                               data=login_data)
        access_token = json.loads(
            self.login_result.data.decode())['access_token']

        # Try to edit another user's bucket list
        result = self.client().put("/api/v1/bucketlists/1/",
                                   headers=dict(Authorization="Bearer " +
                                                access_token),
                                   data={"name": "Swim how to learn"})

        # Not found error since each session includes only the
        # current user's bucketlists
        self.assertEqual(result.status_code, 404)

    def test_search(self):
        """
        Test search functionality of the API
        """
        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                 self.access_token),
                                    data=self.bucketlist,
                                    content_type="application/json")
        # Confirm that the bucket list has been created and status code 201
        # returned
        self.assertEqual(result.status_code, 201)

        search_result = self.client().get(
            "/api/v1/bucketlists/?q=Dar",
            headers=dict(Authorization="Bearer " + self.access_token))
        self.assertEqual(search_result.status_code, 200)
        self.assertIn("Go to Dar", str(search_result.data))

    def test_search_non_existent_bucketlist(self):
        """
        Test search for a bucketlist that does not exist
        """
        # Search for a bucketlist that does not exist
        result = self.client().get(
            "/api/v1/bucketlists/?q=Gym",
            headers=dict(Authorization="Bearer " + self.access_token))
        self.assertEqual(result.status_code, 404)
        self.assertIn("Bucketlist not found", str(result.data))

    def test_search_without_auth(self):
        """
        Test that search without login returns an error
        """
        search_result = self.client().get("/api/v1/bucketlists/?q=Dar")
        self.assertEqual(search_result.status_code, 401)
        self.assertIn("Register or log in to access this resource",
                      str(search_result.data))

    def test_pagination(self):
        """
        Test pagination in the API
        """
        result = self.client().post("/api/v1/bucketlists/",
                                    headers=dict(Authorization="Bearer " +
                                                 self.access_token),
                                    data=self.bucketlist,
                                    content_type="application/json")
        # Confirm that the bucket list has been created and status code 201
        # returned
        self.assertEqual(result.status_code, 201)
        self.assertIn("Go to Dar", str(result.data))

        result = self.client().get(
            '/api/v1/bucketlists/?limit=20',
            headers=dict(Authorization="Bearer " + self.access_token))
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
