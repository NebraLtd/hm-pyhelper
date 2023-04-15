import unittest
import grpc
from concurrent import futures
from hm_pyhelper.gateway_grpc.client import GatewayClient

from hm_pyhelper.protos import local_pb2
from hm_pyhelper.protos import local_pb2_grpc


class TestData:
    server_port = 4468
    validator_address_decoded = "11yJXQPG9deHqvw2ac6VWtNP7gZj8X3t3Qb3Gqm9j729p4AsdaA"
    pubkey_encoded = b"\x01\xc3\x06\x7f\xb9\x19}\xd1n2\xe2M\xeb\xb5\x11\x7f" \
                     b"\xbc\x12\xebT\xb9\x84R\xc7\xca\xf8o\xdddx\xea~\xab"
    pubkey_decoded = "14RdqcZC2rbdTBwNaTsj5EVWYaM7BKGJ44ycq6wWJy9Hg7RKCii"
    region_enum = 0
    region_name = "US915"
    expected_summary = {
        'region': region_name,
        'key': pubkey_decoded
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

    def test_get_region(self):
        with GatewayClient(f'localhost:{TestData.server_port}') as client:
            self.assertEqual(client.get_region_enum(), TestData.region_enum)
            self.assertEqual(client.get_region(), TestData.region_name)

    def test_get_summary(self):
        with GatewayClient(f'localhost:{TestData.server_port}') as client:
            # summary when helium_gateway is not installed
            test_summary_copy = TestData.expected_summary.copy()
            self.assertIn(client.get_summary(),
                          [TestData.expected_summary, test_summary_copy])

    def test_connection_failure(self):
        with self.assertRaises(grpc.RpcError):
            with GatewayClient('localhost:1234') as client:
                client.get_pubkey()
