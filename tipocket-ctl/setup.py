#!/usr/bin/env python3

from setuptools import setup

setup(
    name='tpctl',
    version='0.1.dev0',
    description='run tipocket testcase easier',
    author='Cosven',
    author_email='yinshaowen241@gmail.com',
    packages=[
        'tpctl',
    ],
    package_data={
        '': ['data/*'],
        '': ['scripts/env_raw.sh']
    },
    python_requires=">=3.6",
    url='https://github.com/cosven/tidb-testing/casectl',
    keywords=['tidb', 'testing'],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    install_requires=[
        'click',
        'pyyaml',
        'click_option_group',
    ],
    extras_require={
    },
    tests_require=[],
    entry_points={
        'console_scripts': [
            "tpctl=tpctl.__main__:main",
        ]
    },
)
