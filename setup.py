from setuptools import find_packages, setup

setup(
    name="pygatherer",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
)
