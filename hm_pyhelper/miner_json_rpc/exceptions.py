
class MinerJSONRPCException(Exception):
    pass


class MinerConnectionError(MinerJSONRPCException):
    pass


class MinerMalformedURL(MinerJSONRPCException):
    pass


class MinerRegionUnset(MinerJSONRPCException):
    pass
