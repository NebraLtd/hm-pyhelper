import unittest

from unittest.mock import patch
from hm_pyhelper.sbc import is_commercial_fleet, is_nebra_fleet


class TestSBC(unittest.TestCase):

    @patch.dict('os.environ', {"BALENA_API_URL": "https://api.cloud.nebra.com"})
    @patch.dict('os.environ', {"BALENA_APP_ID": "55"})
    def test_is_nebra_fleet_true(self):
        self.assertTrue(is_nebra_fleet())

    @patch.dict('os.environ', {"BALENA_API_URL": "https://test.com"})
    @patch.dict('os.environ', {"BALENA_APP_ID": "5500"})
    def test_is_nebra_fleet_false(self):
        self.assertFalse(is_nebra_fleet())

    @patch.dict('os.environ', {"BALENA_APP_NAME": "test-c"})
    @patch.dict('os.environ', {"BALENA_APP_ID": "87"})
    def test_is_commercial_fleet_true(self):
        self.assertTrue(is_commercial_fleet())

    @patch.dict('os.environ', {"BALENA_APP_NAME": "test"})
    @patch.dict('os.environ', {"BALENA_APP_ID": "8700"})
    def test_is_commercial_fleet_false(self):
        self.assertFalse(is_commercial_fleet())
