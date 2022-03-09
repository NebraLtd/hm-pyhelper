import os
import pytest
from unittest import TestCase
from unittest.mock import patch, mock_open

from hm_pyhelper.exceptions import UnknownVariantException, \
    UnknownVariantAttributeException

from hm_pyhelper.hardware_definitions import is_rockpi, variant_definitions, \
    get_variant_attribute, is_raspberry_pi
from hm_pyhelper.sbc import BALENA_ENV_RASPBERRY_PI_MODELS, \
    BALENA_ENV_ROCKPI_MODELS

BUILTINS_OPEN_LITERAL = "builtins.open"


class TestHardwareDefinitions(TestCase):
    def test_variant_definitions(self):
        # Not currently expecting APPNAME, GPIO_PIN_LED, or PIO_PIN_BUTTON
        expected_fields = {
            'FRIENDLY',
            'SPIBUS',
            'RESET',
            'MAC',
            'STATUS',
            'BUTTON',
            'ECCOB',
            'TYPE',
            'CELLULAR',
            'FCC_IDS',
            'CONTAINS_FCC_IDS',
            'IC_IDS',
            'CONTAINS_IC_IDS'
        }

        for variant_name, variant_dict in variant_definitions.items():
            variant_keys = variant_dict.keys()
            missing_keys = expected_fields.difference(variant_keys)
            self.assertSetEqual(missing_keys, set())

    mock_variant_definitions = {
        'NEBHNT-XYZ': {
            'FRIENDLY': 'XYZ Hotspot Gen 1',
            'APPNAME': 'APPNAMEXYZ',
            'SPIBUS': 'spidevX.Y',
            'KEY_STORAGE_BUS': '/dev/i2c-X',
            'RESET': 00,
            'MAC': 'ethXYZ',
            'STATUS': 00,
            'BUTTON': 00,
            'ECCOB': True,
            'TYPE': 'TYPEXYZ',
            'CELLULAR': False,
            'FCC_IDS': ['1'],
            'CONTAINS_FCC_IDS': ['2', '3'],
            'IC_IDS': ['4'],
            'CONTAINS_IC_IDS': []
        }
    }

    @patch('hm_pyhelper.hardware_definitions.variant_definitions',
           mock_variant_definitions)
    def test_get_variant_attribute(self):
        mock_variant = self.mock_variant_definitions['NEBHNT-XYZ']
        mock_variant_items = mock_variant.items()
        for attribute_name, attribute_val in mock_variant_items:
            returned_val = get_variant_attribute('NEBHNT-XYZ', attribute_name)
            self.assertEqual(returned_val, attribute_val)

    @patch('hm_pyhelper.hardware_definitions.variant_definitions',
           mock_variant_definitions)
    def test_get_variant_attribute_unknown_variant(self):
        with pytest.raises(UnknownVariantException):
            get_variant_attribute('Nonexistant', 'FRIENDLY')

    @patch('hm_pyhelper.hardware_definitions.variant_definitions',
           mock_variant_definitions)
    def test_get_variant_attribute_unknown_attribute(self):
        with pytest.raises(UnknownVariantAttributeException):
            get_variant_attribute('NEBHNT-XYZ', 'Nonexistant')

    # raspberry pi model names picked from pi kernel sources
    # https://github.com/raspberrypi/linux
    # grep -ir "raspberry" linux/arch/arm*  | grep "model ="  | cut -d "=" -f2
    mock_known_dts_pi_models = [
        "Raspberry Pi Model B+",
        "Raspberry Pi Model B",
        "Raspberry Pi Compute Module",
        "Raspberry Pi Zero",
        "Raspberry Pi 2 Model B rev 1.2",
        "Raspberry Pi Compute Module 3",
        "Raspberry Pi Zero 2 W",
        "Raspberry Pi 4 Model B",
        "Raspberry Pi 400",
        "Raspberry Pi Compute Module 4",
        "Raspberry Pi Compute Module 4S",
        "Raspberry Pi Model A+",
        "Raspberry Pi Model A",
        "Raspberry Pi Model B rev2",
        "Raspberry Pi Compute Module IO board rev1",
        "Raspberry Pi Zero W",
        "Raspberry Pi 2 Model B",
        "Raspberry Pi 3 Model A+",
        "Raspberry Pi 3 Model B+",
        "Raspberry Pi 3 Model B",
        "Raspberry Pi Compute Module 3 IO board V3.0"
    ]

    def test_is_raspberry_pi(self):
        for model in self.mock_known_dts_pi_models:
            with patch(BUILTINS_OPEN_LITERAL, new_callable=mock_open, read_data=model):
                self.assertTrue(is_raspberry_pi())
            with patch(BUILTINS_OPEN_LITERAL, new_callable=mock_open, read_data="Rock something"):
                self.assertFalse(is_raspberry_pi())

        # test balena env based detection
        for model in BALENA_ENV_RASPBERRY_PI_MODELS:
            with patch.dict(os.environ, {'BALENA_DEVICE_TYPE': model}):
                self.assertTrue(is_raspberry_pi())
            # in absence of the env, it should look for /proc/device-tree/model
            # which will not exist on test environment.
            with self.assertRaises(FileNotFoundError):
                self.assertFalse(is_raspberry_pi())

    mock_known_rock_dts_models = ["ROCK PI 4B"]

    def test_is_rock_pi(self):
        for model in self.mock_known_rock_dts_models:
            with patch(BUILTINS_OPEN_LITERAL, new_callable=mock_open, read_data=model):
                self.assertTrue(is_rockpi())
            with patch(BUILTINS_OPEN_LITERAL, new_callable=mock_open,
                       read_data="raspberry something"):
                self.assertFalse(is_rockpi())

        # test balena env based detection
        for model in BALENA_ENV_ROCKPI_MODELS:
            with patch.dict(os.environ, {'BALENA_DEVICE_TYPE': model}):
                self.assertTrue(is_rockpi())
            # in absence of the env, it should look for /proc/device-tree/model
            # which will not exist on test environment.
            with self.assertRaises(FileNotFoundError):
                self.assertFalse(is_rockpi())
