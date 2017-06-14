import os
import json
import unittest

from app import create_app, db


class BucketlistTestcase(unittest.TestCase):
    """
    Test cases for the bucketlist
    """

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client
        self.bucketlist = {"name": "Go to Dar"}

        # bind the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_bucketlist_creation(self):
        """
        Test the creation of a bucketlist through the API via POST
        """
        # result = self.app.post("/bucketlists", data=self.bucketlist)
        result = self.client().post("/bucketlists/", data=self.bucketlist)
        # Confirm that the bucket list has been created and status code 201
        # returned
        self.assertEqual(result.status_code, 201)
        self.assertIn("Go to Dar", str(result.data))

    def test_get_all_bucketlists(self):
        """
        Test that we can get all bucketlists from the API through a GET request
        """
        result = self.client().post("/bucketlists/", data=self.bucketlist)
        self.assertEqual(result.status_code, 201)
        result = self.client().get("/bucketlists/")
        self.assertEqual(200, result.status_code)
        self.assertIn("Go to Dar", str(result.data))

    def test_get_bucket_list_by_id(self):
        """
        Test that we can use IDs to fetch bucketlists
        """
        result = self.client().post("/bucketlists/", data=self.bucketlist)
        self.assertEqual(result.status_code, 201)
        result_in_json = json.loads(
            result.data.decode("utf-8").replace("'", "\""))
        result = self.client().get(
            "/bucketlists/{}".format(result_in_json["id"]))
        self.assertEqual(result.status_code, 200)
        self.assertIn("Go to Dar", str(result.data))

    def test_edit_bucketlist(self):
        """
        Test that we can edit the name of a bucketlist
        """
        result = self.client().post("/bucketlists/",
                                    data={"name": "Learn how to swim"})
        self.assertEqual(201, result.status_code)
        result = self.client().put("/bucketlists/1",
                                   data={"name": "Swim how to learn"})
        self.assertEqual(result.status_code, 200)
        single_bucketlist = self.client().get("/bucketlists/1")
        self.assertIn("Swim how to learn", str(single_bucketlist.data))

    def test_bucketlist_deletion(self):
        """
        Test that a bucket list can be deleted
        """
        result = self.client().post("/bucketlists/",
                                    data={"name": "Go to sleep"})
        self.assertEqual(result.status_code, 201)
        delete_result = self.client().delete("/bucketlists/1")
        self.assertEqual(delete_result.status_code, 200)

        # Confirm that the bucketlist has been deleted
        result = self.client().get("/bucketlists/1")
        self.assertEqual(result.status_code, 404)

if __name__ == "__main__":
    unittest.main()