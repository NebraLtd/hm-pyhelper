import base58
import grpc
import subprocess
import json

from hm_pyhelper.protos import blockchain_txn_add_gateway_v1_pb2, \
    local_pb2_grpc, local_pb2, region_pb2
from hm_pyhelper.gateway_grpc.exceptions import GatewayMalformedAddGatewayTxn

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

    def get_validator_info(self) -> local_pb2.height_res:
        return self.stub.height(local_pb2.height_req())

    def get_height(self) -> int:
        return self.get_validator_info().height

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

    def sign(self, data: bytes) -> bytes:
        '''
        Sign a message with the gateway private key
        '''
        return self.stub.sign(local_pb2.sign_req(data=data)).signature

    def ecdh(self, address: bytes) -> bytes:
        '''
        Return shared secret using ECDH
        '''
        return self.stub.ecdh(local_pb2.ecdh_req(address=address)).secret

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
                gateway/device public key,
            "validator": {
                "height": int
                    blockchain height,
                "block_age": int
                    age of the last block in seconds,
                "address": str
                    public key/address of the validator,
                "uri": http url
                    http endpoint of the validator
            }
        }
        '''
        validator_info = self.get_validator_info()
        return {
            'region': self.get_region(),
            'key': self.get_pubkey(),
            'gateway_version': self.get_gateway_version(),
            'validator': {
                'height': validator_info.height,
                'block_age': validator_info.block_age,
                'address': decode_pub_key(validator_info.gateway.address),
                'uri': validator_info.gateway.uri
            }
        }

    def get_blockchain_config_variables(self, keys: list) -> local_pb2.config_res:
        '''
        Allows one to query blockchain variables. For a complete list of chain variables ref
        https://helium.plus/chain-vars

        Returns config_res which is a list of config_value for the given list
        of blockchain variables.
        '''
        return self.stub.config(local_pb2.config_req(keys=keys))

    def get_blockchain_config_variable(self, key: str) -> local_pb2.config_value:
        '''
        Convenience method to get a single variable from the blockchain

        Raises ValueError if the key is not found
        '''
        values = self.get_blockchain_config_variables(keys=[key]).values
        if not values[0].value:
            raise ValueError(f'{key} not found on chain')
        return values[0]

    def get_gateway_version(self) -> str:
        '''
        Returns the current version of the gateway package installed
        '''
        # NOTE:: there is a command line argument to helium-gateway
        # but it is not exposed in the rpc, falling back to dpkg
        try:
            output = subprocess.check_output(['dpkg', '-s', 'helium_gateway'])
            for line in output.decode().splitlines():
                if line.strip().startswith('Version'):
                    return line.split(':')[1].strip()
            return 'unknown'
        except subprocess.CalledProcessError:
            return 'unknown'

    def create_add_gateway_txn(self, owner_address: str, payer_address: str,
                               staking_mode: local_pb2.gateway_staking_mode = local_pb2.light,
                               gateway_address: str = "") -> dict:
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
            - gateway_address: The address of the miner itself. This is
                               an optional parameter because the miner
                               will always return it in the payload during
                               transaction generation. If the param is
                               provided, it will only be used as extra
                               validation.
        """
        # NOTE:: this is unimplemented as of alpha23 release of the gateway
        response = self.stub.add_gateway(local_pb2.add_gateway_req(
            owner=owner_address.encode('utf-8'),
            payer=payer_address.encode('utf-8'),
            staking_mode=staking_mode
        ))
        return json.loads(response.decode())


def get_address_from_add_gateway_txn(add_gateway_txn:
                                     blockchain_txn_add_gateway_v1_pb2,
                                     address_type: str,
                                     expected_address: str = None):
    """
    Deserializes specified field in the blockchain_txn_add_gateway_v1_pb2
    protobuf to a base58 Helium address.

    Pararms:
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
        raise GatewayMalformedAddGatewayTxn(msg)

    return address
