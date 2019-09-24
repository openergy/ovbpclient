from setuptools import setup, find_packages
from pkg_resources import parse_requirements
import os

with open(os.path.join("openergy", "version.py")) as f:
    version = f.read().split("=")[1].strip().strip("'").strip('"')

with open("requirements.txt", "r") as f:
    requirements = [str(r).replace("pytables", "tables") for r in parse_requirements(f.read())]

setup(
    name='openergy',
    version=version,
    packages=find_packages(),
    author="Geoffroy d'Estaintot",
    author_email="geoffroy.destaintot@openergy.fr",
    long_description=open('README.md').read(),
    install_requires=requirements,
    url='https://github.com/openergy/openergy',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: French",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    package_data={'openergy': ['*.txt']},
    include_package_data=True
)
