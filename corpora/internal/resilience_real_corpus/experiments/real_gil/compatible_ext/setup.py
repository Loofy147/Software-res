from setuptools import Extension, setup

setup(
    name="compatible-ext-fixture",
    version="0.1.0",
    ext_modules=[Extension("compatible_ext", ["compatible_ext.c"])],
)
