import unittest
from unittest.mock import patch
from hm_pyhelper.miner_param import provision_key
from hm_pyhelper.miner_param import \
        did_gateway_mfr_test_result_include_miner_key_pass

ALL_PASS_GATEWAY_MFR_TESTS = [
    {
        "output": "ok",
        "result": "pass",
        "test": "serial"
    },
    {
        "output": "ok",
        "result": "pass",
        "test": "zone_locked(data)"
    },
    {
        "output": "ok",
        "result": "pass",
        "test": "zone_locked(config)"
    },
    {
        "output": "ok",
        "result": "pass",
        "test": "slot_config(0..=15, ecc)"
    },
    {
        "output": "ok",
        "result": "pass",
        "test": "key_config(0..=15, ecc)"
    },
    {
        "output": "ok",
        "result": "pass",
        "test": "miner_key(0)"
    }
]

NONE_PASS_GATEWAY_MFR_TESTS = [
    {
        "output": "timeout/retry error",
        "result": "fail",
        "test": "serial"
    },
    {
        "output": "timeout/retry error",
        "result": "fail",
        "test": "zone_locked(data)"
    },
    {
        "output": "timeout/retry error",
        "result": "fail",
        "test": "zone_locked(config)"
    },
    {
        "output": "timeout/retry error",
        "result": "fail",
        "test": "slot_config(0..=15, ecc)"
    },
    {
        "output": "timeout/retry error",
        "result": "fail",
        "test": "key_config(0..=15, ecc)"
    },
    {
        "output": "timeout/retry error",
        "result": "fail",
        "test": "miner_key(0)"
    }
  ]


class GatewayMfrProvisionMock:
    def stdout():
        return "example"


class TestMinerParam(unittest.TestCase):

    @patch(
            'hm_pyhelper.miner_param.get_gateway_mfr_test_result',
            return_value={
                "result": "pass",
                "tests": ALL_PASS_GATEWAY_MFR_TESTS
                }
    )
    def test_provision_key_all_passed(self, get_gateway_mfr_test_result):
        self.assertTrue(provision_key())

    @patch('subprocess.run', return_value=GatewayMfrProvisionMock())
    @patch(
            'hm_pyhelper.miner_param.get_gateway_mfr_test_result',
            return_value={
                "result": "fail",
                "tests": NONE_PASS_GATEWAY_MFR_TESTS
            }
    )
    def test_provision_key_none_passed(
            self,
            get_gateway_mfr_test_result,
            subprocess_run
    ):
        self.assertTrue(provision_key())

    @patch(
            'hm_pyhelper.miner_param.get_gateway_mfr_test_result',
            return_value={
                "result": "fail",
                "tests": NONE_PASS_GATEWAY_MFR_TESTS
            }
    )
    def test_did_gateway_mfr_test_result_include_miner_key_fail(
            self,
            get_gateway_mfr_test_result
    ):
        self.assertFalse(
                did_gateway_mfr_test_result_include_miner_key_pass(
                    get_gateway_mfr_test_result
                    )
        )

    def test_did_gateway_mfr_test_result_include_miner_key_pass(self):
        get_gateway_mfr_test_result = {
            "result": "fail",
            "tests": [
                {
                    "output": "timeout/retry error",
                    "result": "fail",
                    "test": "serial"
                },
                {
                    "output": "timeout/retry error",
                    "result": "fail",
                    "test": "zone_locked(data)"
                },
                {
                    "output": "timeout/retry error",
                    "result": "fail",
                    "test": "zone_locked(config)"
                },
                {
                    "output": "timeout/retry error",
                    "result": "fail",
                    "test": "slot_config(0..=15, ecc)"
                },
                {
                    "output": "timeout/retry error",
                    "result": "fail",
                    "test": "key_config(0..=15, ecc)"
                },
                {
                    "output": "ok",
                    "result": "pass",
                    "test": "miner_key(0)"
                }
            ]
        }
        self.assertTrue(
                did_gateway_mfr_test_result_include_miner_key_pass(
                    get_gateway_mfr_test_result
                    )
        )
