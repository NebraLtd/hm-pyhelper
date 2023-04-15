from setuptools import setup, find_packages
import os

# allow setup.py to be run from any path
here = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))
os.chdir(here)

requires = [
    line.strip()
    for line in open(os.path.join(here, "requirements.txt"), "r").readlines()
]

setup(
    name='hm_pyhelper',
    version='0.14.7',
    author="Nebra Ltd",
    author_email="support@nebra.com",
    description="Helium Python Helper",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NebraLtd/hm-pyhelper",
    install_requires=requires,
    project_urls={
        "Bug Tracker": "https://github.com/NebraLtd/hm-pyhelper/issues",
    },
    packages=find_packages(),
    include_package_data=True
)
