from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("pretreatment_MatrixSimilarityCy.pyx", compiler_directives={'language_level' : "3"}, include_path=['/usr/include/python3.7m'])
)