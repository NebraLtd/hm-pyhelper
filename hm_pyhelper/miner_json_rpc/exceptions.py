class MinerJSONRPCException(Exception):
    pass


class MinerConnectionError(MinerJSONRPCException):
    pass


class MinerMalformedURL(MinerJSONRPCException):
    pass


class MinerRegionUnset(MinerJSONRPCException):
    pass


class MinerFailedFetchData(MinerJSONRPCException):
    pass


class MinerFailedToFetchEthernetAddress(MinerJSONRPCException):
    pass


class MinerMalformedAddGatewayTxn(MinerJSONRPCException):
    pass
