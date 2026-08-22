from setuptools import Extension, setup

setup(
    name="incompatible-ext-fixture",
    version="0.1.0",
    ext_modules=[Extension("incompatible_ext", ["incompatible_ext.c"])],
)
