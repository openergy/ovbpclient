from setuptools import setup, find_packages
from pkg_resources import parse_requirements
import os

with open(os.path.join("openergy", "version.py")) as f:
    version = f.read().split("=")[1].strip().strip("'").strip('"')


def _get_req_list(file_name):
    with open(os.path.join(file_name)) as f:
        return [str(r) for r in parse_requirements(f.read())]


setup(
    name='openergy',

    version=version,

    packages=find_packages(),

    author="Geoffroy d'Estaintot",

    author_email="geoffroy.destaintot@openergy.fr",

    long_description=open('README.md').read(),

    install_requires=_get_req_list("requirements-conda.txt"),

    url='https://bitbucket.org/openergy/outil',

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: French",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.4",
    ],
    package_data={'openergy': ['*.txt']},

    include_package_data=True
)
