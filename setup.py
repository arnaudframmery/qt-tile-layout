from setuptools import setup

with open('./README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="pyqt5-tile-layout",
    version="0.1.6",
    author="Arnaud Frammery",
    author_email="arnaud.frammery@gmail.com",
    description="A tile layout for PyQt5",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="GPL3",
    url="https://github.com/arnaudframmery/qt-tile-layout",
    packages=["QTileLayout"],
    install_requires=["PyQt5~=5.12"],
)
