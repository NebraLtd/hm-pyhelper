import os
import re
import subprocess
import json
import platform
from urllib.parse import urlparse
from packaging.version import Version

from retry import retry

from hm_pyhelper.lock_singleton import ResourceBusyError, lock_ecc
from hm_pyhelper.logger import get_logger
from hm_pyhelper.exceptions import MalformedRegionException, \
    SPIUnavailableException, ECCMalfunctionException, \
    GatewayMFRFileNotFoundException, \
    MinerFailedToFetchMacAddress, GatewayMFRExecutionException, GatewayMFRInvalidVersion, \
    UnsupportedGatewayMfrVersion
from hm_pyhelper.hardware_definitions import get_variant_attribute, \
    UnknownVariantException, UnknownVariantAttributeException


LOGGER = get_logger(__name__)
REGION_INVALID_SLEEP_SECONDS = 30
REGION_FILE_MISSING_SLEEP_SECONDS = 60
SPI_UNAVAILABLE_SLEEP_SECONDS = 60


@lock_ecc()
def run_gateway_mfr(sub_command: str, slot: int = False) -> dict:
    command = get_gateway_mfr_command(sub_command, slot=slot)

    try:
        run_gateway_mfr_result = subprocess.run(
            command,
            capture_output=True,
            check=True
        )
        LOGGER.info(f"gateway_mfr response stdout: {run_gateway_mfr_result.stdout}")
        LOGGER.info(f"gateway_mfr response stderr: {run_gateway_mfr_result.stderr}")
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
        raise ResourceBusyError(e) \
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
    machine = platform.machine()

    if 'aarch64' in machine:
        gateway_mfr_path = os.path.join(direct_path, 'gateway_mfr_aarch64')
    elif 'x86_64' in machine:
        gateway_mfr_path = os.path.join(direct_path, 'gateway_mfr_x86_64')
    else:
        gateway_mfr_path = os.path.join(direct_path, 'gateway_mfr')
    return gateway_mfr_path


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


def get_ecc_location() -> str:
    ecc_list = get_variant_attribute(os.getenv('VARIANT'), 'SWARM_KEY_URI')
    ecc_location = None

    try:
        with open("/var/nebra/ecc_file", 'r') as data:
            generated_ecc_location = str(data.read()).rstrip('\n')

        if len(generated_ecc_location) < 10:
            generated_ecc_location = None
        else:
            LOGGER.info("Generated ECC location file found: " + generated_ecc_location)
    except FileNotFoundError:
        # No ECC location file found, create variable with value None
        generated_ecc_location = None

    if os.getenv('SWARM_KEY_URI_OVERRIDE'):
        ecc_location = os.getenv('SWARM_KEY_URI_OVERRIDE')
    elif generated_ecc_location is not None:
        ecc_location = generated_ecc_location
    elif len(ecc_list) == 1:
        ecc_location = ecc_list[0]
    else:
        for location in ecc_list:
            parse_result = urlparse(location)
            i2c_bus = parse_i2c_bus(parse_result.hostname)
            i2c_address = parse_i2c_address(parse_result.port)
            command = f'i2cdetect -y {i2c_bus}'
            parameter = f'{i2c_address} --'

            if config_search_param(command, parameter):
                ecc_location = location
                with open("/var/nebra/ecc_file", "w") as file:
                    file.write(ecc_location)
                return ecc_location

    if not ecc_location:
        LOGGER.error("Can't find ECC. Ensure SWARM_KEY_URI is correct in hardware definitions.")

    return ecc_location


def get_gateway_mfr_command(sub_command: str, slot: int = False) -> list:
    gateway_mfr_path = get_gateway_mfr_path()
    command = [gateway_mfr_path]

    gateway_mfr_version = get_gateway_mfr_version()

    if gateway_mfr_version >= Version('0.2.0'):
        try:
            device_arg = [
                '--device',
                get_ecc_location()
            ]
            command.extend(device_arg)
        except (UnknownVariantException, UnknownVariantAttributeException) as e:
            LOGGER.warning(str(e) + ' Omitting --device arg.')

        if slot:
            slot_str = f'slot={slot}'
            slot_pattern = r'(slot=\d+)'
            command[-1] = re.sub(slot_pattern, slot_str, command[-1])

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


def provision_key(slot: int, force: bool = False):
    """
    Attempt to provision key.

    :param slot: The ECC key slot to use
    :param force: If set to True then try `key --generate` if `provision` action fails.

    :return: A 2 element tuple, first one specifying provisioning success (True/False) and
             second element contains gateway mfr output or error response.
    """

    provisioning_successful = False
    response = ''

    try:
        gateway_mfr_result = run_gateway_mfr("provision", slot=slot)
        LOGGER.info(f"[ECC Provisioning] {gateway_mfr_result}")
        provisioning_successful = True
        response = gateway_mfr_result

    except subprocess.CalledProcessError as exp:
        LOGGER.error("[ECC Provisioning] Exited with a non-zero status")
        provisioning_successful = False
        response = str(exp)

    except Exception as exp:
        response = str(exp)
        LOGGER.error(f"[ECC Provisioning] Error during provisioning. {response}")
        provisioning_successful = False

    # Try key generation.
    if provisioning_successful is False and force is True:
        try:
            gateway_mfr_result = run_gateway_mfr("key --generate", slot=slot)
            provisioning_successful = True
            response = gateway_mfr_result

        except Exception as exp:
            response = str(exp)
            LOGGER.error(f"[ECC Provisioning] key --generate failed: {response}")

    return provisioning_successful, response


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
    # Get ethernet and wlan MAC address

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
            LOGGER.error(e)
            raise MinerFailedToFetchMacAddress(str(e))


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
    except FileNotFoundError as e:
        # logging as warning because some people remove wifi from their outdoor units.
        # We can't do anything about these errors even if they were failing wifi units.
        LOGGER.warning("Failed to find Miner"
                       f"Mac Address file at path {path}")
        raise MinerFailedToFetchMacAddress("Failed to find file"
                                           "containing miner mac address. "
                                           "Exception: %s" % str(e)) \
            .with_traceback(e.__traceback__)
    except PermissionError as e:
        LOGGER.exception("Permissions invalid for Miner"
                         f"Mac Address file at path {path}")
        raise MinerFailedToFetchMacAddress("Failed to fetch"
                                           "miner mac address. "
                                           "Invalid permissions to access "
                                           "file. Exception: %s" % str(e)) \
            .with_traceback(e.__traceback__)
    except Exception as e:
        LOGGER.exception(e)
        raise MinerFailedToFetchMacAddress("Failed to fetch miner"
                                           "mac address. "
                                           "Exception: %s" % str(e)) \
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
        f"No region override set (value = {region_override}), will retrieve from miner.")  # noqa: E501
    with open(region_filepath) as region_file:
        region = region_file.read().rstrip('\n')
        LOGGER.debug(f"Region {region} parsed from {region_filepath}")

        is_region_valid = len(region) > 3
        if is_region_valid:
            return region

        raise MalformedRegionException(f"Region {region} is invalid")


@retry(SPIUnavailableException, delay=SPI_UNAVAILABLE_SLEEP_SECONDS,
       logger=LOGGER)  # noqa
def await_spi_available(spi_bus):
    """
    Check that the SPI bus path exists, assuming it is in /dev/{spi_bus}
    """
    if os.path.exists(f"/dev/{spi_bus}"):
        LOGGER.debug(f"SPI bus {spi_bus} Configured Correctly")
        return True
    else:
        raise SPIUnavailableException(f"SPI bus {spi_bus} not found!")


def config_search_param(command, param):
    """
    input:
        command: Command to execute
        param: The parameter we are looking for in the response
    return: True is exist, or False if doesn't exist
    Possible exceptions:
        TypeError: If the arguments passed to the function are not strings.
    """
    if type(command) is not str:
        raise TypeError("The command must be a string value")
    if type(param) is not str:
        raise TypeError("The param must be a string value")
    result = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    out, err = result.communicate()
    out = out.decode("UTF-8")
    if param in out:
        return True
    else:
        return False


def parse_i2c_bus(address):
    """
    Takes i2c bus as input parameter, extracts the bus number and returns it.
    """
    i2c_bus_pattern = r'i2c-(\d+)'
    return re.search(i2c_bus_pattern, address).group(1)


def parse_i2c_address(port):
    """
    Takes i2c address in decimal as input parameter, extracts the hex version and returns it.
    """
    return f'{port:x}'
