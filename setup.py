#!/usr/bin/env python3
from setuptools import setup

config = {
    "name": "c-sar-denarius",
    "description": "Interface overlay for c-sar",
    "long_description": open("README.md").read(),
    "long_description_content_type": "text/markdown",
    "author": "Keiran M Raine",
    "url": "https://github.com/cancerit/c-sar-denarius",
    "author_email": "cgphelp@sanger.ac.uk",
    "version": "0.0.0",
    "license": "AGPL-3.0",
    "python_requires": ">= 3.9",
    "install_requires": [
        "click>=8.0.1",
        "click-option-group>=0.5.3",
        "mkdocs-material>=7.2.2",
        "pyyaml>=5.4.1",
    ],
    "packages": ["c_sar_denarius"],
    "package_data": {
        "c_sar_denarius": [
            "resources/structure/*.yaml",
            "resources/templates/*",
            "resources/other/*",
        ]
    },
    "entry_points": {
        "console_scripts": ["c-sar-denarius=c_sar_denarius.cli:cli"],
    },
}

setup(**config)
