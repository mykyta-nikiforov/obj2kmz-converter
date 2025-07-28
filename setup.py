#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="obj2kmz-converter",
    version="1.0.0",
    author="Mykyta Nikiforov",
    description="Convert 3D models from OBJ format to KMZ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mykyta-nikiforov/obj2kmz-converter",
    py_modules=[
        "convert_obj_to_kmz",
        "pipeline", 
        "assimp_converter",
        "georeferencing",
        "kmz_generator",
        "z_offset_utils",
        "obj_parser",
        "errors"
    ],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "obj2kmz=convert_obj_to_kmz:main",
            "obj2kmz-convert=convert_obj_to_kmz:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.xml", "*.txt", "*.md"],
    },
) 