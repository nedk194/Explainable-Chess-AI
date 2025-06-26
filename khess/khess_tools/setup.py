import sys
import os
from pybind11 import get_cmake_dir
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

os.environ["CC"] = "g++"
os.environ["CXX"] = "g++"
# os.environ["CC"] = "clang++"
# os.environ["CXX"] = "clang++"

if "MSC" in sys.version:  # MSVC detected
    extra_compile_args = ["/O2", "/Wall", "/std:c++20", "/DNDEBUG"]
    libraries = []  # Remove 'gomp' (MSVC does not support it)
else:  # GCC or Clang
    extra_compile_args = [
        "-O3", "-Wall", "-march=native", "-mtune=native", "-std=gnu++20",
        "-ffast-math", "-fargument-noalias-global", "-fopenmp", "-DNDEBUG"
    ]
    libraries = ["gomp"]

# need to change the relative path to sources when building from parent folder
khess_tools = Pybind11Extension('khess_tools',
                                sources=['khess_tools\khess_tools.cpp',
                                         'lib\surge\src/types.cpp',
                                         'lib\surge\src/tables.cpp',
                                         'lib\surge\src\position.cpp'],
                                include_dirs=['lib\pybind11',
                                              'lib\surge\src'],

                                extra_compile_args=extra_compile_args,
                                # extra_compile_args=[
                                # '-O3', '-march=native', '-mtune=native', '-ffast-math', '-fopenmp',  '-DNDEBUG'],
                                libraries=libraries
                                # libraries=["iomp5"]
                                )


setup(name='KHESS',
      version='2.0',
      description='Fast routines for KHESS.',
      ext_modules=[khess_tools])
