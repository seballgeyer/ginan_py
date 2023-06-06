import unittest
from flask import Flask
from flask_testing import TestCase

from api.eda.routes.dbConnection import eda_bp


class RouteTestCase(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True
        app.register_blueprint(eda_bp)
        return app

    def test_valid_route(self):
        response = self.client.get("/eda/")
        self.assertEqual(response.status_code, 200)
        # Add more assertions to validate the response content or behavior

    def test_invalid_route(self):
        response = self.client.get("/eda/nonexistent")
        self.assertEqual(response.status_code, 404)
        # Add more assertions to validate the response content or behavior

    def test_404_error_handling(self):
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)
        # Add more assertions to validate the response content or behavior


if __name__ == "__main__":
    unittest.main()
