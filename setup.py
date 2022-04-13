import ast
import re

from setuptools import setup

# Read version number ----


_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("gtfs_validator_api.py", "rb") as f:
    VERSION = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )

# Get README ----

# with open('README.md') as f:
#     README = f.read()

# Setup ----

setup(
    name="gtfs_validator_api",
    py_modules=["gtfs_validator_api"],
    version=VERSION,
    # description="A thin wrapper around MobilityData/gtfs-validator",
    # author='Michael Chow',
    # license='MIT',
    # author_email='mc_al_general@fastmail.com',
    # url='https://github.com/cal-itp/gtfs_validator_api',
    keywords=["package"],
    entry_points={"console_scripts": ["gtfs-validator-api=gtfs_validator_api:main"]},
    install_requires=["argh"],
    python_requires=">=3.6",
    # long_description=README,
    # long_description_content_type="text/markdown",
)
