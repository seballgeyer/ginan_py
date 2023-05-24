"""
Testing set for mongo connections
"""
import unittest

from pymongo import MongoClient


import sateda.dbconnector.mongo as dbmongo


class TestMongo(unittest.TestCase):
    """
    Test class for mongo
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self.data_base = None
        self.collection_content = None

    @classmethod
    def setUpClass(cls) -> None:
        """
        Setting up the test database
        :return:
        """
        # Replace with your MongoDB connection string
        conn_str = "mongodb://localhost:27017/"
        # Connect to the MongoDB server
        cls.client = MongoClient(conn_str)
        cls.data_base = cls.client.test_database
        cls.collection_content = cls.data_base.Content
        # Insert test data into the collection
        cls.collection_content.insert_one(
            {"type": "Measurements", "Values": ["L120", "L125", "P120", "P125", "0", "120", "125"]}
        )

        cls.connector = dbmongo.MongoDB("127.0.0.1", "test_database")
        cls.connector.connect()
        cls.connector.get_content()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Destroying the test database
        :return:
        """
        cls.collection_content.delete_many({})
        cls.client.drop_database(cls.data_base.name)
        cls.client.close()

    def test_content(self) -> None:
        """
        Checking if the database content contains information
        """
        self.assertEqual(len(self.connector.mongo_content["Measurements"]), 7)
        self.assertTrue("L125" in self.connector.mongo_content["Measurements"], "Didn't find L125 in the test dataset")

    def test_connection_error(self) -> None:
        """
        Check if a connection error is raised correctly
        """
        connector = dbmongo.MongoDB("dummy.host", "test")
        with self.assertRaises(ConnectionError):
            connector.connect()

if __name__ == "__main__":
    unittest.main()
