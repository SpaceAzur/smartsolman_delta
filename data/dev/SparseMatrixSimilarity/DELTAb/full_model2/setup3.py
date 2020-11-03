# cython: language_level=3, boundscheck=False
from distutils.core import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension("pretreatment_MatrixSimilarityCy", ["pretreatment_MatrixSimilarityCy.pyx"],
                include_dirs=["/usr/include/python3.7m"])
]

setup(
    ext_modules = cythonize(extensions)
)