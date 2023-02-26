from setuptools import setup

with open("README.rst", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="procyclingstats",
    version="0.1.1",
    license="MIT",
    description="A Python API wrapper for procyclingstats.com",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Martin Madzin",
    author_email="madzin.m@gmail.com",
    packages=["procyclingstats"],
    url="https://github.com/themm1/procyclingstats",
    keywords="cycling cycling-stats procyclingstats scraper html-parsing" +
        " sports-analytics",
    install_requires=[
        "requests",
        "selectolax"
    ],
)
