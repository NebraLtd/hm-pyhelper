import os
import subprocess
import json
from retry import retry
from hm_pyhelper.lock_singleton import ResourceBusyError, lock_ecc
from hm_pyhelper.logger import get_logger
from hm_pyhelper.exceptions import MalformedRegionException, \
    SPIUnavailableException, ECCMalfunctionException, \
    GatewayMFRFileNotFoundException, \
    MinerFailedToFetchMacAddress
from hm_pyhelper.miner_json_rpc.exceptions import \
     MinerFailedToFetchEthernetAddress
from hm_pyhelper.hardware_definitions import is_rockpi


LOGGER = get_logger(__name__)
REGION_INVALID_SLEEP_SECONDS = 30
REGION_FILE_MISSING_SLEEP_SECONDS = 60
SPI_UNAVAILABLE_SLEEP_SECONDS = 60


@lock_ecc()
def run_gateway_mfr(args):
    direct_path = os.path.dirname(os.path.abspath(__file__))
    gateway_mfr_path = os.path.join(direct_path, 'gateway_mfr')

    command = [gateway_mfr_path]

    if is_rockpi():
        extra_args = ['--path', '/dev/i2c-7']
        command.extend(extra_args)

    command.extend(args)

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
        err_str = "Exception occured on running gateway_mfr %s" \
                  % str(e)
        LOGGER.exception(e)
        raise ECCMalfunctionException(err_str).with_traceback(e.__traceback__)

    try:
        return json.loads(run_gateway_mfr_result.stdout)
    except json.JSONDecodeError as e:
        err_str = "Unable to parse JSON from gateway_mfr"
        LOGGER.exception(err_str)
        raise ECCMalfunctionException(err_str).with_traceback(e.__traceback__)


def get_public_keys_rust():
    """
    Run gateway_mfr and report back the key.
    """
    return run_gateway_mfr(["key", "0"])


def get_getway_mfr_info():
    """
    Run gateway_mfr info.
    """
    return run_gateway_mfr(["info"])


def get_gateway_mfr_test_result():
    """
    Run gateway_mfr test and report back.
    """
    return run_gateway_mfr(["test"])


def provision_key():
    """
    Attempt to provision key.
    """
    direct_path = os.path.dirname(os.path.abspath(__file__))
    gateway_mfr_path = os.path.join(direct_path, 'gateway_mfr')

    test_results = get_gateway_mfr_test_result()
    if did_gateway_mfr_test_result_include_miner_key_pass(test_results):
        return True

    try:
        @lock_ecc()
        def run_gateway_mfr():
            return subprocess.run(
                [gateway_mfr_path, "provision"],
                capture_output=True,
                check=True
            )

        gateway_mfr_result = run_gateway_mfr()
        LOGGER.info("[ECC Provisioning] %s", gateway_mfr_result.stdout)

    except subprocess.CalledProcessError:
        LOGGER.error("[ECC Provisioning] Exited with a non-zero status")
        return False
    return True


def did_gateway_mfr_test_result_include_miner_key_pass(
        gateway_mfr_test_result
):
    """
    Returns true if gateway_mfr_test_result["tests"] has an entry where
    "test": "miner_key(0)" and "result": "pass"
    Input: {
        "result": "pass",
        "tests": [
            {
            "output": "ok",
            "result": "pass",
            "test": "serial"
            },
            {
            "output": "ok",
            "result": "pass",
            "test": "zone_locked(data)"
            },
            {
            "output": "ok",
            "result": "pass",
            "test": "zone_locked(config)"
            },
            {
            "output": "ok",
            "result": "pass",
            "test": "slot_config(0..=15, ecc)"
            },
            {
            "output": "ok",
            "result": "pass",
            "test": "key_config(0..=15, ecc)"
            },
            {
            "output": "ok",
            "result": "pass",
            "test": "miner_key(0)"
            }
        ]
    }
    """

    def is_miner_key_and_passed(test_result):
        return test_result['test'] == 'miner_key(0)' and \
               test_result['result'] == 'pass'

    results_is_miner_key_and_passed = map(
        is_miner_key_and_passed,
        gateway_mfr_test_result['tests']
    )
    return any(results_is_miner_key_and_passed)


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
        LOGGER.exception("Failed to find Miner"
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
