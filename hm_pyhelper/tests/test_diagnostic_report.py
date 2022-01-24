import unittest
import json

from hm_pyhelper.diagnostics import Diagnostic, DiagnosticsReport
from hm_pyhelper.diagnostics.diagnostics_report import \
                                    DIAGNOSTICS_PASSED_KEY, \
                                    DIAGNOSTICS_ERRORS_KEY


class TestDiagnostic(unittest.TestCase):
    def test_record_result(self):
        diagnostic = Diagnostic('key', 'friendly_name')
        diagnostics_report = DiagnosticsReport()
        diagnostics_report.record_result('foo', diagnostic)

        self.assertDictEqual(diagnostics_report, {
            DIAGNOSTICS_PASSED_KEY: False,
            DIAGNOSTICS_ERRORS_KEY: [],
            'key': 'foo',
            'friendly_name': 'foo'
        })

    def test_record_failure(self):
        diagnostic = Diagnostic('key', 'friendly_name')
        diagnostics_report = DiagnosticsReport()
        diagnostics_report.record_failure('foo', diagnostic)
        self.assertDictEqual(diagnostics_report, {
            DIAGNOSTICS_PASSED_KEY: False,
            DIAGNOSTICS_ERRORS_KEY: ['key', 'friendly_name'],
            'key': 'foo',
            'friendly_name': 'foo'
        })

    def test_deserialization(self):
        report_str = '{"diagnostics_passed": false, "errors": ["ECC"], "ECC": false, "foo": "bar"}'  # noqa E501
        report_dict = json.loads(report_str)
        diagnostics_report = DiagnosticsReport(**report_dict)

        self.assertDictEqual(diagnostics_report, {
            DIAGNOSTICS_PASSED_KEY: False,
            DIAGNOSTICS_ERRORS_KEY: ['ECC'],
            'ECC': False,
            'foo': 'bar'
        })

    def test_get_error_messages(self):
        diagnostic1 = Diagnostic('key1', 'friendly_name1')
        diagnostic2 = Diagnostic('key2', 'friendly_name2')
        diagnostics_report = DiagnosticsReport()
        diagnostics_report.record_failure('Error1', diagnostic1)
        diagnostics_report.record_failure('Error2', diagnostic2)

        actual_msgs = diagnostics_report.get_error_messages()
        expected_msgs = "key1 Error: Error1\nfriendly_name1 Error: Error1" + \
            "\nkey2 Error: Error2\nfriendly_name2 Error: Error2"
        self.assertEqual(actual_msgs, expected_msgs)

    def test_get_report_subset(self):
        diagnostics_report = DiagnosticsReport()
        diagnostics_report['VA'] = 'NEBHNT-IN1'
        diagnostics_report['foo'] = 'bar'

        self.assertDictEqual(diagnostics_report.get_report_subset(["VA"]), {
            'VA': 'NEBHNT-IN1'
        })

    def test_passed_success(self):
        report = DiagnosticsReport()
        report[DIAGNOSTICS_PASSED_KEY] = True

        self.assertTrue(report.passed())

    def test_passed_false_on_errors(self):
        keys_to_test = {
            'ECC', 'onboarding_key', 'eth_mac_address', 'wifi_mac_address',
            'public_key', 'bluetooth', 'VARIANT', 'FREQ', 'serial_number'
        }

        response = {
            'diagnostics_passed': False,
            'errors': ['ECC', 'BN', 'OK', 'PK', 'PF'],
            'serial_number': '0000000021aabbcc',
            'ECC': 'gateway_mfr test finished with error',
            'E0': 'F0:4C:D5:58:E0:E1',
            'eth_mac_address': 'F0:4C:D5:58:E0:E1',
            'FR': '915',
            'FREQ': '915',
            'FW': '2021.11.22.0-1',
            'FIRMWARE_VERSION': '2021.11.22.0-1',
            'VA': 'NEBHNT-OUT1',
            'VARIANT': 'NEBHNT-OUT1',
            'BT': True,
            'bluetooth': True,
            'LTE': False,
            'LOR': False,
            'lora': False,
            'OK': 'gateway_mfr exited with a non-zero status',
            'onboarding_key': 'gateway_mfr exited with a non-zero status',
            'PK': 'gateway_mfr exited with a non-zero status',
            'public_key': 'gateway_mfr exited with a non-zero status',
            'PF': False,
            'legacy_pass_fail': False
        }

        for key in keys_to_test:
            response['errors'] = [key]
            report = DiagnosticsReport.from_json_dict(response)
            self.assertFalse(report.passed())
            assert report.has_errors([key]) == {key}

        response['errors'] = set(keys_to_test)
        report = DiagnosticsReport.from_json_dict(response)
        self.assertFalse(report.passed())
        assert report.has_errors(keys_to_test) == keys_to_test

    def test_assert_diagnostics_present(self):
        diagnostics_report = DiagnosticsReport.from_json_dict({
            'foo': 'bar'
        })

        missing_keys = diagnostics_report.get_missing_keys({'foo'})

        self.assertEqual(missing_keys, set())

    def test_assert_diagnostics_not_present(self):
        diagnostics_report = DiagnosticsReport.from_json_dict({
            'foo': 'bar'
        })

        missing_keys = diagnostics_report.get_missing_keys({'missing_key'})
        self.assertEqual(missing_keys, {'missing_key'})
