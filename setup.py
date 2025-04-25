from setuptools import setup, find_packages

setup(
    name="joby_challenge",
    packages=find_packages(),
    install_requires=[
        "aioping==0.4.0",
        "pytest==8.3.4",
        "pytest-asyncio==0.26.0",
    ],
    entry_points={
        "console_scripts": [
            "joby_challenge=joby_challenge.main:run",
        ],
    },
    description="A utility to ping IP addresses across different networks and identify mismatches",
    python_requires=">=3.7",
)
