# Helium Python Helper

A helper module used across various Nebra repos to reduce redundant features.

This package is used in a number of Nebra software repos:
- [hm-pktfwd](https://github.com/NebraLtd/hm-pktfwd/)
- [hm-config](https://github.com/NebraLtd/hm-config/)
- [hm-diag](https://github.com/NebraLtd/hm-diag/)
- [hm-dashboard (private repo)](https://github.com/NebraLtd/hm-dashboard)
- [Hotspot-Production-Tool (private repo)](https://github.com/NebraLtd/Hotspot-Production-Tool)

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
| Nebra Hotspot HAT ROCK Pi 4 Indoor | NEBHNT-HHRK4 | 32766.0 | 149 | 156 (Physical pin 18) | 154 (Physical pin 16) | Full | False | In Planning |
| Nebra Hotspot HAT ROCK Pi 4 Outdoor | NEBHNT-HHRK4-OUT | 32766.0 | 149 | 156 (Physical pin 18) | 154 (Physical pin 16)| Full | True | In Planning |
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
`LockSingleton` prevents the concurrent access to a resource across threads.

### Methods

**LockSingleton()**

Creates a new `LockSingleton` object.
  
**acquire(timeout = DEFAULT_TIMEOUT)**

Waits until the resource is available. DEFAULT_TIMEOUT = 2 seconds 
 
**release()**

Release the resource.

**locked()**

Check if there is an available resource.

### Usage
```
lock = LockSingleton()

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
```

### `@lock_ecc` decorator
`@lock_ecc(timeout=DEFAULT_TIMEOUT, raise_resource_busy_exception=True):`

This is the convenient decorator wrapping around the `LockSingleton`.
  - timeout: timeout value. DEFAULT_TIMEOUT = 2 seconds.
  - raise_resource_busy_exception: set True to raise exception in case of timeout or some error, otherwise just log the error msg

Usage
```
@lock_ecc()
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

### Release strategy

The automated GitHub Actions in this repo do the following:
- all pushes / PRs, regardless of branch, trigger a build of the wheels and python package which are released as build artifacts ([see below section](#test-release-artifacts))
- pushes to master with an updated version number in `setup.py` are pushed to Test PyPI as well as being uploaded as build artifacts (note that if the version number isn't properly updated and is a duplicate of a previous one then the push to Test PyPI will fail)
- any tagged releases on master branch ([see releasing process above](#releasing)) are built and published to PyPI as well as being uploaded as build artifacts

### Test release artifacts

Note that artifacts (wheels and source) are uploaded to the GitHub Actions artifacts even when the build fails or isn't pushed to PyPI/Test PyPI due to not being on the master branch.

For example, [this failed build](https://github.com/NebraLtd/hm-pyhelper/actions/runs/1369814396), has artifacts uploaded [here](https://github.com/NebraLtd/hm-pyhelper/suites/4125934376/artifacts/105569066).

These artifacts can be useful for testing releases without needing to bump version numbers.
