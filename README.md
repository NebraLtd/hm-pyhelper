# Helium Python Helper

A helper module used across various Nebra repos to reduce redundant features.

This package is used in a number of Nebra software repos:
- [hm-pktfwd](https://github.com/NebraLtd/hm-pktfwd/)
- [hm-config](https://github.com/NebraLtd/hm-config/)
- [hm-diag](https://github.com/NebraLtd/hm-diag/)

The package is available on PyPI and PyPI test repos:
- [PyPI hm-pyhelper](https://pypi.org/project/hm-pyhelper)
- [PyPI Test hm-pyhelper](https://test.pypi.org/project/hm-pyhelper)

## Helium Hardware Definitions

```python
from hm_pyhelper.hardware_definitions import variant_definitions
```

This repository contains the python file that contains a GPIO map for all of the different hardware combinations to be supported by the Nebra Helium Hotspot Software.

All numbers below are their GPIO / BCM Numbers, not physical pin numbers.

Note: Light hotspot software will also work on all models listed as type "full".

### Nebra Hotspots

| Model | ENV Identifier | SPI Bus | Reset Pin | Status LED | Button |Type | Cellular | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Nebra Indoor Hotspot Gen 1 | NEBHNT-IN1 | 1.2 | 38 | 25 | 26 | Full | False | CM3 based |
| Nebra Outdoor Hotspot Gen 1 | NEBHNT-OUT1 | 1.2 | 38 | 25 | 24 | Full | True | CM3 based |
| Nebra Pi 0 Light Hotspot S | NEBHNT-LGT-ZS | 1.2 | 22 | 24 | 23 | Light | False | SPI Based Ethernet |
| Nebra Pi 0 Light Hotspot X | NEBHNT-LGT-ZX | 1.2 | 22 | 24 | 23 | Light | False | USB Based Ethernet |
| Nebra Beaglebone Light Hotspot | NEBHNT-BBB | 1.0 | 60 | 31  | 30  | Light | False | In Planning |
| Nebra Pocket Beagle Light Hotspot | NEBHNT-PBB | 1.0 | 60 | 31 | 30 | Light | False | In Planning |
| Nebra Hotspot HAT RockPi4 | NEBHNT-HHRK4 | 1.0 | 149 | 156 | 154 | Full | False | In Planning |
| Nebra Hotspot HAT RPi | NEBHNT-HHRPI | 0.0 | 22 | 24 | 23 | Full | False | Should be compatible with 3+ & 4 |
| Nebra Hotspot HAT RPi LIGHT | NEBHNT-HHRPL | 0.0 | 22 | 24 | 23 | Light | False | Light is compatible with all 40 pin headers |
| Nebra Hotspot HAT Tinkerboard 2 | NEBHNT-HHTK | 2.0 | 167 | 163 | 162 | Full | False | Light would be compatible on TK1 |

### Third Party Hotspots

We may be adding in support for other vendor's hotspots to use our software soon. Here are the variables for those.

These would also depend on their SOCs being supported by Balena.

| Model | SOC/SBC | ENV Identifier | SPI Bus | Reset Pin | Status LED | Button |Type | Cellular | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Rak Hotspot Miner | BCM2711 (Pi4 2gb RAM)  | COMP-RAKHM | 0.0 | 17 | 20 | 21 | Full | False | Only Compatible with V2 hotspots with ECC Key. |
| OG Helium Hotspot | BCM2711 (Pi4 2gb RAM) | COMP-HELIUM | 0.0 | 17 | 20 | 21 | Full | False |  |
| Syncrobit Hotspot 1 (Pi) |  |  |  |  |   |   | Full | False |  |
| Syncrobit Hotspot 2 (RK) |  |  |  |  |   |   | Full | False |  |
| Bobcat Miner 300 |  |  |  |  |   |   | Full | False |  |
| SenseCAP M1 | BCM2711 (Pi4 2gb RAM)  | COMP-SENSECAPM1 | 0.0 | 17 | 20 | 21 | Full | False |  |

### DIY Hotspots

The following DIY options are also supported for light hotspot software only.

Please note, DIY Hotspots do not earn HNT.

| Model | SOC/SBC | ENV Identifier | SPI Bus | Reset Pin | Status LED | Button |Type | Cellular | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pi Supply IoT LoRa Gateway HAT | RPi | DIY-PISLGH | 0.0 | 22 |   |   | Light | False | Any pi with 40 pin header |
| RAK2287 | RPi | DIY-RAK2287 | 0.0 | 17 |   |   | Light | False | Any pi with 40 pin header |

## logger

```python
from hm_pyhelper.logger import get_logger
LOGGER = get_logger(__name__)
LOGGER.debug("message to log")
```

## miner_param

### retry_get_region(region_override, region_filepath)
Return the region from envvar region_override or
from the contents of region_filepath

```python
from hm_pyhelper.miner_param import retry_get_region
print(retry_get_region("US915", "/invalid/path"))
# US915

# echo "EU868" > /var/pktfwd/region
print(retry_get_region("", "/var/pktfwd/region"))
# EU868
```

## LockSingleton
`LockSingleton` prevents the concurrent access to a resource.

### Methods

**InterprocessLock(name, initial_value=1)**

Creates a new `InterprocessLock` object.
- `name` uniquely identifies the `LockSingleton` across processes in the system
- `available_resources` the count of the available resources
- `reset` set `True` to reset the available_resources  
  
Note:
  The available_resources of a `InterprocessLock` get reset on every restart of the system or docker container.
  It's tested in Ubuntu 20.04 desktop and diagnostics container in a Hotspot.
  Resetting the available_resources by passing the `reset=True` should be used with a caution and it can be used
  in a very specific scenarios such as in the development environment. It's designed for facilitating
  the development. It's not recommended to be used in production.

**acquire([timeout = None])**

Waits until the resource is available and then returns, decrementing the available count.
 
**release()**

Release the resource.

**locked()**

Check if there is an available resource.

**value()**

Returns the count of available resources.

### Usage
```
lock = LockSingleton("some_resource")

try:
    # try to acquire the resource or may raise an exception
    lock.acquire()

    # do some work
    print("Starting work...")
    sleep(5)
    print("Finished work!")

    # release the resource
    lock.release()
except ResourceBusyError:
    print("The resource is busy now.")
except CannotLockError:
    print("Can't lock the resource for some internal issue.")
```

### `@ecc_lock` decorator
`@ecc_lock(timeout=DEFAULT_TIMEOUT, raise_exception=False):`

This is the convenient decorator wrapping around the `LockSingleton`.
  - timeout: timeout value. DEFAULT_TIMEOUT = 2 seconds 
  - raise_exception: set True to raise exception in case of timeout or some error, otherwise just log the error msg

Usage
```
@ecc_lock()
def run_gateway_mfr():
    return subprocess.run(
        [gateway_mfr_path, "key", "0"],
        capture_output=True,
        check=True
    )

gateway_mfr_result = run_gateway_mfr()
log_stdout_stderr(gateway_mfr_result)
```

## Testing

To run tests:

```bash
pip install -r requirements.txt
pip install -r test-requirements.txt
PYTHONPATH=./ pytest
```

## Referencing a branch for development
It is sometimes convenient to use recent changes in hm-pyhelper before an official release.
To do so, first double check that you've added any relevant dependencies to
the `install_requires` section of `setup.py`. Then add the following lines to the
project's Dockerfile.

```Dockerfile
RUN pip3 install setuptools wheel
RUN pip3 install --target="$OUTPUTS_DIR" git+https://github.com/NebraLtd/hm-pyhelper@BRANCH_NAME
``````

## Releasing

To release, use the [Github new release flow](https://github.com/NebraLtd/hm-pyhelper/releases/new).

1. Create a new tag in format `vX.Y.Z`. You can use a previously tagged commit, but this is not necessary.
2. Make sure the tag you created matches the value in setup.py.
3. Select `master` as the target branch. If you do not select the master branch, the tag should be in format `vX.Y.Z-rc.N`.
4. Title: `Release vX.Y.Z`.
5. Body:

**Note: you can create the release notes automatically by selecting the "Auto-generate release notes" option on the releases page.**

```
## What's Changed
* Foo
* Bar

**Full Changelog**: https://github.com/NebraLtd/hm-pyhelper/compare/v0.0.A...v0.0.Z
```
