import base58
import grpc

from hm_pyhelper.protos import blockchain_txn_add_gateway_v1_pb2, \
    local_pb2_grpc, local_pb2, region_pb2, gateway_staking_mode_pb2
from hm_pyhelper.gateway_grpc.exceptions import MinerMalformedAddGatewayTxn

from hm_pyhelper.logger import get_logger

LOGGER = get_logger(__name__)


def decode_pub_key(encoded_key: bytes) -> str:
    # Addresses returned by the RPC response are missing a leading
    # byte for the version. The version is currently always 0.
    # https://github.com/helium/helium-js/blob/8d5cb76e156fb80de6fc80f239b43e3872c7b7d7/packages/crypto/src/Address.ts#L64
    version_byte = b'\x00'

    # Convert binary address to base58
    complete_key = version_byte + encoded_key
    decoded_key = base58.b58encode_check(complete_key).decode()
    return decoded_key


class GatewayClient(object):
    '''
    GatewayClient wraps grpc api provided by helium gateway-rs
    It provides some convenience methods to support the old api
    to limit breaking changes.
    Direct interaction with the grpc api can be achieved by
    using GatewayClient.stub.<api>

    All methods might return grpc pass through exceptions.
    '''

    def __init__(self, url='helium-miner:4467'):
        self._url = url
        self._channel = grpc.insecure_channel(url)
        self._channel.subscribe(self._connect_state_handler)
        self.stub = local_pb2_grpc.apiStub(self._channel)

    def _connect_state_handler(self, state):
        if state == grpc.ChannelConnectivity.SHUTDOWN:
            LOGGER.error('GRPC Channel shutdown : irrecoverable error')

    def __enter__(self):
        return self

    def __exit__(self, _, _2, _3):
        self._channel.close()

    def api_stub(self):
        return self.stub

    def get_region_enum(self) -> int:
        '''
        Returns the current configured region of the gateway.
        If not asserted or set in settings, defaults to 0 (US915)
        ref: https://github.com/helium/proto/blob/master/src/region.proto
        '''
        return self.stub.region(local_pb2.region_req()).region

    def get_region(self) -> str:
        '''
        Returns the current configured region of the gateway.
        If not asserted or set in settings, defaults to 0 (US915)
        '''
        region_id = self.get_region_enum()
        return region_pb2.region.Name(region_id)

    def get_pubkey(self) -> str:
        '''
        Returns decoded public key of the gateway
        '''
        encoded_key = self.stub.pubkey(local_pb2.pubkey_req()).address
        return decode_pub_key(encoded_key)

    def get_summary(self) -> dict:
        '''
        Returns a dict with following information
        {
            "region": str
                configured region eg. "US915",
            "key": str
                gateway/device public key
        }
        '''
        return {
            'region': self.get_region(),
            'key': self.get_pubkey()
        }

    def create_add_gateway_txn(self, owner_address: str, payer_address: str,
                               staking_mode: gateway_staking_mode_pb2.gateway_staking_mode
                               = gateway_staking_mode_pb2.gateway_staking_mode.light
                               ) -> bytes:
        """
        Invokes the txn_add_gateway RPC endpoint on the gateway and returns
        the same payload that the smartphone app traditionally expects.
        https://docs.helium.com/mine-hnt/full-hotspots/become-a-maker/hotspot-integration-testing/#generate-an-add-hotspot-transaction

        Parameters:
            - owner_address: The address of the account that owns the gateway.
            - payer_address: The address of the account that will pay for the
                             transaction. This will typically be the
                             maker/Nebra's account.
            - staking_mode: The staking mode of the gateway.
                            ref:
                            https://github.com/helium/proto/blob/master/src/service/local.proto#L38
        """
        # base58 gives version number as first byte. Get rid of it.
        owner = base58.b58decode_check(owner_address)[1:]
        payer = base58.b58decode_check(payer_address)[1:]
        response = self.stub.add_gateway(local_pb2.add_gateway_req(
            owner=owner,
            payer=payer,
            staking_mode=staking_mode
        ))
        return response.add_gateway_txn


def get_address_from_add_gateway_txn(add_gateway_txn:
                                     blockchain_txn_add_gateway_v1_pb2,
                                     address_type: str,
                                     expected_address: str = None):
    """
    Deserializes specified field in the blockchain_txn_add_gateway_v1_pb2
    protobuf to a base58 Helium address.

    Params:
        - add_gateway_txn: The blockchain_txn_add_gateway_v1_pb2 to
                           inspect.
        - address_type: 'owner', 'gateway', or 'payer'.
        - expected_address (optional): Value we expect to be returned.

    Raises:
        MinerMalformedAddGatewayTxn if expected_address supplied and
        does not match the return value.
    """

    # Addresses returned by the RPC response are missing a leading
    # byte for the version. The version is currently always 0.
    # https://github.com/helium/helium-js/blob/8d5cb76e156fb80de6fc80f239b43e3872c7b7d7/packages/crypto/src/Address.ts#L64
    version_byte = b'\x00'

    # Convert binary address to base58
    address_bytes = version_byte + getattr(add_gateway_txn, address_type)
    address = str(base58.b58encode_check(address_bytes), 'utf-8')

    # Ensure resulting address matches expectation
    is_expected_address_defined = expected_address is not None
    if is_expected_address_defined and address != expected_address:
        msg = f"Expected {address_type} address to be {expected_address}," + \
              f"but is {address}"
        raise MinerMalformedAddGatewayTxn(msg)

    return address
