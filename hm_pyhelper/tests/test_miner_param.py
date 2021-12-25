from hm_pyhelper.exceptions import ECCMalfunctionException, \
    MinerFailedToFetchMacAddress
from hm_pyhelper.lock_singleton import ResourceBusyError
from hm_pyhelper.miner_param import get_gateway_mfr_test_result, \
    retry_get_region, await_spi_available, \
    provision_key, run_gateway_mfr, \
    did_gateway_mfr_test_result_include_miner_key_pass, \
    get_mac_address
import unittest
from unittest.mock import mock_open, patch
import pytest

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

mock_variant_definitions = {
        'NEBHNT-WITHKSB': {
            'KEY_STORAGE_BUS': '/dev/i2c-X',
        },
        'NEBHNT-NOKSB': {
            'NO_KEY_STORAGE_BUS': '/dev/i2c-X',
        }
    }


class GatewayMfrProvisionMock:
    stderr = "example error"

    stdout = """{
          "provision": "example"
        }"""


@patch.dict('os.environ', {"VARIANT": "NEBHNT-WITHKSB"})
@patch('hm_pyhelper.hardware_definitions.variant_definitions',
       mock_variant_definitions)
class TestMinerParam(unittest.TestCase):
    @patch('subprocess.run', return_value=GatewayMfrProvisionMock())
    def test_run_gateway_mfr(self, subprocess_run):
        run_gateway_mfr(["unittest"])
        self.assertEqual(
            subprocess_run.call_args[0][0][1:], [
                "--path",
                mock_variant_definitions['NEBHNT-WITHKSB']['KEY_STORAGE_BUS'],
                "unittest"
            ]
        )

    @patch.dict('os.environ', {"VARIANT": "NEBHNT-NOKSB"})
    @patch('subprocess.run', return_value=GatewayMfrProvisionMock())
    def test_run_gateway_mfr_no_ksb_attribute(self, subprocess_run):
        run_gateway_mfr(["unittest"])
        self.assertEqual(
            subprocess_run.call_args[0][0][1:], ["unittest"]
        )

    @patch.dict('os.environ', {"VARIANT": "NEBHNT-INVALID"})
    @patch('subprocess.run', return_value=GatewayMfrProvisionMock())
    def test_run_gateway_mfr_no_variant(self, subprocess_run):
        run_gateway_mfr(["unittest"])
        self.assertEqual(
            subprocess_run.call_args[0][0][1:], ["unittest"]
        )

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

    def test_get_region_from_override(self):
        self.assertEqual(retry_get_region("foo", "bar/"), 'foo')

    @patch("builtins.open", new_callable=mock_open, read_data="ZZ111\n")
    def test_get_region_from_miner(self, _):
        self.assertEqual(retry_get_region(False, "foo/"), 'ZZ111')  # noqa: E501

    @patch("os.path.exists", return_value=True)
    def test_is_spi_available(self, _):
        self.assertTrue(await_spi_available("spiXY.Z"))

    def test_error_mac_address(self):
        with pytest.raises(MinerFailedToFetchMacAddress):
            get_mac_address("test/path")

    @patch(
      'hm_pyhelper.miner_param.run_gateway_mfr',
      side_effect=FileNotFoundError("File Not Found Error"))
    def test_filenotfound_exception(self, mock):
        with pytest.raises(FileNotFoundError):
            get_gateway_mfr_test_result()

    @patch(
      'hm_pyhelper.miner_param.run_gateway_mfr',
      side_effect=ECCMalfunctionException("File Not Found Error"))
    def test_eccmalfunction_exception(self, mock):
        with pytest.raises(ECCMalfunctionException):
            get_gateway_mfr_test_result()

    @patch(
      'hm_pyhelper.miner_param.run_gateway_mfr',
      side_effect=ResourceBusyError("Resource Busy Error"))
    def test_resourcebusy_exception(self, mock):
        with pytest.raises(ResourceBusyError):
            get_gateway_mfr_test_result()
