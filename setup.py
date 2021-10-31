from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='hm_pyhelper_smaj_test',
    version='0.8.12',
    author="Sebastian Maj",
    author_email="smaj@nebra.com",
    description="Helium Python Helper Test Package",
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SebastianMaj/hm-pyhelper",
    install_requires=[
        'requests>=2.26.0',
        'jsonrpcclient==3.3.6',
        'retry==0.9.2',
        'bump2version'
    ],
    project_urls={
        "Bug Tracker": "https://github.com/SebastianMaj/hm-pyhelper/issues",
    },
    packages=find_packages(),
    include_package_data=True
)
