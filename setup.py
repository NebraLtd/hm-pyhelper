from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='hm_pyhelper',
    version='0.1',
    author="Nebra Ltd",
    description="Helium Python Helper",
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NebraLtd/hm-pyhelper",
    project_urls={
        "Bug Tracker": "https://github.com/NebraLtd/hm-pyhelper/issues",
    },
    packages=find_packages(),
)
