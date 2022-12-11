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

BALENA_MODELS = {
    DeviceVendorID.ROCK_PI: BALENA_ENV_ROCKPI_MODELS,
    DeviceVendorID.RASPBERRY_PI: BALENA_ENV_RASPBERRY_PI_MODELS
}


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
    elif dev_model.lower().find('rock') >= 0:
        sbc_info = SBCInfo(vendor_id=DeviceVendorID.ROCK_PI,
                           vendor_name='Radxa Rock Pi',
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
