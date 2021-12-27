from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='hm_pyhelper',
    version='0.12.5',
    author="Nebra Ltd",
    author_email="support@nebra.com",
    description="Helium Python Helper",
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NebraLtd/hm-pyhelper",
    install_requires=[
        'requests>=2.26.0',
        'jsonrpcclient==3.3.6',
        'retry==0.9.2'
    ],
    project_urls={
        "Bug Tracker": "https://github.com/NebraLtd/hm-pyhelper/issues",
    },
    packages=find_packages(),
    include_package_data=True
)
