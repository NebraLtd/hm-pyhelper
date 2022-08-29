import json
import unittest
import pytest
from unittest.mock import ANY, mock_open, patch
from packaging.version import Version
from hm_pyhelper.exceptions import ECCMalfunctionException, \
    MinerFailedToFetchMacAddress, GatewayMFRInvalidVersion, GatewayMFRExecutionException, \
    GatewayMFRFileNotFoundException, UnsupportedGatewayMfrVersion
from hm_pyhelper.lock_singleton import ResourceBusyError
from hm_pyhelper.miner_param import retry_get_region, await_spi_available, \
    provision_key, run_gateway_mfr, \
    did_gateway_mfr_test_result_include_miner_key_pass, \
    get_mac_address, get_public_keys_rust, get_gateway_mfr_version, get_gateway_mfr_command


ALL_PASS_GATEWAY_MFR_TESTS = {
    'ecdh(0)': {'error': 'decode error\n\nCaused by:\n    not a compact key', 'result': 'fail'},
    'key_config(0)': {
        'checks': {
            'auth_key': '0',
            'intrusion_disable': 'false',
            'key_type': 'ecc',
            'lockable': 'true',
            'private': 'true',
            'pub_info': 'true',
            'req_auth': 'false',
            'req_random': 'false',
            'x509_index': '0'
        },
        'result': 'pass'
    },
    'miner_key(0)': {'checks': 'ok', 'result': 'pass'},
    'sign(0)': {'checks': 'ok', 'result': 'pass'},
    'slot_config(0)': {
        'checks': {
            'ecdh_operation': 'true',
            'encrypt_read': 'false',
            'external_signatures': 'true',
            'internal_signatures': 'true',
            'limited_use': 'false',
            'secret': 'true'
        },
        'result': 'pass'
    },
    'zone_locked(config)': {'checks': 'ok', 'result': 'pass'},
    'zone_locked(data)': {'checks': 'ok', 'result': 'pass'}
}

ERROR_MESSAGE = 'decode error\n\nCaused by:\n    not a compact key'

NONE_PASS_GATEWAY_MFR_TESTS = {
    'ecdh(0)': {'error': ERROR_MESSAGE, 'result': 'fail'},
    'key_config(0)': {'error': ERROR_MESSAGE, 'result': 'fail'},
    'miner_key(0)': {'error': ERROR_MESSAGE, 'result': 'fail'},
    'sign(0)': {'error': ERROR_MESSAGE, 'result': 'fail'},
    'slot_config(0)': {'error': ERROR_MESSAGE, 'result': 'fail'},
    'zone_locked(config)': {'error': ERROR_MESSAGE, 'result': 'fail'},
    'zone_locked(data)': {'error': ERROR_MESSAGE, 'result': 'fail'}
}

MOCK_VARIANT_DEFINITIONS = {
        'NEBHNT-WITH-ECC-ADDRESS': {
            'KEY_STORAGE_BUS': '/dev/i2c-X',
            'SWARM_KEY_URI': 'ecc://i2c-X:96?slot=0',
        },
        'NEBHNT-NO-ECC-ADDRESS': {
            'NO_KEY_STORAGE_BUS': '/dev/i2c-X',
            'NO_KEY_SWARM_KEY_URI': 'ecc://i2c-X:96?slot=0',
        }
    }


class SubprocessResult(object):
    def __init__(self, stdout=None, stderr=None):
        self.stdout = stdout
        self.stderr = stderr


@patch.dict('os.environ', {"VARIANT": "NEBHNT-WITH-ECC-ADDRESS"})
@patch('hm_pyhelper.hardware_definitions.variant_definitions',
       MOCK_VARIANT_DEFINITIONS)
class TestMinerParam(unittest.TestCase):

    @patch('subprocess.run', side_effect=FileNotFoundError("File Not Found Error"))
    def test_get_gateway_mfr_version_exception(self, mocked_subprocess_run):
        with self.assertRaises(GatewayMFRExecutionException):
            get_gateway_mfr_version()

        mocked_subprocess_run.assert_called_once_with(
            [ANY, '--version'], capture_output=True, check=True)

    @patch('subprocess.run', return_value=SubprocessResult(stdout='invalid version'))
    def test_get_gateway_mfr_version_invalid_version(self, mocked_subprocess_run):
        with self.assertRaises(GatewayMFRInvalidVersion):
            get_gateway_mfr_version()

        mocked_subprocess_run.assert_called_once_with(
            [ANY, '--version'], capture_output=True, check=True)

    @patch('subprocess.run', return_value=SubprocessResult(stdout=b'gateway_mfr 0.1.7'))
    def test_get_gateway_mfr_version_v017(self, mocked_subprocess_run):
        version = get_gateway_mfr_version()

        self.assertEqual(version.major, 0)
        self.assertEqual(version.minor, 1)
        self.assertEqual(version.micro, 7)

        mocked_subprocess_run.assert_called_once_with(
            [ANY, '--version'], capture_output=True, check=True)

    @patch('subprocess.run', return_value=SubprocessResult(stdout=b'gateway_mfr 0.2.1'))
    def test_get_gateway_mfr_version_v021(self, mocked_subprocess_run):
        version = get_gateway_mfr_version()

        self.assertEqual(version.major, 0)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.micro, 1)

        mocked_subprocess_run.assert_called_once_with(
            [ANY, '--version'], capture_output=True, check=True)

    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.1.7'))
    def test_get_gateway_mfr_command_v017(self, mocked_get_gateway_mfr_version):
        actual_result = get_gateway_mfr_command('key')
        expected_result = [ANY, '--path', '/dev/i2c-X', 'key', '0']
        self.assertListEqual(actual_result, expected_result)
        mocked_get_gateway_mfr_version.assert_called_once()

        actual_result = get_gateway_mfr_command('info')
        expected_result = [ANY, '--path', '/dev/i2c-X', 'info']
        self.assertListEqual(actual_result, expected_result)

    @patch.dict('os.environ', {"VARIANT": "NEBHNT-INVALID"})
    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.1.7'))
    def test_get_gateway_mfr_command_v017_no_variant(self, mocked_get_gateway_mfr_version):
        actual_result = get_gateway_mfr_command('key')
        expected_result = [ANY, 'key', '0']
        self.assertListEqual(actual_result, expected_result)
        mocked_get_gateway_mfr_version.assert_called_once()

        actual_result = get_gateway_mfr_command('info')
        expected_result = [ANY, 'info']
        self.assertListEqual(actual_result, expected_result)

    @patch.dict('os.environ', {"VARIANT": "NEBHNT-NO-ECC-ADDRESS"})
    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.1.7'))
    def test_get_gateway_mfr_command_v017_no_KEY_STORAGE_BUS(self, mocked_get_gateway_mfr_version):
        actual_result = get_gateway_mfr_command('key')
        expected_result = [ANY, 'key', '0']
        self.assertListEqual(actual_result, expected_result)
        mocked_get_gateway_mfr_version.assert_called_once()

        actual_result = get_gateway_mfr_command('info')
        expected_result = [ANY, 'info']
        self.assertListEqual(actual_result, expected_result)

    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.2.1'))
    def test_get_gateway_mfr_command_v021(self, mocked_get_gateway_mfr_version):
        actual_result = get_gateway_mfr_command('key')
        expected_result = [ANY, '--device', 'ecc://i2c-X:96?slot=0', 'key']
        self.assertListEqual(actual_result, expected_result)
        mocked_get_gateway_mfr_version.assert_called_once()

        actual_result = get_gateway_mfr_command('info')
        expected_result = [ANY, '--device', 'ecc://i2c-X:96?slot=0', 'info']
        self.assertListEqual(actual_result, expected_result)

    @patch.dict('os.environ', {"VARIANT": "NEBHNT-INVALID"})
    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.2.1'))
    def test_get_gateway_mfr_command_v021_no_variant(self, mocked_get_gateway_mfr_version):
        actual_result = get_gateway_mfr_command('key')
        expected_result = [ANY, 'key']
        self.assertListEqual(actual_result, expected_result)
        mocked_get_gateway_mfr_version.assert_called_once()

        actual_result = get_gateway_mfr_command('test')
        expected_result = [ANY, 'test']
        self.assertListEqual(actual_result, expected_result)

    @patch.dict('os.environ', {"VARIANT": "NEBHNT-NO-ECC-ADDRESS"})
    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.2.1'))
    def test_get_gateway_mfr_command_v021_no_SWARM_KEY_URI(self, mocked_get_gateway_mfr_version):
        actual_result = get_gateway_mfr_command('key')
        expected_result = [ANY, 'key']
        self.assertListEqual(actual_result, expected_result)
        mocked_get_gateway_mfr_version.assert_called_once()

        actual_result = get_gateway_mfr_command('test')
        expected_result = [ANY, 'test']
        self.assertListEqual(actual_result, expected_result)

    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.2.0'))
    def test_get_gateway_mfr_command_v020(self, mocked_get_gateway_mfr_version):
        actual_result = get_gateway_mfr_command('key')
        expected_result = [ANY, '--device', 'ecc://i2c-X:96?slot=0', 'key']
        self.assertListEqual(actual_result, expected_result)
        mocked_get_gateway_mfr_version.assert_called_once()

        actual_result = get_gateway_mfr_command('info')
        expected_result = [ANY, '--device', 'ecc://i2c-X:96?slot=0', 'info']

    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.3.9'))
    def test_get_gateway_mfr_command_v021_upward(self, mocked_get_gateway_mfr_version):
        actual_result = get_gateway_mfr_command('key')
        expected_result = [ANY, '--device', 'ecc://i2c-X:96?slot=0', 'key']
        self.assertListEqual(actual_result, expected_result)
        mocked_get_gateway_mfr_version.assert_called_once()

        actual_result = get_gateway_mfr_command('info')
        expected_result = [ANY, '--device', 'ecc://i2c-X:96?slot=0', 'info']

    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.0.0'))
    def test_get_gateway_mfr_command_unsupported_version(self, mocked_get_gateway_mfr_version):
        with self.assertRaises(UnsupportedGatewayMfrVersion):
            get_gateway_mfr_command('key')
        mocked_get_gateway_mfr_version.assert_called_once()

    @patch('hm_pyhelper.miner_param.get_gateway_mfr_command',
           return_value=['gateway_mfr', 'arg1', 'arg2'])
    @patch('subprocess.run', side_effect=FileNotFoundError())
    def test_run_gateway_mfr_GatewayMFRFileNotFoundException(
            self,
            mocked_subprocess_run,
            mocked_get_gateway_mfr_command
    ):
        with self.assertRaises(GatewayMFRFileNotFoundException):
            run_gateway_mfr("unittest")

        mocked_get_gateway_mfr_command.assert_called_once_with('unittest')
        mocked_subprocess_run.assert_called_once_with(
            ['gateway_mfr', 'arg1', 'arg2'],
            capture_output=True, check=True)

    @patch('hm_pyhelper.miner_param.get_gateway_mfr_command',
           return_value=['gateway_mfr', 'arg1', 'arg2'])
    @patch('subprocess.run', side_effect=Exception())
    def test_run_gateway_mfr_ECCMalfunctionException(
            self,
            mocked_subprocess_run,
            mocked_get_gateway_mfr_command
    ):
        with self.assertRaises(ECCMalfunctionException):
            run_gateway_mfr("unittest")

        mocked_get_gateway_mfr_command.assert_called_once_with('unittest')
        mocked_subprocess_run.assert_called_once_with(
            ['gateway_mfr', 'arg1', 'arg2'],
            capture_output=True, check=True)

    @patch('hm_pyhelper.miner_param.get_gateway_mfr_command',
           return_value=['gateway_mfr', 'arg1', 'arg2'])
    @patch('subprocess.run', side_effect=ResourceBusyError())
    def test_run_gateway_mfr_ResourceBusyError(
            self,
            mocked_subprocess_run,
            mocked_get_gateway_mfr_command
    ):
        with self.assertRaises(ResourceBusyError):
            run_gateway_mfr("unittest")

        mocked_get_gateway_mfr_command.assert_called_once_with('unittest')
        mocked_subprocess_run.assert_called_once_with(
            ['gateway_mfr', 'arg1', 'arg2'],
            capture_output=True, check=True)

    @patch('hm_pyhelper.miner_param.get_gateway_mfr_command',
           return_value=['gateway_mfr', 'arg1', 'arg2'])
    @patch('subprocess.run',
           return_value=SubprocessResult(
               stdout=json.dumps({
                   "key": "ABCD123456789",
                   "name": "formal-magenta-anteater",
                   "slot": 0
               })
           ))
    def test_get_public_keys_rust(
            self,
            mocked_subprocess_run,
            mocked_get_gateway_mfr_command
    ):
        actual_result = get_public_keys_rust()
        expected_result = {
            "key": "ABCD123456789",
            "name": "formal-magenta-anteater",
            "slot": 0
        }

        self.assertDictEqual(actual_result, expected_result)

        mocked_get_gateway_mfr_command.assert_called_once_with('key')
        mocked_subprocess_run.assert_called_once_with(
            ['gateway_mfr', 'arg1', 'arg2'],
            capture_output=True, check=True)

    @patch(
            'hm_pyhelper.miner_param.get_gateway_mfr_test_result',
            return_value={
                "result": "pass",
                "tests": ALL_PASS_GATEWAY_MFR_TESTS
                }
    )
    def test_provision_key_all_passed(
            self,
            mocked_get_gateway_mfr_test_result
    ):
        self.assertTrue(provision_key())
        mocked_get_gateway_mfr_test_result.assert_called_once()

    @patch(
            'hm_pyhelper.miner_param.get_gateway_mfr_test_result',
            return_value={
                "result": "fail",
                "tests": NONE_PASS_GATEWAY_MFR_TESTS
            }
    )
    @patch('hm_pyhelper.miner_param.run_gateway_mfr')
    def test_provision_key_none_passed(
            self,
            mocked_get_gateway_mfr_test_result,
            mocked_run_gateway_mfr
    ):
        self.assertTrue(provision_key())

        mocked_get_gateway_mfr_test_result.assert_called_once()
        mocked_run_gateway_mfr.assert_called_once()

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
            "tests": ALL_PASS_GATEWAY_MFR_TESTS
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
