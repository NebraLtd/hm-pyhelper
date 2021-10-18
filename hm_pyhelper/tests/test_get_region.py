from hm_pyhelper.miner_param import get_region, REGION_OVERRIDE_KEY
import unittest
from unittest.mock import mock_open, patch
import os


class TestGetRegion(unittest.TestCase):
    def test_get_region_from_override(self):
        os.environ[REGION_OVERRIDE_KEY] = 'foo'
        self.assertEqual(get_region(), 'foo')

    @patch("builtins.open", new_callable=mock_open, read_data="ZZ111\n")
    def test_get_region_from_miner(self, _):
        os.environ[REGION_OVERRIDE_KEY] = ''
        self.assertEqual(get_region(), 'ZZ111')
