# import unittest
# from pymongo import MongoClient
# # from your_app import create_app
# # import plotly.graph_objs as go
#
# class TestFlaskRoutes(unittest.TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         cls.client = MongoClient('mongodb://localhost:27017')
#         cls.db = cls.client.test_database
#         # Insert some test data into the database
#         cls.db.timeseries.insert_one({
#             'date': '2022-02-15',
#             'value': 10
#         })
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.client.drop_database(cls.db.name)
#
#     def setUp(self):
#         # app = create_app({'TESTING': True, 'MONGO_URI': 'mongodb://localhost:27017/test_database'})
#         # self.client = app.test_client()
#
#     def test_plot_route(self):
#         response = self.client.get('/plot')
#         self.assertEqual(response.status_code, 200)
#         # Verify that the response contains a Plotly figure
#         # plot = go.Figure(data=go.Scatter(x=[0], y=[0]))
#         # plot.update_layout(title_text='Test plot')
#         # self.assertEqual(response.json, plot.to_json())
# #
# # if __name__ == '__main__':
# #     unittest.main()