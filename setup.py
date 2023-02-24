from setuptools import setup
  
setup(
    name='procyclingstats',
    version='0.1',
    description='A Python API wrapper for ProCyclingStats.com',
    author='Martin Madzin',
    author_email='',
    packages=['procyclingstats'],
    install_requires=[
        'requests',
    ],
)
