from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='hm_pyhelper',
    version='0.13.53',
    author="Nebra Ltd",
    author_email="support@nebra.com",
    description="Helium Python Helper",
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NebraLtd/hm-pyhelper",
    install_requires=[
        'requests>=2.28.1',
        'retry==0.9.2',
        'base58==2.1.1',
        'protobuf==4.21.12',
        'packaging>=22.0'
    ],
    project_urls={
        "Bug Tracker": "https://github.com/NebraLtd/hm-pyhelper/issues",
    },
    packages=find_packages(),
    include_package_data=True
)
