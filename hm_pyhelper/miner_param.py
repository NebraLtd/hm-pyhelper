import os
import subprocess
import json
from packaging.version import Version

from retry import retry

from hm_pyhelper.lock_singleton import ResourceBusyError, lock_ecc
from hm_pyhelper.logger import get_logger
from hm_pyhelper.exceptions import MalformedRegionException, \
    SPIUnavailableException, ECCMalfunctionException, \
    GatewayMFRFileNotFoundException, \
    MinerFailedToFetchMacAddress, GatewayMFRExecutionException, GatewayMFRInvalidVersion, \
    UnsupportedGatewayMfrVersion
from hm_pyhelper.miner_json_rpc.exceptions import \
     MinerFailedToFetchEthernetAddress
from hm_pyhelper.hardware_definitions import get_variant_attribute, \
    UnknownVariantException, UnknownVariantAttributeException


LOGGER = get_logger(__name__)
REGION_INVALID_SLEEP_SECONDS = 30
REGION_FILE_MISSING_SLEEP_SECONDS = 60
SPI_UNAVAILABLE_SLEEP_SECONDS = 60


@lock_ecc()
def run_gateway_mfr(sub_command: str) -> None:
    command = get_gateway_mfr_command(sub_command)

    try:
        run_gateway_mfr_result = subprocess.run(
            command,
            capture_output=True,
            check=True
        )
        LOGGER.info(
            'gateway_mfr response stdout: %s' % run_gateway_mfr_result.stdout)
        LOGGER.info(
            'gateway_mfr response stderr: %s' % run_gateway_mfr_result.stderr)
    except subprocess.CalledProcessError as e:
        err_str = "gateway_mfr exited with a non-zero status"
        LOGGER.exception(err_str)
        raise ECCMalfunctionException(err_str).with_traceback(e.__traceback__)
    except (FileNotFoundError, NotADirectoryError) as e:
        err_str = "file/directory for gateway_mfr was not found"
        LOGGER.exception(err_str)
        raise GatewayMFRFileNotFoundException(err_str) \
            .with_traceback(e.__traceback__)
    except ResourceBusyError as e:
        err_str = "resource busy error: %s"
        LOGGER.exception(err_str % str(e))
        raise ResourceBusyError(e)\
            .with_traceback(e.__traceback__)
    except Exception as e:
        err_str = "Exception occurred on running gateway_mfr %s" \
                  % str(e)
        LOGGER.exception(e)
        raise ECCMalfunctionException(err_str).with_traceback(e.__traceback__)

    try:
        return json.loads(run_gateway_mfr_result.stdout)
    except json.JSONDecodeError as e:
        err_str = "Unable to parse JSON from gateway_mfr"
        LOGGER.exception(err_str)
        raise ECCMalfunctionException(err_str).with_traceback(e.__traceback__)


def get_gateway_mfr_path() -> str:
    direct_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(direct_path, 'gateway_mfr')


def get_gateway_mfr_version() -> Version:
    """
    Returns version of gateway_mfr
    """
    gateway_mfr_path = get_gateway_mfr_path()
    command = [gateway_mfr_path, '--version']

    try:
        run_gateway_mfr_result = subprocess.run(
            command,
            capture_output=True,
            check=True
        )
    except Exception as e:
        err_str = f"Exception occurred on running gateway_mfr --version: {e}"
        LOGGER.exception(err_str)
        raise GatewayMFRExecutionException(err_str).with_traceback(e.__traceback__)

    # Parse gateway_mfr version
    try:
        version_str = run_gateway_mfr_result.stdout.decode().rpartition(' ')[-1]
        gateway_mfr_version = Version(version_str)

        return gateway_mfr_version
    except Exception as e:
        err_str = f"Exception occurred while parsing gateway_mfr version: {e}"
        LOGGER.exception(err_str)
        raise GatewayMFRInvalidVersion(err_str).with_traceback(e.__traceback__)


def get_gateway_mfr_command(sub_command: str) -> list:
    gateway_mfr_path = get_gateway_mfr_path()
    command = [gateway_mfr_path]

    gateway_mfr_version = get_gateway_mfr_version()
    if Version('0.1.1') < gateway_mfr_version < Version('0.2.0'):
        try:
            device_arg = [
                '--path',
                get_variant_attribute(os.getenv('VARIANT'), 'KEY_STORAGE_BUS')
            ]
            command.extend(device_arg)
        except (UnknownVariantException, UnknownVariantAttributeException) as e:
            LOGGER.warning(str(e) + ' Omitting --path arg.')

        command.append(sub_command)

        # In case of "key" command, append the slot number 0 at the end.
        if sub_command == "key":
            command.append("0")

    elif gateway_mfr_version >= Version('0.2.0'):
        try:
            device_arg = [
                '--device',
                get_variant_attribute(os.getenv('VARIANT'), 'SWARM_KEY_URI')
            ]
            command.extend(device_arg)
        except (UnknownVariantException, UnknownVariantAttributeException) as e:
            LOGGER.warning(str(e) + ' Omitting --device arg.')

        if ' ' in sub_command:
            command += sub_command.split(' ')
        else:
            command.append(sub_command)

    else:
        raise UnsupportedGatewayMfrVersion(f"Unsupported gateway_mfr version {gateway_mfr_version}")

    return command


def get_public_keys_rust():
    """
    Run gateway_mfr and report back the key.
    """
    return run_gateway_mfr("key")


def get_getway_mfr_info():
    """
    Run gateway_mfr info.
    """
    return run_gateway_mfr("info")


def get_gateway_mfr_test_result():
    """
    Run gateway_mfr test and report back.
    """
    return run_gateway_mfr("test")


def provision_key():
    """
    Attempt to provision key.
    """
    test_results = get_gateway_mfr_test_result()
    if did_gateway_mfr_test_result_include_miner_key_pass(test_results):
        return True

    provisioning_successful = False

    try:
        gateway_mfr_result = run_gateway_mfr("provision")
        LOGGER.info("[ECC Provisioning] %s", gateway_mfr_result)
        provisioning_successful = True

    except subprocess.CalledProcessError:
        LOGGER.error("[ECC Provisioning] Exited with a non-zero status")
        provisioning_successful = False

    except Exception as exp:
        LOGGER.error("[ECC Provisioning] Error during provisioning. %s" % str(exp))
        provisioning_successful = False

    return provisioning_successful


def did_gateway_mfr_test_result_include_miner_key_pass(
        gateway_mfr_test_result
):
    """
    Returns true if gateway_mfr_test_result["tests"] has an key "miner_key(0)" with value
    being a dict that contains result key value set to pass.

    {
        'result': 'pass',
        'tests': 'miner_key(0)': {'result': 'pass'}
    }
    """

    return gateway_mfr_test_result.get(
        'tests', {}).get('miner_key(0)', {}).get('result', 'fail') == 'pass'


def get_ethernet_addresses(diagnostics):
    # Get ethernet MAC and WIFI address

    # The order of the values in the lists is important!
    # It determines which value will be available for which key
    path_to_files = [
        "/sys/class/net/eth0/address",
        "/sys/class/net/wlan0/address"
    ]
    keys = ["E0", "W0"]
    for (path, key) in zip(path_to_files, keys):
        try:
            diagnostics[key] = get_mac_address(path)
        except MinerFailedToFetchMacAddress as e:
            diagnostics[key] = False
            LOGGER.error(e)
        except Exception as e:
            diagnostics[key] = False
            LOGGER.error(e)
            raise MinerFailedToFetchEthernetAddress(str(e))


def get_mac_address(path):
    """
    input: path to the file with the location of the mac address
    output: A string containing a mac address
    Possible exceptions:
        FileNotFoundError - when the file is not found
        PermissionError - in the absence of access rights to the file
        TypeError - If the function argument is not a string.
    """
    if type(path) is not str:
        raise TypeError(
            "Constructing miner mac address failed.\
             The path must be a string value")
    try:
        file = open(path)
    except MinerFailedToFetchMacAddress as e:
        LOGGER.exception(str(e))
    except FileNotFoundError as e:
        # logging as warning because some people remove wifi from their outdoor units.
        # We can't do anything about these errors even if they were failing wifi units.
        LOGGER.warning("Failed to find Miner"
                       "Mac Address file at path %s" % path)
        raise MinerFailedToFetchMacAddress("Failed to find file"
                                           "containing miner mac address."
                                           "Exception: %s" % str(e))\
              .with_traceback(e.__traceback__)
    except PermissionError as e:
        LOGGER.exception("Permissions invalid for Miner"
                         "Mac Address file at path %s" % path)
        raise MinerFailedToFetchMacAddress("Failed to fetch"
                                           "miner mac address. "
                                           "Invalid permissions to access "
                                           "file. Exception: %s" % str(e))\
              .with_traceback(e.__traceback__)
    except Exception as e:
        LOGGER.exception(e)
        raise MinerFailedToFetchMacAddress("Failed to fetch miner"
                                           "mac address. "
                                           "Exception: %s" % str(e))\
              .with_traceback(e.__traceback__)

    return file.readline().strip().upper()


@retry(MalformedRegionException, delay=REGION_INVALID_SLEEP_SECONDS,
       logger=LOGGER)  # noqa
@retry(FileNotFoundError, delay=REGION_FILE_MISSING_SLEEP_SECONDS,
       logger=LOGGER)  # noqa
def retry_get_region(region_override, region_filepath):
    """
    Return the override if it exists, or parse file created by hm-miner.
    region_override is the actual value,
    not the name of the environment variable.
    Retry if region in file is malformed or not found.
    """
    if region_override:
        return region_override

    LOGGER.debug(
        "No region override set (value = %s), will retrieve from miner." % region_override)  # noqa: E501
    with open(region_filepath) as region_file:
        region = region_file.read().rstrip('\n')
        LOGGER.debug("Region %s parsed from %s " % (region, region_filepath))

        is_region_valid = len(region) > 3
        if is_region_valid:
            return region

        raise MalformedRegionException("Region %s is invalid" % region)


@retry(SPIUnavailableException, delay=SPI_UNAVAILABLE_SLEEP_SECONDS,
       logger=LOGGER)  # noqa
def await_spi_available(spi_bus):
    """
    Check that the SPI bus path exists, assuming it is in /dev/{spi_bus}
    """
    if os.path.exists('/dev/{}'.format(spi_bus)):
        LOGGER.debug("SPI bus %s Configured Correctly" % spi_bus)
        return True
    else:
        raise SPIUnavailableException("SPI bus %s not found!" % spi_bus)
