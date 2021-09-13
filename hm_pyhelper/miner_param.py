import os
import subprocess
import logging
import json


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
    except subprocess.CalledProcessError:
        logging.error("gateway_mfr exited with a non-zero status")
        return False

    try:
        return json.loads(run_gateway_mfr_keys.stdout)
    except json.JSONDecodeError:
        logging.error("Unable to parse JSON from gateway_mfr")
    return False


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
