import hm_pyhelper.sbc as sbc
from hm_pyhelper.exceptions import UnknownVariantException, \
    UnknownVariantAttributeException


def is_bobcat_px30() -> bool:
    return sbc.is_sbc_type(sbc.DeviceVendorID.BOBCAT_PX30)


def is_bobcat_rk3566() -> bool:
    return sbc.is_sbc_type(sbc.DeviceVendorID.BOBCAT_RK3566)


def is_rockpi() -> bool:
    return sbc.is_sbc_type(sbc.DeviceVendorID.ROCK_PI)


def is_raspberry_pi() -> bool:
    return sbc.is_sbc_type(sbc.DeviceVendorID.RASPBERRY_PI)


# The variant name is determined by following rules:
# - Format : <vendor>-<model>
# - All lower case.
# - Models are named fl1,fl2...fln, based on release chronology.
# - Any new models should be added to the end of the list and follow this naming convention.
# - Three are some names here that don't follow this convention.
#   These historical names are all capital letters and we don't consider them in use.
variant_definitions = {
    # Nebra Indoor Hotspot Gen1
    'nebra-indoor1': {
        'FRIENDLY': 'Nebra Indoor Hotspot Gen 1',
        'SUPPORTED_MODELS': ['Nebra Indoor Hotspot Gen 1'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypi3-64'],
        'SPIBUS': 'spidev1.2',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 38,
        'MAC': 'eth0',
        'STATUS': 25,
        'BUTTON': 26,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': ['2AZDM-HNTIN'],
        'CONTAINS_FCC_IDS': ['2AHRD-EPN8531', '2AB8JCSR40', '2ARPP-GL5712UX'],
        'IC_IDS': ['27187-HNTIN'],
        'CONTAINS_IC_IDS': []
        },

    # Nebra Outdoor Hotspot Gen1
    'nebra-outdoor1': {
        'FRIENDLY': 'Nebra Outdoor Hotspot Gen 1',
        'SUPPORTED_MODELS': ['Nebra Outdoor Hotspot Gen 1'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypi3-64'],
        'SPIBUS': 'spidev1.2',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 38,
        'MAC': 'eth0',
        'STATUS': 25,
        'BUTTON': 24,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': True,
        'FCC_IDS': ['2AZDM-HNTOUT'],
        'CONTAINS_FCC_IDS': ['2ARPP-GL5712UX', '2AZDM-CSR8510',
                             'XMR201903EG25G', '2AZDM-WIFIRP'],
        'IC_IDS': ['27187-HNTOUT'],
        'CONTAINS_IC_IDS': []
        },

    # Nebra Outdoor Hotspot Gen2
    # Note:: assuming outdoor2 is equivalent to indoor2
    'nebra-outdoor2': {
        'FRIENDLY': 'Nebra ROCK Pi 4 Outdoor',
        'SUPPORTED_MODELS': ['Nebra ROCK Pi 4 Outdoor'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['rockpi-4b-rk3399'],
        'SPIBUS': 'spidev32766.0',
        'SWARM_KEY_URI': ['ecc://i2c-7:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-7:96?slot=0'],
        'RESET': 149,
        'MAC': 'eth0',
        'STATUS': 156,
        'BUTTON': 154,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': True,
        'GPIO_PIN_LED': 18,
        'GPIO_PIN_BUTTON': 16,
        'FCC_IDS': ['2AZDM-HHRK4-OUT'],
        'CONTAINS_FCC_IDS': ['2ARPP-GL5712UX',
                             '2A3PA-ROCKPI4',
                             'XMR201903EG25G'],
        'IC_IDS': ['27187-HHRK4-OUT'],
        'CONTAINS_IC_IDS': []
        },

    # Nebra Pi 0 Light Hotspot SPI Ethernet
    'nebra-light1': {
        'FRIENDLY': 'Nebra Pi 0 Light Hotspot SE',
        'SUPPORTED_MODELS': ['Nebra Pi 0 Light Hotspot SE'],
        'CPU_ARCH': 'armv6hf',
        'BALENA_DEVICE_TYPE': ['raspberry-pi'],
        'SPIBUS': 'spidev1.2',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 22,
        'MAC': 'wlan0',
        'STATUS': 24,
        'BUTTON': 23,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': ['2AZDM-HNTLGTMC'],
        'CONTAINS_FCC_IDS': ['2ABCB-RPI0W', '2ARPP-GL5712UX'],
        'IC_IDS': ['27187-HNTLGTMC'],
        'CONTAINS_IC_IDS': ['20953-RPI0W']
        },

    # Nebra Pi 0 Light Hotspot USB Ethernet
    'NEBHNT-LGT-ZX': {
        'FRIENDLY': 'Nebra Pi 0 Light Hotspot XE',
        'SUPPORTED_MODELS': ['Nebra Pi 0 Light Hotspot XE'],
        'CPU_ARCH': 'armv6hf',
        'BALENA_DEVICE_TYPE': ['raspberry-pi'],
        'SPIBUS': 'spidev1.2',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 22,
        'MAC': 'wlan0',
        'STATUS': 24,
        'BUTTON': 23,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Nebra Radxa Zero Light Hotspot II SPI Ethernet
    'nebra-light2': {
        'FRIENDLY': 'Nebra Radxa Zero Light Hotspot II SE',
        'SUPPORTED_MODELS': ['Nebra Radxa Zero Light Hotspot II SE'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['radxa-zero'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-3:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-3:96?slot=0'],
        'RESET': 415,
        'MAC': 'wlan0',
        'STATUS': 421,
        'BUTTON': 416,
        'ECCOB': True,
        'TYPE': 'Light',
        'CELLULAR': False,
        'FCC_IDS': ['2AZDM-HNTLGTMC-RADXA'],
        'CONTAINS_FCC_IDS': ['2A3PA-RADXA-ZERO', '2ARPP-GL5712UX'],
        'IC_IDS': ['27187-HNTLGTMC-RADXA'],
        'CONTAINS_IC_IDS': []
        },

    # Nebra Raspberry Pi Zero Light Hotspot II SPI Ethernet
    'nebra-light3': {
        'FRIENDLY': 'Nebra Raspberry Pi Zero Light Hotspot II SE',
        'SUPPORTED_MODELS': ['Nebra Raspberry Pi Zero Light Hotspot II SE'],
        'CPU_ARCH': 'armv6hf',
        'BALENA_DEVICE_TYPE': ['raspberry-pi'],
        'SPIBUS': 'spidev1.2',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 4,
        'MAC': 'wlan0',
        'STATUS': 26,
        'BUTTON': 12,
        'ECCOB': True,
        'TYPE': 'Light',
        'CELLULAR': False,
        'FCC_IDS': ['2AZDM-HNTLGTMC'],
        'CONTAINS_FCC_IDS': ['2ABCB-RPI0W', '2ARPP-GL5712UX'],
        'IC_IDS': ['27187-HNTLGTMC'],
        'CONTAINS_IC_IDS': ['20953-RPI0W']
        },

    # Nebra Beaglebone Light Hotspot
    'NEBHNT-BBB': {
        'FRIENDLY': 'Nebra Beaglebone Light Hotspot',
        'SUPPORTED_MODELS': ['Nebra Beaglebone Light Hotspot'],
        'CPU_ARCH': 'armv7hf',
        'BALENA_DEVICE_TYPE': ['beaglebone-black'],
        'SPIBUS': 'spidev1.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 60,
        'MAC': 'eth0',
        'STATUS': 31,
        'BUTTON': 30,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Nebra Pocket Beagle Light Hotspot
    'NEBHNT-PBB': {
        'FRIENDLY': 'Nebra Pocket Beagle Light Hotspot',
        'SUPPORTED_MODELS': ['Nebra Pocket Beagle Light Hotspot'],
        'CPU_ARCH': 'armv7hf',
        'BALENA_DEVICE_TYPE': ['beaglebone-pocket'],
        'SPIBUS': 'spidev1.2',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 60,
        'MAC': 'wlan0',
        'STATUS': 31,
        'BUTTON': 30,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Nebra Hotspot HAT ROCK Pi 4 Indoor
    'nebra-indoor2': {
        'FRIENDLY': 'Nebra ROCK Pi 4 Indoor',
        'SUPPORTED_MODELS': ['Nebra ROCK Pi 4 Indoor'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['rockpi-4b-rk3399'],
        'SPIBUS': 'spidev32766.0',
        'SWARM_KEY_URI': ['ecc://i2c-7:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-7:96?slot=0'],
        'RESET': 149,
        'MAC': 'eth0',
        'STATUS': 156,
        'BUTTON': 154,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'GPIO_PIN_LED': 18,
        'GPIO_PIN_BUTTON': 16,
        'FCC_IDS': ['2AZDM-HHRK4'],
        'CONTAINS_FCC_IDS': ['2ARPP-GL5712UX', '2A3PA-ROCKPI4'],
        'IC_IDS': ['27187-HHRK4'],
        'CONTAINS_IC_IDS': []
        },

    # Nebra Hotspot HAT Tinkerboard 1
    'NEBHNT-HHTK': {
        'FRIENDLY': 'Nebra Hotspot HAT Tinkerboard Light',
        'SUPPORTED_MODELS': ['Nebra Hotspot HAT Tinkerboard Light'],
        'CPU_ARCH': 'armv7hf',
        'BALENA_DEVICE_TYPE': ['asus-tinker-board'],
        'SPIBUS': 'spidev2.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 167,
        'MAC': 'eth0',
        'STATUS': 163,
        'BUTTON': 162,
        'ECCOB': True,
        'TYPE': 'Light',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # RAKwireless Hotspot Miner
    'rak-fl1': {
        'FRIENDLY': 'RAK Hotspot',
        'SUPPORTED_MODELS': ['RAK v1.5', 'RAK v2', 'RAK MNTD'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypi4-64'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 25,
        'MAC': 'wlan0',
        'STATUS': 20,
        'BUTTON': 7,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Helium Hotspot
    'helium-fl1': {
        'FRIENDLY': 'Helium Hotspot',
        'SUPPORTED_MODELS': ['Helium Hotspot'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypi3-64', 'raspberrypi4-64'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=15'],
        'RESET': 25,
        'MAC': 'wlan0',
        'STATUS': 20,
        'BUTTON': 7,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # SenseCAP M1 Hotspot
    'sensecap-fl1': {
        'FRIENDLY': 'SenseCAP M1',
        'SUPPORTED_MODELS': ['SenseCAP M1'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypi4-64'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 17,
        'MAC': 'wlan0',
        'STATUS': 22,
        'BUTTON': 27,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Panther X1
    'pantherx1-fl1': {
        'FRIENDLY': 'Panther X1',
        'SUPPORTED_MODELS': ['Panther X1'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypi4-64'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 23,
        'MAC': 'wlan0',
        'STATUS': 22,
        'BUTTON': 21,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Smart Mimic / Mimiq Finestra
    'finestra-fl1': {
        'FRIENDLY': 'Finestra Miner',
        'SUPPORTED_MODELS': ['Finestra Miner'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypi4-64'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 17,
        'MAC': 'wlan0',
        'STATUS_LED': {
            'TYPE': 'RGB',
            'GPIO_NUMBERS_RGB': [20, 26, 7],
            'GPIO_NUMBER_SINGLE': 20
         },
        'STATUS': 20,
        'BUTTON': 16,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Pisces P100 Hotspot
    'pisces-fl1': {
        'FRIENDLY': 'Pisces P100',
        'SUPPORTED_MODELS': ['Pisces P100'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypi4-64'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-0:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-0:96?slot=0'],
        'RESET': 23,
        'MAC': 'eth0',
        'STATUS': 17,
        'BUTTON': 22,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Embit / Controllino / Conelcom
    'controllino-fl1': {
        'FRIENDLY': 'Controllino  (Conelcom) Hotspot',
        'SUPPORTED_MODELS': ['Controllino Hotspot', 'Conelcom Hotspot'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypi4-64'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 4,
        'MAC': 'wlan0',
        'STATUS_LED': {
            'TYPE': 'RGB',
            'GPIO_NUMBERS_RGB': [20, 26, 7],
            'GPIO_NUMBER_SINGLE': 20
         },
        'STATUS': 20,
        'BUTTON': False,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # DIY Pi Supply Hotspot HAT
    'DIY-PISLGH': {
        'FRIENDLY': 'DIY Pi Supply Hotspot HAT',
        'SUPPORTED_MODELS': ['Raspberry Pi DIY Pi Supply Hotspot HAT'],
        'CPU_ARCH': '',
        'BALENA_DEVICE_TYPE': ['raspberry-pi', 'raspberry-pi2',
                               'raspberrypi0-2w-64', 'raspberrypi3-64',
                               'raspberrypi4-64'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 22,
        'MAC': 'eth0',
        'STATUS': 20,
        'BUTTON': 21,
        'ECCOB': False,
        'TYPE': 'Light',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Nebra Indoor Hotspot
    'DIY-RAK2287': {
        'FRIENDLY': 'DIY RAK2247/RAK2287 HAT',
        'SUPPORTED_MODELS': ['Raspberry Pi DIY RAK2247/RAK2287 HAT'],
        'CPU_ARCH': '',
        'BALENA_DEVICE_TYPE': ['raspberry-pi', 'raspberry-pi2',
                               'raspberrypi0-2w-64', 'raspberrypi3-64',
                               'raspberrypi4-64'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 17,
        'MAC': 'eth0',
        'STATUS': 20,
        'BUTTON': 21,
        'ECCOB': False,
        'TYPE': 'Light',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Linxdot CM4
    'linxdot-fl1': {
        'FRIENDLY': 'Linxdot Hotspot',
        'SUPPORTED_MODELS': ['Linxdot Hotspot'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypicm4-ioboard'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 17,
        'MAC': 'wlan0',
        'STATUS': 22,
        'BUTTON': 27,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Linxdot RKCM3
    'linxdot-rk3566-fl1': {
        'FRIENDLY': 'Linxdot RK3566 Hotspot',
        'SUPPORTED_MODELS': ['Linxdot RK3566 Hotspot'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['nanopc-t4'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 17,
        'MAC': 'wlan0',
        'STATUS': 22,
        'BUTTON': 27,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Pycom CM4
    'pycom-fl1': {
        'FRIENDLY': 'Pycom Hotspot',
        'SUPPORTED_MODELS': ['Pycom Hotspot'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypicm4-ioboard'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-10:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-10:96?slot=0'],
        'RESET': 23,
        'MAC': 'wlan0',
        'STATUS': 22,
        'BUTTON': 27,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Syncrobit CM4
    'syncrobit-fl1': {
        'FRIENDLY': 'Syncrobit Hotspot',
        'SUPPORTED_MODELS': ['Syncrobit Hotspot'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypicm4-ioboard'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0', 'ecc://i2c-1:88?slot=2'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0', 'ecc://i2c-1:88?slot=15'],
        'RESET': 17,
        'MAC': 'wlan0',
        'BUTTON': 27,
        'STATUS_NEOPIXEL': {
            'LED_COUNT': 6,
            'PIN': 18,
            'DMA': 10,
            'CHANNEL': 0,
            'ACTIVE_HIGH': True,
        },
        'STATUS': None,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Syncrobit RKCM3
    'syncrobit-rkcm3-fl1': {
        'FRIENDLY': 'Syncrobit RockPi Hotspot',
        'SUPPORTED_MODELS': ['Syncrobit RockPi Hotspot'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['radxa-cm3-rpicm4-ioboard'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0', 'ecc://i2c-1:88?slot=2'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0', 'ecc://i2c-1:88?slot=15'],
        'RESET': 17,
        'MAC': 'wlan0',
        'STATUS': 22,
        'BUTTON': 27,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # COTX X3 Hotspot
    'cotx-fl1': {
        'FRIENDLY': 'COTX X3',
        'SUPPORTED_MODELS': ['COTX X3'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypi4-64'],
        'SPIBUS': 'spidev0.0',  # There is a CSN1 pin which is connected to GPIO6 (HAT Pin 31)
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 22,
        'MAC': 'eth0',
        'STATUS': 21,  # Stub. There is no status LED on X3. I2C-3 is used for display
                       # communication (HAT pins 5,7)
        'BUTTON': 23,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,  # There is a 4G option on the HAT board.
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # RisingHF
    'risinghf-fl1': {
        'FRIENDLY': 'RisingHF Hotspot',
        'SUPPORTED_MODELS': ['RisingHF Hotspot'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypi3-64'],
        'SPIBUS': 'spidev1.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 38,
        'MAC': 'eth0',
        'STATUS': 25,
        'BUTTON': 24,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': True,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Midas CM4
    'midas-fl1': {
        'FRIENDLY': 'Midas Hotspot',
        'SUPPORTED_MODELS': ['Midas Hotspot'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['raspberrypicm4-ioboard'],
        'SPIBUS': 'spidev0.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 17,
        'MAC': 'wlan0',
        'STATUS': 22,
        'BUTTON': 27,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Bobcat PX30 (1GB RAM)
    'bobcat-px30': {
        'FRIENDLY': 'Bobcat PX30 Hotspot (1GB RAM)',
        'SUPPORTED_MODELS': ['Bobcat PX30 Hotspot (1GB RAM)'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['isg-503'],
        'SPIBUS': 'spidev1.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0'],
        'RESET': 104,
        'MAC': 'wlan0',
        'BUTTON': 10,
        'STATUS': 45,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Bobcat RK3566 (2GB RAM)
    'bobcat-rk3566': {
        'FRIENDLY': 'Bobcat RK3566 Hotspot (2GB RAM)',
        'SUPPORTED_MODELS': ['Bobcat RK3566 Hotspot (2GB RAM)'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['rockpro64'],
        'SPIBUS': 'spidev5.0',
        'SWARM_KEY_URI': ['ecc://i2c-5:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-5:96?slot=0'],
        'RESET': 149,
        'MAC': 'wlan0',
        'BUTTON': 6,
        'STATUS': 129,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        },

    # Heltec HT-M2808
    'heltec-fl1': {
        'FRIENDLY': 'Heltec HT-M2808 Hotspot',
        'SUPPORTED_MODELS': ['Heltec HT-M2808'],
        'CPU_ARCH': 'arm64',
        'BALENA_DEVICE_TYPE': ['rockpro64'],
        'SPIBUS': 'spidev32766.0',
        'SWARM_KEY_URI': ['ecc://i2c-1:96?slot=0','ecc://i2c-4:96?slot=0'],
        'ONBOARDING_KEY_URI': ['ecc://i2c-1:96?slot=0','ecc://i2c-4:96?slot=0'],
        'RESET': 2,
        'MAC': 'eth0',
        'STATUS': 85,
        'BUTTON': 83,
        'ECCOB': True,
        'TYPE': 'Full',
        'CELLULAR': False,
        'FCC_IDS': [],
        'CONTAINS_FCC_IDS': [],
        'IC_IDS': [],
        'CONTAINS_IC_IDS': []
        }
}

# Note: Maintain old names for backward compatibility, should be removed at some
# point of time.
variant_definitions['Indoor'] = variant_definitions['nebra-indoor1']
variant_definitions['NEBHNT-IN1'] = variant_definitions['nebra-indoor1']
variant_definitions['NEBHNT-OUT1'] = variant_definitions['nebra-outdoor1']
variant_definitions['Outdoor'] = variant_definitions['nebra-outdoor1']
variant_definitions['NEBHNT-LGT-ZS'] = variant_definitions['nebra-light1']
variant_definitions['NEBHNT-LGT-RADXA'] = variant_definitions['nebra-light2']
variant_definitions['NEBHNT-HHRK4'] = variant_definitions['nebra-indoor2']
variant_definitions['NEBHNT-HHRK4-OUT'] = variant_definitions['nebra-outdoor2']
variant_definitions['COMP-RAKHM'] = variant_definitions['rak-fl1']
variant_definitions['COMP-HELIUM'] = variant_definitions['helium-fl1']
variant_definitions['COMP-SENSECAPM1'] = variant_definitions['sensecap-fl1']
variant_definitions['COMP-PANTHERX1'] = variant_definitions['pantherx1-fl1']
variant_definitions['COMP-FINESTRA'] = variant_definitions['finestra-fl1']
variant_definitions['COMP-PISCESP100'] = variant_definitions['pisces-fl1']
variant_definitions['COMP-COTX3'] = variant_definitions['cotx-fl1']
variant_definitions['COMP-CONTROLLINO'] = variant_definitions['controllino-fl1']
variant_definitions['COMP-LINXDOTCM4'] = variant_definitions['linxdot-fl1']
variant_definitions['COMP-PYCOM'] = variant_definitions['pycom-fl1']
variant_definitions['COMP-SYNCROBITCM4'] = variant_definitions['syncrobit-fl1']
variant_definitions['COMP-MIDAS'] = variant_definitions['midas-fl1']
variant_definitions['COMP-SYNCROBITRKCM3'] = variant_definitions['syncrobit-rkcm3-fl1']
variant_definitions['COMP-LINXDOTRK3566'] = variant_definitions['linxdot-rk3566-fl1']
variant_definitions['COMP-RISINGHF'] = variant_definitions['risinghf-fl1']
variant_definitions['COMP-BOBCATPX30'] = variant_definitions['bobcat-px30']
variant_definitions['COMP-BOBCATRK3566'] = variant_definitions['bobcat-rk3566']


def get_variant_attribute(variant_name, attribute_key):
    """
    Returns the value of an attribute from a specific variant.
    Raises UnknownVariantException and UnknownVariantAttributeException.
    """

    try:
        variant_dict = variant_definitions[variant_name]
    except KeyError:
        raise UnknownVariantException("Variant %s is not recognized."
                                      % variant_name)

    try:
        return variant_dict[attribute_key]
    except KeyError:
        raise UnknownVariantAttributeException("Variant attribute %s"
                                               " is not recognized."
                                               % attribute_key)
