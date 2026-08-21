from pathlib import Path
from setuptools import Extension, setup

HERE = Path(__file__).parent.resolve()

setup(
    name="compatible-ext-fixture",
    version="0.1.0",
    ext_modules=[Extension("compatible_ext", [str(HERE / "compatible_ext.c")])],
)
