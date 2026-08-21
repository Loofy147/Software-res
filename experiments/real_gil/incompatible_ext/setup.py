from pathlib import Path
from setuptools import Extension, setup

HERE = Path(__file__).parent.resolve()

setup(
    name="incompatible-ext-fixture",
    version="0.1.0",
    ext_modules=[Extension("incompatible_ext", [str(HERE / "incompatible_ext.c")])],
)
