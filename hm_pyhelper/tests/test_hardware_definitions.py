from unittest import TestCase

from hm_pyhelper.hardware_definitions import variant_definitions


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
            'IC_IDS'
        }

        for variant_name, variant_dict in variant_definitions.items():
            variant_keys = variant_dict.keys()
            missing_keys = expected_fields.difference(variant_keys)
            self.assertSetEqual(missing_keys, set())
