import os
import subprocess
import logging
import json
from retry import retry
from hm_pyhelper.logger import get_logger
from hm_pyhelper.exceptions import MalformedRegionException, \
    SPIUnavailableException

LOGGER = get_logger(__name__)
REGION_INVALID_SLEEP_SECONDS = 30
REGION_FILE_MISSING_SLEEP_SECONDS = 60
SPI_UNAVAILABLE_SLEEP_SECONDS = 60


def log_stdout_stderr(sp_result):
    logging.info('gateway_mfr response stdout: %s' % sp_result.stdout)
    logging.info('gateway_mfr response stderr: %s' % sp_result.stderr)


def get_public_keys_rust():
    """
    Run gateway_mfr and report back the key.
    """
    direct_path = os.path.dirname(os.path.abspath(__file__))
    gateway_mfr_path = os.path.join(direct_path, 'gateway_mfr')

    try:
        run_gateway_mfr_keys = subprocess.run(
            [gateway_mfr_path, "key", "0"],
            capture_output=True,
            check=True
        )
        log_stdout_stderr(run_gateway_mfr_keys)
    except subprocess.CalledProcessError:
        logging.error("gateway_mfr exited with a non-zero status")
        return False

    try:
        return json.loads(run_gateway_mfr_keys.stdout)
    except json.JSONDecodeError:
        logging.error("Unable to parse JSON from gateway_mfr")
    return False


def get_gateway_mfr_test_result():
    """
    Run gateway_mfr test and report back.
    """
    direct_path = os.path.dirname(os.path.abspath(__file__))
    gateway_mfr_path = os.path.join(direct_path, 'gateway_mfr')

    try:
        run_gateway_mfr_keys = subprocess.run(
            [gateway_mfr_path, "test"],
            capture_output=True,
            check=True
        )
        log_stdout_stderr(run_gateway_mfr_keys)
    except subprocess.CalledProcessError:
        logging.error("gateway_mfr exited with a non-zero status")
        return False

    try:
        return json.loads(run_gateway_mfr_keys.stdout)
    except json.JSONDecodeError:
        logging.error("Unable to parse JSON from gateway_mfr")
    return False


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
        run_gateway_mfr = subprocess.run(
            [gateway_mfr_path, "provision"],
            capture_output=True,
            check=True
        )
        logging.info("[ECC Provisioning] %s",  run_gateway_mfr.stdout)

    except subprocess.CalledProcessError:
        logging.error("[ECC Provisioning] Exited with a non-zero status")
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
        except Exception as e:
            diagnostics[key] = False
            logging.error(e)


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
        raise TypeError("The path must be a string value")
    try:
        file = open(path)
    except FileNotFoundError as e:
        raise e
    except PermissionError as e:
        raise e
    return file.readline().strip().upper()


@retry(MalformedRegionException, delay=REGION_INVALID_SLEEP_SECONDS, logger=LOGGER) # noqa
@retry(FileNotFoundError, delay=REGION_FILE_MISSING_SLEEP_SECONDS, logger=LOGGER) # noqa
def retry_get_region(region_override, region_filepath):
    """
    Return the override if it exists, or parse file created by hm-miner.
    region_override is the actual value,
    not the name of the environment variable.
    Retry if region in file is malformed or not found.
    """
    if region_override:
        return region_override

    LOGGER.debug("No region override set (value = %s), will retrieve from miner." % region_override)  # noqa: E501
    with open(region_filepath) as region_file:
        region = region_file.read().rstrip('\n')
        LOGGER.debug("Region %s parsed from %s " % (region, region_filepath))

        is_region_valid = len(region) > 3
        if is_region_valid:
            return region

        raise MalformedRegionException("Region %s is invalid" % region)


@retry(SPIUnavailableException, delay=SPI_UNAVAILABLE_SLEEP_SECONDS, logger=LOGGER) # noqa
def await_spi_available(spi_bus):
    """
    Check that the SPI bus path exists, assuming it is in /dev/{spi_bus}
    """
    if os.path.exists('/dev/{}'.format(spi_bus)):
        LOGGER.debug("SPI bus %s Configured Correctly" % spi_bus)
        return True
    else:
        raise SPIUnavailableException("SPI bus %s not found!" % spi_bus)
