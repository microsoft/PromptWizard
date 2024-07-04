# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = "" #(this_directory / "README.md").read_text()
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: Other/Proprietary License",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
    "Operating System :: POSIX :: Linux",
]

REQUIRES = ["llama-index-core==0.10.24",
            "pyyaml",
            "pandas==2.2.0",
            "numpy==1.26.3",
            "pyyaml~=6.0.1",
            "tenacity",
            "tqdm"]

# TODO pin down versions of libraries
TEST_REQUIRES = ["pytest"]
DEV_REQUIRES = ["twine", "wheel"]

setup(
    name="glue-common",
    version="0.0.1",
    author="Vivek Dani",
    description="Its a framework to seamlessly evaluate any pipeline where there is a need to evaluate each component "
                "of the pipeline independently. e.g. Co-pilot pipeline which uses Large Language Model at multiple "
                "stages and we want to evaluate its output at each stage.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="",  # TODO add url of repo
    classifiers=CLASSIFIERS,
    install_requires=REQUIRES,
    python_requires=">=3.10, <3.13",
    packages=find_packages(exclude=["tests*", "scripts*"]),
    extras_require={"test": TEST_REQUIRES, "dev": DEV_REQUIRES},
    package_data={"": ["*/*requirements.txt"]},
)
