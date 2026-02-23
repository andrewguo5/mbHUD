"""
Setup configuration for mbHUD package.

Install with: pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name="mbhud",
    version="0.1.1",
    description="Poker HUD for Americas Cardroom",
    author="Andrew Guo",
    python_requires=">=3.7",

    # Find all packages (poker_hud, scripts, etc.)
    packages=find_packages(),

    # Include the CLI module at top level
    py_modules=['cli'],

    # Include non-Python files (config.json, etc.)
    include_package_data=True,

    # Dependencies
    install_requires=[
        "click>=8.0",
    ],

    # Create 'mbhud' command that points to cli:cli
    entry_points={
        "console_scripts": [
            "mbhud=cli:cli",
        ],
    },

    # Package metadata
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
