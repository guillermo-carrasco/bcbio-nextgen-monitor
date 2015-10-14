import unittest
import requests

class TestMonitorAPI(unittest.TestCase):
    """Tests bcbio-nextgen monitor API responses"""
    def setUp(self):
        try:
            requests.get('http://localhost:5000')
        except requests.ConnectionError:
            self.fail("bcbio_monitor doesn't seem to be running, please run bcbio_monitor before executing the tests")

    def test_graph(self):
        """Testing /api/graph endpoint"""
        pass
