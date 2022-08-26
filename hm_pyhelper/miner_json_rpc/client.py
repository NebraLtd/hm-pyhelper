import requests
import base64
import base58

from hm_pyhelper.protos import blockchain_txn_pb2, \
                               blockchain_txn_add_gateway_v1_pb2
from hm_pyhelper.miner_json_rpc.exceptions import MinerConnectionError, \
                                                  MinerMalformedURL, \
                                                  MinerRegionUnset, \
                                                  MinerMalformedAddGatewayTxn


class Client(object):

    def __init__(self, url='http://helium-miner:4467'):
        self.url = url

    def __fetch_data(self, method, **kwargs):
        req_body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
        }
        if kwargs:
            req_body["params"] = kwargs
        try:
            response = requests.post(self.url, json=req_body)
        except requests.exceptions.ConnectionError:
            raise MinerConnectionError(
                "Unable to connect to miner %s" % self.url
            )
        except requests.exceptions.MissingSchema:
            raise MinerMalformedURL(
                "Miner JSONRPC URL '%s' is not a valid URL"
                % self.url
            )

        if not response.ok:
            response.raise_for_status()

        return response.json().get('result')

    def get_height(self):
        return self.__fetch_data('info_height')

    def get_region(self):
        region = self.__fetch_data('info_region')
        if not region.get('region'):
            raise MinerRegionUnset(
                "Miner at %s does not have an asserted region"
                % self.url
            )
        return region

    def get_summary(self):
        return self.__fetch_data('info_summary')

    def get_peer_addr(self):
        return self.__fetch_data('peer_addr')

    def get_peer_book(self):
        return self.__fetch_data('peer_book', addr='self')

    def get_firmware_version(self):
        summary = self.get_summary()
        return summary.get('firmware_version')

    def create_add_gateway_txn(self, owner_address: str, payer_address: str,
                               gateway_address: str = None) -> dict:
        """
        Invokes the txn_add_gateway RPC endpoint on the miner and returns
        the same payload that the smartphone app traditionally expects.
        https://docs.helium.com/mine-hnt/full-hotspots/become-a-maker/hotspot-integration-testing/#generate-an-add-hotspot-transaction

        Alternatively, the same thing can be accomplished with dbus,
        like in the below, but RPC is generally easier to use.
        https://github.com/NebraLtd/hm-config/blob/900aeed353fb9729b49bca97d7da8a9abf0a2029/gatewayconfig/bluetooth/characteristics/add_gateway_characteristic.py#L71

        Parameters:
            - owner_address: The address of the account that owns the gateway.
            - payer_address: The address of the account that will pay for the
                             transaction. This will typically be the
                             maker/Nebra's account.
            - gateway_address: The address of the miner itself. This is
                               an optional parameter because the miner
                               will always return it in the payload during
                               transaction generation. If the param is
                               provided, it will only be used as extra
                               validation.

        Raises:
            - MinerMalformedAddGatewayTxn if returned transaction does
              not correspond to the supplied parameters.
        """
        # Invoke add_gateway_txn on miner
        # https://github.com/helium/miner/blob/b9d2cd108cdcc864b641ccf4209f790b1461926d/src/jsonrpc/miner_jsonrpc_txn.erl#L31
        rpc_response = self.__fetch_data('txn_add_gateway',
                                         owner=owner_address,
                                         payer=payer_address)
        encoded_wrapped_txn = rpc_response['result']

        # Base64 decode
        # https://github.com/helium/miner/blob/b9d2cd108cdcc864b641ccf4209f790b1461926d/src/jsonrpc/miner_jsonrpc_txn.erl#L38
        decoded_wrapped_txn = base64.b64decode(encoded_wrapped_txn)

        # Deserialize wrapped protobuf
        # https://github.com/helium/blockchain-core/blob/3cd6bca6c5595a1363a9bbd625ef254383a4141b/src/transactions/blockchain_txn.erl#L160
        wrapped_txn = blockchain_txn_pb2.blockchain_txn()
        wrapped_txn.ParseFromString(decoded_wrapped_txn)

        # Unwrap to get blockchain_txn_add_gateway_v1
        # https://github.com/helium/proto/blob/6dc60a9933628c3baf9d2f5386481f20a5d79bb8/src/blockchain_txn_add_gateway_v1.proto#L1
        add_gateway_txn = wrapped_txn.add_gateway

        txn_gateway_address = get_address_from_add_gateway_txn(
            add_gateway_txn, 'gateway', gateway_address)

        txn_owner_address = get_address_from_add_gateway_txn(
            add_gateway_txn, 'owner', owner_address)

        txn_payer_address = get_address_from_add_gateway_txn(
            add_gateway_txn, 'payer', payer_address)

        return {
            'gateway_address': txn_gateway_address,
            'owner_address': txn_owner_address,
            'payer_address': txn_payer_address,
            'fee': add_gateway_txn.fee,
            'staking_fee': add_gateway_txn.staking_fee,
            'txn': encoded_wrapped_txn
        }


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
        raise MinerMalformedAddGatewayTxn(msg)

    return address
