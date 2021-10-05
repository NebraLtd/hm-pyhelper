import os
import subprocess
import logging
import json
from retry import retry
from hm_pyhelper.utils.logger import get_logger

logger = get_logger(__name__)


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


REGION_OVERRIDE_KEY = 'REGION_OVERRIDE'
REGION_FILEPATH = '/var/pktfwd/region'
REGION_INVALID_SLEEP_SECONDS = 30
REGION_FILE_MISSING_SLEEP_SECONDS = 60


class MalformedRegionException(Exception):
    pass


@retry(MalformedRegionException, delay=REGION_INVALID_SLEEP_SECONDS, logger=logger) # noqa
@retry(FileNotFoundError, delay=REGION_FILE_MISSING_SLEEP_SECONDS, logger=logger) # noqa
def get_region():
    """
    Return the region from the environment or parse file created by hm-miner.
    Retry if region in file is malformed or not found.
    """
    region = os.getenv(REGION_OVERRIDE_KEY, False)
    if region:
        return region

    logger.debug("No REGION_OVERRIDE defined, will retrieve from miner.")
    with open(REGION_FILEPATH) as region_file:
        region = region_file.read().rstrip('\n')
        logger.debug("Region %s parsed from %s " % (region, REGION_FILEPATH))

        is_region_valid = len(region) > 3
        if is_region_valid:
            return region

        raise MalformedRegionException("Region %s is invalid" % region)
