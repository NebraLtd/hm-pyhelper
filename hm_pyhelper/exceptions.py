class MalformedRegionException(Exception):
    pass


class SPIUnavailableException(Exception):
    pass


class ECCMalfunctionException(Exception):
    pass


class GatewayMFRFileNotFoundException(Exception):
    pass


class MinerFailedToFetchMacAddress(Exception):
    pass


class UnknownVariantException(Exception):
    pass


class UnknownVariantAttributeException(Exception):
    pass


class GatewayMFRExecutionException(Exception):
    pass


class GatewayMFRInvalidVersion(Exception):
    pass


class UnsupportedGatewayMfrVersion(Exception):
    pass
