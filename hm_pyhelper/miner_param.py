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
    except subprocess.CalledProcessError:
        logging.error("gateway_mfr exited with a non-zero status")
        return False

    try:
        return json.loads(run_gateway_mfr_keys.stdout)
    except json.JSONDecodeError:
        logging.error("Unable to parse JSON from gateway_mfr")
    return False


def get_ethernet_addresses(diagnostics):
    # Get Ethernet and WiFi MAC

    # The order of the values in the lists is important!
    # It determines which value will be available for which key
    path_to_files = [
        "/sys/class/net/eth0/address",
        "/sys/class/net/wlan0/address"
    ]
    keys = ["E0", "W0"]
    for (path, key) in zip(path_to_files, keys):
        if not os.path.isfile(path):
            diagnostics[key] = False
            logging.error("{} doesn't exist".format(path))
            break
        try:
            read_file = open(path)
            diagnostics[key] = read_file.readline().strip().upper()
        except PermissionError as e:
            diagnostics[key] = False
            logging.error(e)
