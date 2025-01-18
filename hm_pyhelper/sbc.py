"""
This module provides a set of functions to extract information about
the Single Board Computer in use.
It considers Balena environment variables as primary source of truth.
It also uses the device tree to extract information about the SBC.
"""

import os
from enum import Enum, auto
from collections import namedtuple

SBCInfo = namedtuple('SBCInfo', ['vendor_id', 'vendor_name', 'model_name'])


class DeviceVendorID(Enum):
    """
    Enum for device vendors.
    """
    INVALID = auto()
    ROCK_PI = auto()
    RASPBERRY_PI = auto()
    BOBCAT_PX30 = auto()
    BOBCAT_RK3566 = auto()
    LINXDOT_RK3566 = auto()


# Pulled from
# https://www.balena.io/docs/reference/base-images/devicetypes/
BALENA_ENV_RASPBERRY_PI_MODELS = [
    'raspberry-pi',
    'raspberry-pi2',
    'raspberrypi3',
    'raspberrypi3-64',
    'raspberrypi4-64',
    'nebra-hnt',
    'raspberrypicm4-ioboard',
    'raspberrypi0-2w-64'
]

BALENA_ENV_ROCKPI_MODELS = ['rockpi-4b-rk3399']

BALENA_ENV_BOBCATPX30_MODELS = ['isg-503']

BALENA_ENV_BOBCATRK3566_MODELS = ['rockpro64']

BALENA_ENV_LINXDOTRK3566_MODELS = ['nanopc-t4']

BALENA_MODELS = {
    DeviceVendorID.BOBCAT_PX30: BALENA_ENV_BOBCATPX30_MODELS,
    DeviceVendorID.BOBCAT_RK3566: BALENA_ENV_BOBCATRK3566_MODELS,
    DeviceVendorID.LINXDOT_RK3566: BALENA_ENV_LINXDOTRK3566_MODELS,
    DeviceVendorID.ROCK_PI: BALENA_ENV_ROCKPI_MODELS,
    DeviceVendorID.RASPBERRY_PI: BALENA_ENV_RASPBERRY_PI_MODELS
}

COMMERCIAL_FLEETS = [
    156,  # Bobcat PX30
    161,  # Bobcat RK3566
    56,  # Controllino
    106,  # COTX
    53,  # Finestra
    31,  # Nebra Indoor 868MHz
    40,  # Nebra Indoor RockPi 868MHz
    119,  # Nebra Indoor 915MHz
    58,  # Nebra Indoor RockPi 915MHz
    62,  # Linxdot
    42,  # Linxdot RKCM3
    143,  # Midas
    145,  # Nebra indoor1
    147,  # Nebra indoor2
    148,  # Nebra outdoor1
    149,  # Nebra outdoor2
    52,  # Helium OG
    80,  # Nebra Outdoor 868MHz
    107,  # Nebra Outdoor 915MHz
    47,  # PantherX
    66,  # Pisces
    73,  # Pycom
    88,  # RAK
    114,  # RisingHF
    124,  # Sensecap
    90,  # Syncrobit
    126,  # Syncrobit RKCM3
    98,  # Nebra Indoor Testing
    158,  # Bobcat PX30 Testing
    163,  # Bobcat RK3566 Testing
    127,  # Controllino Testing
    87,  # COTX Testing
    76,  # Finestra Testing
    132,  # Linxdot Testing
    84,  # Linxdot RKCM3 Testing
    144,  # Midas Testing
    128,  # Helium OG Testing
    41,  # PantherX Testing
    43,  # Pisces Testing
    116,  # Pycom Testing
    113,  # RAK Testing
    103,  # RisingHF Testing
    60,  # Nebra RockPi Testing
    137,  # Sensecap Testing
    57,  # Syncrobit Testing
    111,  # Syncrobit RKCM3 Testing
    2006816,  # Rob Testing
    2061340,  # Rob Testing
    2173105,  # Aaron Testing
]

NON_COMMERCIAL_FLEETS = [
    67,  # dev-1
    54,  # dev-2
    74,  # dev-3
    25,  # devnet-01
    26,  # devnet-02
    150,  # devnet-03
    153,  # dev-sensorhub
    121,  # Bobcat PX30
    160,  # Bobcat RK3566
    105,  # Controllino
    136,  # COTX
    99,  # Disputed
    118,  # Finestra
    109,  # Indoor 470
    39,  # Indoor 868
    134,  # Indoor 868 RockPi
    91,  # Indoor 915
    122,  # Indoor 915 RockPi
    46,  # Linxdot
    68,  # Linxdot RKCM3
    138,  # Midas
    3,  # Indoor1
    27,  # Indoor2
    28,  # Outdoor1
    29,  # Outdoor2
    104,  # OG
    79,  # Outdoor 470
    63,  # Outdoor 868
    133,  # Outdoor 915
    94,  # Outdoor 915 RockPi
    32,  # Panther X1
    71,  # Pisces
    83,  # Pycom
    78,  # RAK
    85,  # RisingHF
    101,  # Sensecap
    130,  # Syncrobit
    69,  # Syncrobit RKCM3
    123,  # Testnet
    157,  # Bobcat PX30 Testnet
    162,  # Bobcat RK3566 Testnet
    102,  # Controllino Testnet
    86,  # COTX Testnet
    77,  # Finestra Testnet
    117,  # Linxdot Testnet
    110,  # Linxdot RKCM3 Testnet
    139,  # Midas Testnet
    70,  # OG Testnet
    129,  # Panther X1 Testnet
    125,  # Pisces Testnet
    131,  # Pycom Testnet
    36,  # RAK Testnet
    55,  # Rising HF Testnet
    95,  # RockPi Testnet
    75,  # Sensecap Testnet
    97,  # Syncrobit Testnet
    37,  # Syncrobit RKCM3 Testnet
    22,  # Indoor2 Testnet
]

NEBRA_API_URL = "https://api.cloud.nebra.com"

def device_model():
    with open('/proc/device-tree/model', 'r') as f:
        return f.readline().strip()


def sbc_info() -> SBCInfo:
    '''
    return SBCInfo formed by reading '/proc/device-tree/model'
    '''
    sbc_info = SBCInfo(vendor_id=DeviceVendorID.INVALID, vendor_name='', model_name='')
    dev_model = device_model()
    if dev_model.lower().find('raspberry') >= 0:
        sbc_info = SBCInfo(vendor_id=DeviceVendorID.RASPBERRY_PI,
                           vendor_name='Raspberry Pi',
                           model_name=dev_model)
    elif dev_model.lower().find('rk3566 evb2') >= 0:
        sbc_info = SBCInfo(vendor_id=DeviceVendorID.BOBCAT_RK3566,
                           vendor_name='Bobcat',
                           model_name=dev_model)
    elif dev_model.lower().find('rk3566 r01') >= 0:
        sbc_info = SBCInfo(vendor_id=DeviceVendorID.LINXDOT_RK3566,
                           vendor_name='Linxdot',
                           model_name=dev_model)
    elif dev_model.lower().find('rock') >= 0:
        sbc_info = SBCInfo(vendor_id=DeviceVendorID.ROCK_PI,
                           vendor_name='Radxa Rock Pi',
                           model_name=dev_model)
    elif dev_model.lower().find('px30') >= 0:
        sbc_info = SBCInfo(vendor_id=DeviceVendorID.BOBCAT_PX30,
                           vendor_name='Bobcat',
                           model_name=dev_model)
    return sbc_info


def is_sbc_type(device_id: DeviceVendorID) -> bool:
    '''
    Return true if the sbc matches the type supplied.
    '''
    device_type = os.getenv('BALENA_DEVICE_TYPE')

    # use device tree supplied model name if evn not set
    if not device_type:
        return sbc_info().vendor_id == device_id

    # honor env override
    return device_type in BALENA_MODELS.get(device_id, [])


def is_commercial_fleet() -> bool:
    '''
    Return true if the device is in a commercial fleet. Otherwise return false.
    '''
    # all fleets will get commercial software
    # fleet_name = os.environ.get('BALENA_APP_NAME')
    # fleet_id = int(os.environ.get('BALENA_APP_ID'))

    # if not fleet_name.endswith('-c') or fleet_id not in COMMERCIAL_FLEETS:
    #     return False

    return True


def is_nebra_fleet() -> bool:
    '''
    Return true if the device is in a Nebra Cloud fleet. Otherwise return false.
    '''
    api_url = os.environ.get('BALENA_API_URL')
    fleet_id = int(os.environ.get('BALENA_APP_ID'))

    if (api_url != NEBRA_API_URL) or (fleet_id not in COMMERCIAL_FLEETS and fleet_id not in NON_COMMERCIAL_FLEETS):
        return False

    return True
