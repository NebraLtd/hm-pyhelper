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
            DIAGNOSTICS_ERRORS_KEY: ['key'],
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
        diagnostic1 = Diagnostic('key1', 'friendly_name')
        diagnostic2 = Diagnostic('key2', 'friendly_name')
        diagnostics_report = DiagnosticsReport()
        diagnostics_report.record_failure('Error1', diagnostic1)
        diagnostics_report.record_failure('Error2', diagnostic2)

        actual_msgs = diagnostics_report.get_error_messages()
        expected_msgs = "key1 Error: Error1\nkey2 Error: Error2"
        self.assertEqual(actual_msgs, expected_msgs)

    def test_get_report_subset(self):
        diagnostics_report = DiagnosticsReport()
        diagnostics_report['VA'] = 'NEBHNT-IN1'
        diagnostics_report['foo'] = 'bar'

        self.assertDictEqual(diagnostics_report.get_report_subset(["VA"]), {
            'VA': 'NEBHNT-IN1'
        })
