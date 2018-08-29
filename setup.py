from setuptools import find_packages, setup

__author__ = "spapanik"
__license__ = "MIT"
__version__ = "0.0.1"


PKG_NAME = "pygatherer"
PKG_URL = f"https://github.com/{__author__}/{PKG_NAME}"

setup(
    name=PKG_NAME,
    version=__version__,
    license=__license__,
    description="An API for the gatherer",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.0,<3.0" "beautifulsoup4>=4.0,<5.0" "lxml>=4.0,<5.0"
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
