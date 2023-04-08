import json
import unittest
import pytest
import sys
from unittest.mock import ANY, mock_open, patch, Mock
from packaging.version import Version
from hm_pyhelper.exceptions import ECCMalfunctionException, UnknownVariantAttributeException, \
    MinerFailedToFetchMacAddress, GatewayMFRInvalidVersion, GatewayMFRExecutionException, \
    GatewayMFRFileNotFoundException, UnsupportedGatewayMfrVersion, UnknownVariantException
from hm_pyhelper.lock_singleton import ResourceBusyError
from hm_pyhelper.miner_param import retry_get_region, await_spi_available, \
    provision_key, run_gateway_mfr, get_gateway_mfr_path, config_search_param, get_ecc_location, \
    did_gateway_mfr_test_result_include_miner_key_pass, parse_i2c_address, parse_i2c_bus, \
    get_mac_address, get_public_keys_rust, get_gateway_mfr_version, get_gateway_mfr_command, \
    get_onboarding_location

sys.path.append("..")

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
            'SWARM_KEY_URI': ['ecc://i2c-X:96?slot=0'],
            'ONBOARDING_KEY_URI': ['ecc://i2c-X:96?slot=0'],
        },
        'NEBHNT-NO-ECC-ADDRESS': {
            'NO_KEY_STORAGE_BUS': '/dev/i2c-X',
            'NO_KEY_SWARM_KEY_URI': ['ecc://i2c-X:96?slot=0'],
            'NO_ONBOARDING_KEY_URI': ['ecc://i2c-X:96?slot=0'],
        },
        'NEBHNT-MULTIPLE-ECC-ADDRESS': {
            'KEY_STORAGE_BUS': '/dev/i2c-2',
            'SWARM_KEY_URI': ['ecc://i2c-3:96?slot=0', 'ecc://i2c-4:88?slot=10'],
            'ONBOARDING_KEY_URI': ['ecc://i2c-3:96?slot=0', 'ecc://i2c-4:88?slot=15'],
        }
    }

ECC_FILE_DATA = 'ecc://i2c-Y:96?slot=1'
ECC_FILE_DATA_BLANK = None
ONBOARDING_FILE_DATA = 'ecc://i2c-Z:96?slot=10'
ONBOARDING_FILE_DATA_BLANK = None


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
           return_value=Version('0.2.1'))
    def test_get_gateway_mfr_command_v021(self, mocked_get_gateway_mfr_version):
        actual_result = get_gateway_mfr_command('key')
        expected_result = [ANY, '--device', 'ecc://i2c-X:96?slot=0', 'key']
        self.assertListEqual(actual_result, expected_result)
        mocked_get_gateway_mfr_version.assert_called_once()

        actual_result = get_gateway_mfr_command('test', 9)
        expected_result = [ANY, '--device', 'ecc://i2c-X:96?slot=9', 'test']
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

    @patch.dict('os.environ', {"SWARM_KEY_URI_OVERRIDE": "override-test"})
    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.2.1'))
    def test_get_gateway_mfr_command_v021_override(self, mocked_get_gateway_mfr_version):
        actual_result = get_gateway_mfr_command('key')
        expected_result = [ANY, '--device', 'override-test', 'key']
        self.assertListEqual(actual_result, expected_result)
        mocked_get_gateway_mfr_version.assert_called_once()

        actual_result = get_gateway_mfr_command('test')
        expected_result = [ANY, '--device', 'override-test', 'test']
        self.assertListEqual(actual_result, expected_result)

    @patch("builtins.open", mock_open(read_data=ECC_FILE_DATA_BLANK))
    @patch.dict('os.environ', {"VARIANT": "NEBHNT-MULTIPLE-ECC-ADDRESS"})
    @patch('subprocess.Popen')
    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.2.1'))
    def test_get_gateway_mfr_command_v021_multi_SWARM_KEY_URI(self, mocked_get_gateway_mfr_version,
                                                              mock_subproc_popen):
        process_mock = Mock()
        attrs = {'communicate.return_value': (str.encode("60 --"), 'error')}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock

        actual_result = get_gateway_mfr_command('key')
        expected_result = [ANY, '--device', 'ecc://i2c-3:96?slot=0', 'key']
        self.assertListEqual(actual_result, expected_result)
        mocked_get_gateway_mfr_version.assert_called_once()

    @patch("builtins.open", mock_open(read_data=ECC_FILE_DATA_BLANK))
    @patch.dict('os.environ', {"VARIANT": "NEBHNT-MULTIPLE-ECC-ADDRESS"})
    @patch('subprocess.Popen')
    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.2.1'))
    def test_get_gateway_mfr_command_v021_multi_SWARM_KEY_58(self, mocked_get_gateway_mfr_version,
                                                             mock_subproc_popen):
        process_mock = Mock()
        attrs = {'communicate.return_value': (str.encode("58 --"), 'error')}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock

        actual_result = get_gateway_mfr_command('test')
        expected_result = [ANY, '--device', 'ecc://i2c-4:88?slot=10', 'test']
        self.assertListEqual(actual_result, expected_result)

    @patch("builtins.open", mock_open(read_data=ECC_FILE_DATA_BLANK))
    @patch.dict('os.environ', {"VARIANT": "NEBHNT-MULTIPLE-ECC-ADDRESS"})
    @patch('subprocess.Popen')
    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.2.1'))
    def test_get_gateway_mfr_command_v021_multi_SWARM_KEY_42(self, mocked_get_gateway_mfr_version,
                                                             mock_subproc_popen):
        process_mock = Mock()
        attrs = {'communicate.return_value': (str.encode("42 --"), 'error')}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock

        actual_result = get_gateway_mfr_command('test')
        expected_result = [ANY, '--device', None, 'test']
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
        self.assertListEqual(actual_result, expected_result)

    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.3.9'))
    def test_get_gateway_mfr_command_v021_upward(self, mocked_get_gateway_mfr_version):
        actual_result = get_gateway_mfr_command('key')
        expected_result = [ANY, '--device', 'ecc://i2c-X:96?slot=0', 'key']
        self.assertListEqual(actual_result, expected_result)
        mocked_get_gateway_mfr_version.assert_called_once()

        actual_result = get_gateway_mfr_command('info')
        expected_result = [ANY, '--device', 'ecc://i2c-X:96?slot=0', 'info']
        self.assertListEqual(actual_result, expected_result)

    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.3.9'))
    def test_get_gateway_mfr_command_slot_force(self, mocked_get_gateway_mfr_version):
        actual_result = get_gateway_mfr_command('key', 3)
        expected_result = [ANY, '--device', 'ecc://i2c-X:96?slot=3', 'key']
        self.assertListEqual(actual_result, expected_result)
        mocked_get_gateway_mfr_version.assert_called_once()

        actual_result = get_gateway_mfr_command('info', 15)
        expected_result = [ANY, '--device', 'ecc://i2c-X:96?slot=15', 'info']
        self.assertListEqual(actual_result, expected_result)

    @patch('hm_pyhelper.miner_param.get_gateway_mfr_version',
           return_value=Version('0.0.0'))
    def test_get_gateway_mfr_command_unsupported_version(self, mocked_get_gateway_mfr_version):
        with self.assertRaises(UnsupportedGatewayMfrVersion):
            get_gateway_mfr_command('key')
        mocked_get_gateway_mfr_version.assert_called_once()

    @patch("builtins.open", mock_open(read_data=ECC_FILE_DATA))
    def test_get_ecc_location_generated_ecc(self):
        actual_result = get_ecc_location()
        expected_result = 'ecc://i2c-Y:96?slot=1'
        self.assertEqual(actual_result, expected_result)

    @patch("builtins.open", mock_open(read_data=ONBOARDING_FILE_DATA))
    def test_get_onboarding_location_generated_ecc(self):
        actual_result = get_onboarding_location()
        expected_result = 'ecc://i2c-Z:96?slot=10'
        self.assertEqual(actual_result, expected_result)

    @patch.dict('os.environ', {"ONBOARDING_KEY_URI_OVERRIDE": "override-test"})
    def test_get_onboarding_override(self):
        actual_result = get_onboarding_location()
        expected_result = "override-test"
        self.assertEqual(actual_result, expected_result)

    @patch("builtins.open", mock_open(read_data=ONBOARDING_FILE_DATA_BLANK))
    @patch.dict('os.environ', {"VARIANT": "NEBHNT-MULTIPLE-ECC-ADDRESS"})
    @patch('subprocess.Popen')
    def test_get_onboarding_key_multi_KEY_URI(self, mock_subproc_popen):
        process_mock = Mock()
        attrs = {'communicate.return_value': (str.encode("60 --"), 'error')}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock

        actual_result = get_onboarding_location()
        expected_result = 'ecc://i2c-3:96?slot=0'
        self.assertEqual(actual_result, expected_result)

    @patch("builtins.open", mock_open(read_data=ONBOARDING_FILE_DATA_BLANK))
    @patch.dict('os.environ', {"VARIANT": "NEBHNT-MULTIPLE-ECC-ADDRESS"})
    @patch('subprocess.Popen')
    def test_get_onboarding_key_multi_KEY_58(self, mock_subproc_popen):
        process_mock = Mock()
        attrs = {'communicate.return_value': (str.encode("58 --"), 'error')}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock

        actual_result = get_onboarding_location()
        expected_result = 'ecc://i2c-4:88?slot=15'
        self.assertEqual(actual_result, expected_result)

    @patch.dict('os.environ', {"VARIANT": "NEBHNT-NO-ECC-ADDRESS"})
    def test_get_onboarding_key_missing(self):
        with self.assertRaises(UnknownVariantAttributeException):
            get_onboarding_location()

    @patch.dict('os.environ', {"VARIANT": "NEBHNT-NO-ECC-ADDRESS"})
    def test_get_ecc_key_missing(self):
        with self.assertRaises(UnknownVariantAttributeException):
            get_ecc_location()

    @patch.dict('os.environ', {"VARIANT": "MISSING"})
    def test_get_onboarding_key_missing_variant(self):
        with self.assertRaises(UnknownVariantException):
            get_onboarding_location()

    @patch.dict('os.environ', {"VARIANT": "MISSING"})
    def test_get_ecc_key_missing_variant(self):
        with self.assertRaises(UnknownVariantException):
            get_ecc_location()

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

        mocked_get_gateway_mfr_command.assert_called_once_with('unittest', slot=0)
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

        mocked_get_gateway_mfr_command.assert_called_once_with('unittest', slot=0)
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

        mocked_get_gateway_mfr_command.assert_called_once_with('unittest', slot=0)
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

        mocked_get_gateway_mfr_command.assert_called_once_with('key', slot=0)
        mocked_subprocess_run.assert_called_once_with(
            ['gateway_mfr', 'arg1', 'arg2'],
            capture_output=True, check=True)

    def test_provision_key_all_passed(self):
        self.assertTrue(provision_key(slot=0))

    @patch('hm_pyhelper.miner_param.run_gateway_mfr')
    def test_provision_key_none_passed(self, mocked_run_gateway_mfr):
        self.assertTrue(provision_key(slot=0))

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

    @patch('platform.machine')
    @patch('os.path.dirname')
    def test_get_gateway_mfr_path(self, mock_dir, mock_platform):
        mock_dir.return_value = "/test/this/works"
        mock_platform.return_value = "aarch64"
        actual_result = get_gateway_mfr_path()
        expected_result = "/test/this/works/gateway_mfr_aarch64"
        self.assertEqual(actual_result, expected_result)

    def test_parse_i2c_address(self):
        port = 96
        output = parse_i2c_address(port)
        hex_i2c_address = '60'

        self.assertEqual(output, hex_i2c_address)

    def test_parse_i2c_bus(self):
        bus = 'i2c-1'
        output = parse_i2c_bus(bus)
        i2c_bus = '1'

        self.assertEqual(output, i2c_bus)


class TestConfigSearch(unittest.TestCase):
    @patch('subprocess.Popen')
    def test_correct_param(self, mock_subproc_popen):
        process_mock = Mock()
        attrs = {'communicate.return_value': (str.encode("60--"), 'error')}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock
        result = config_search_param("somecommand", "60--")
        self.assertEqual(result, True)

    @patch('subprocess.Popen')
    def test_incorrect_param(self, mock_subproc_popen):
        process_mock = Mock()
        attrs = {'communicate.return_value': (str.encode('output'), 'error')}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock
        result = config_search_param("somecommand", "60--")
        self.assertEqual(result, False)

    @patch('subprocess.Popen')
    def test_error_command(self, mock_subproc_popen):
        process_mock = Mock()
        attrs = {'communicate.return_value': (str.encode(''),
                 "Error: Could not open file `/dev/i2c-1' or `/dev/i2c/1': "
                                              "No such file or directory")}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock
        result = config_search_param("somecommand", "60--")
        self.assertEqual(result, False)

    def test_types(self):
        self.assertRaises(TypeError, config_search_param, 1, 2)
        self.assertRaises(TypeError, config_search_param, "123321", 1)
        self.assertRaises(TypeError, config_search_param, 1, "123321")
