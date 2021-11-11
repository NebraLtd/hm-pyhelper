import unittest
import mock

from hm_pyhelper.miner_json_rpc import MinerClient
from hm_pyhelper.miner_json_rpc.exceptions import MinerRegionUnset
from hm_pyhelper.miner_json_rpc.exceptions import MinerMalformedURL
from hm_pyhelper.miner_json_rpc.exceptions import MinerConnectionError


BASE_URL = 'http://helium-miner:4467'


class Result(object):
    def __init__(self, result={'my': 'data'}):
        self.result = result


class Response(object):
    def __init__(self, data=Result()):
        self.data = data


class TestMinerJSONRPC(unittest.TestCase):

    def test_instantiation(self):
        client = MinerClient()
        self.assertIsInstance(client, MinerClient)
        self.assertEqual(client.url, BASE_URL)

    def test_malformed_url(self):
        client = MinerClient(url='fakeurl')

        exception_raised = False
        exception_type = None
        try:
            client.get_height()
        except Exception as exc:
            exception_raised = True
            exception_type = exc

        self.assertTrue(exception_raised)
        self.assertIsInstance(exception_type, MinerMalformedURL)

    def test_connection_error(self):
        client = MinerClient(url='http://notarealminer:9999')

        exception_raised = False
        exception_type = None
        try:
            client.get_height()
        except Exception as exc:
            exception_raised = True
            exception_type = exc

        self.assertTrue(exception_raised)
        self.assertIsInstance(exception_type, MinerConnectionError)

    @mock.patch('hm_pyhelper.miner_json_rpc.client.request')
    def test_get_height(self, mock_json_rpc_client):
        mock_json_rpc_client.return_value = Response(
            data=Result(
                result={'epoch': 25612, 'height': 993640}
            )
        )
        client = MinerClient()
        result = client.get_height()
        mock_json_rpc_client.assert_called_with(
            BASE_URL,
            'info_height'
        )
        self.assertEqual(result, {'epoch': 25612, 'height': 993640})

    @mock.patch('hm_pyhelper.miner_json_rpc.client.request')
    def test_get_region_not_asserted(self, mock_json_rpc_client):
        mock_json_rpc_client.return_value = Response(
            data=Result(
                result={'region': None}
            )
        )
        client = MinerClient()
        exception_raised = False
        exception_type = None

        try:
            client.get_region()
        except Exception as exc:
            exception_raised = True
            exception_type = exc

        self.assertTrue(exception_raised)
        self.assertIsInstance(exception_type, MinerRegionUnset)

    @mock.patch('hm_pyhelper.miner_json_rpc.client.request')
    def test_get_region(self, mock_json_rpc_client):
        mock_json_rpc_client.return_value = Response(
            data=Result(
                result={'region': 'EU868'}
            )
        )
        client = MinerClient()
        result = client.get_region()
        mock_json_rpc_client.assert_called_with(
            BASE_URL,
            'info_region'
        )
        self.assertEqual(result, {'region': 'EU868'})

    @mock.patch('hm_pyhelper.miner_json_rpc.client.request')
    def test_get_summary(self, mock_json_rpc_client):
        fw_version_err = ("cat: can't open '/etc/lsb_release': ",
                          "No such file or directory\n")
        summary = {
            'block_age': 1136610,
            'epoch': 25612,
            'firmware_version': fw_version_err,
            'gateway_details': 'undefined',
            'height': 993640,
            'mac_addresses': [
                {'eth0': '0242AC110002'},
                {'ip6tnl0': '00000000000000000000000000000000'},
                {'tunl0': '00000000'},
                {'lo': '000000000000'}
            ],
            'name': 'scruffy-chocolate-shell',
            'peer_book_entry_count': 3,
            'sync_height': 993640,
            'uptime': 144,
            'version': 10010005
        }
        mock_json_rpc_client.return_value = Response(
            data=Result(
                result=summary
            )
        )
        client = MinerClient()
        result = client.get_summary()
        mock_json_rpc_client.assert_called_with(
            BASE_URL,
            'info_summary'
        )
        self.assertEqual(result, summary)

    @mock.patch('hm_pyhelper.miner_json_rpc.client.request')
    def test_get_peer_addr(self, mock_json_rpc_client):
        peer_addr = '/p2p/11jr2kMp1bZvSC6pd3XkNvs9Q43qCgEzxRwV6vpuqXanC5UcLEs'
        mock_json_rpc_client.return_value = Response(
            data=Result(
                result={'peer_addr': peer_addr}
            )
        )
        client = MinerClient()
        result = client.get_peer_addr()
        mock_json_rpc_client.assert_called_with(
            BASE_URL,
            'peer_addr'
        )
        self.assertEqual(result, {'peer_addr': peer_addr})

    @mock.patch('hm_pyhelper.miner_json_rpc.client.request')
    def test_get_peer_book(self, mock_json_rpc_client):
        mock_json_rpc_client.return_value = Response(
            data=Result(
                result=[]
            )
        )
        client = MinerClient()
        result = client.get_peer_book()
        mock_json_rpc_client.assert_called_with(
            BASE_URL,
            'peer_book',
            addr='self'
        )
        self.assertEqual(result, [])

    @mock.patch('hm_pyhelper.miner_json_rpc.client.request')
    def test_get_firmware_version(self, mock_json_rpc_client):
        firmware_version = '2021.10.18.0'
        summary = {
            'block_age': 1136610,
            'epoch': 25612,
            'firmware_version': firmware_version,
            'gateway_details': 'undefined',
            'height': 993640,
            'mac_addresses': [
                {'eth0': '0242AC110002'},
                {'ip6tnl0': '00000000000000000000000000000000'},
                {'tunl0': '00000000'},
                {'lo': '000000000000'}
            ],
            'name': 'scruffy-chocolate-shell',
            'peer_book_entry_count': 3,
            'sync_height': 993640,
            'uptime': 144,
            'version': 10010005
        }
        mock_json_rpc_client.return_value = Response(
            data=Result(
                result=summary
            )
        )
        client = MinerClient()
        result = client.get_firmware_version()
        mock_json_rpc_client.assert_called_with(
            BASE_URL,
            'info_summary'
        )
        self.assertEqual(result, firmware_version)
