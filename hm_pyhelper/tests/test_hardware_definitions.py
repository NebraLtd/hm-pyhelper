import pytest
from unittest import TestCase
from unittest.mock import patch

from hm_pyhelper.exceptions import UnknownVariantException, \
                                   UnknownVariantAttributeException

from hm_pyhelper.hardware_definitions import variant_definitions, \
                                            get_variant_attribute


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
