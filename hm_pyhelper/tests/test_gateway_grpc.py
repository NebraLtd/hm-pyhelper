import unittest
from unittest.mock import patch
import grpc
from concurrent import futures
from hm_pyhelper.gateway_grpc.client import GatewayClient

from hm_pyhelper.protos import local_pb2
from hm_pyhelper.protos import local_pb2_grpc


class TestData:
    server_port = 4468
    height_res = local_pb2.height_res(
        height=43,
        block_age=42,
        gateway=local_pb2.keyed_uri(
            address=b"\000\177\327E-\223\222e\002e[*\250\260\361p\271\267/"
                    b"\220\026\010\360\213t\304\313\022\316>\254\347?",
            uri="http://32.23.54.23:8080"  # NOSONAR
        )
    )
    validator_address_decoded = "11yJXQPG9deHqvw2ac6VWtNP7gZj8X3t3Qb3Gqm9j729p4AsdaA"
    pubkey_encoded = b"\x01\xc3\x06\x7f\xb9\x19}\xd1n2\xe2M\xeb\xb5\x11\x7f" \
                     b"\xbc\x12\xebT\xb9\x84R\xc7\xca\xf8o\xdddx\xea~\xab"
    pubkey_decoded = "14RdqcZC2rbdTBwNaTsj5EVWYaM7BKGJ44ycq6wWJy9Hg7RKCii"
    chain_vars = {
        "block_size_limit": local_pb2.config_value(name="block_size_limit",
                                                   value=b"5242880",
                                                   type="int"),
        "min_assert_h3_res": local_pb2.config_value(name="min_assert_h3_res",
                                                    value=b"12",
                                                    type="int")
    }
    region_enum = 0
    region_name = "US915"
    dpkg_output = b"""Package: helium_gateway\n
                    Status: install ok installed\n
                    Priority: optional\n
                    Section: utility\n
                    Installed-Size: 3729\n
                    Maintainer: Marc Nijdam <marc@helium.com>\n
                    Architecture: amd64\n
                    Version: 1.0.0~alpha.23\n
                    Depends: curl\n
                    Conffiles:\n
                    /etc/helium_gateway/settings.toml 4d6fb434f97a50066b8163a371d5c208\n
                    Description: Helium Gateway for LoRa packet forwarders\n
                    The Helium Gateway to attach your LoRa gateway to the Helium Blockchain.\n"""
    expected_summary = {
        'region': region_name,
        'key': pubkey_decoded,
        'gateway_version': "v1.0.0",
        'validator': {
            'height': height_res.height,
            'block_age': height_res.block_age,
            'address': validator_address_decoded,
            'uri': height_res.gateway.uri
        }
    }


class MockServicer(local_pb2_grpc.apiServicer):
    def height(self, request, context):
        return TestData.height_res

    def region(self, request, context):
        return local_pb2.region_res(region=0)

    def pubkey(self, request, context):
        return local_pb2.pubkey_res(address=TestData.pubkey_encoded)

    def config(self, request, context):
        result = local_pb2.config_res()
        for key in request.keys:
            if key in TestData.chain_vars.keys():
                result.values.append(TestData.chain_vars.get(key))
            else:
                result.values.append(local_pb2.config_value(name=key))
        return result


class TestGatewayGRPCClient(unittest.TestCase):

    # we can start the real service hear by installing dpkg. But AFAIK
    # our testing methods, real service exposes us to random failures
    def setUp(self):
        self.mock_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        local_pb2_grpc.add_apiServicer_to_server(MockServicer(), self.mock_server)
        self.mock_server.add_insecure_port(f'[::]:{TestData.server_port}')
        self.mock_server.start()

    def tearDown(self):
        self.mock_server.stop(None)

    def test_get_pubkey(self):
        with GatewayClient(f'localhost:{TestData.server_port}') as client:
            self.assertEqual(client.get_pubkey(), TestData.pubkey_decoded)

    def test_get_validator_info(self):
        with GatewayClient(f'localhost:{TestData.server_port}') as client:
            self.assertEqual(client.get_validator_info(), TestData.height_res)

    def test_get_height(self):
        with GatewayClient(f'localhost:{TestData.server_port}') as client:
            self.assertEqual(client.get_height(), client.get_validator_info().height)

    def test_get_region(self):
        with GatewayClient(f'localhost:{TestData.server_port}') as client:
            self.assertEqual(client.get_region_enum(), TestData.region_enum)
            self.assertEqual(client.get_region(), TestData.region_name)

    def test_get_blockchain_variable(self):
        with GatewayClient(f'localhost:{TestData.server_port}') as client:
            for key in TestData.chain_vars:
                self.assertEqual(client.get_blockchain_config_variable(key),
                                 TestData.chain_vars.get(key))

    def test_get_summary(self):
        with GatewayClient(f'localhost:{TestData.server_port}') as client:
            # summary when helium_gateway is not installed
            test_summary_copy = TestData.expected_summary.copy()
            test_summary_copy['gateway_version'] = None
            self.assertIn(client.get_summary(),
                          [TestData.expected_summary, test_summary_copy])

    @patch('subprocess.check_output', return_value=TestData.dpkg_output)
    def test_get_gateway_version(self, mock_check_output):
        mock_check_output.return_value = TestData.dpkg_output
        with GatewayClient(f'localhost:{TestData.server_port}') as client:
            self.assertIn(client.get_gateway_version(),
                          [TestData.expected_summary['gateway_version'], None])

    def test_connection_failure(self):
        with self.assertRaises(grpc.RpcError):
            with GatewayClient('localhost:1234') as client:
                client.get_pubkey()

    def test_invalid_chain_var(self):
        with GatewayClient(f'localhost:{TestData.server_port}') as client:
            with self.assertRaises(ValueError):
                client.get_blockchain_config_variable('not_a_key')
