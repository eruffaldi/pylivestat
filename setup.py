import os
from setuptools import setup

# Utility function to read the README file.  
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "livestat",
    version = "0.1.1",
    author = "Emanuele Ruffaldi",
    author_email = "emanuele.ruffaldi@gmail.com",
    description = ("Computing descriptive statistics over streaming data"),
    license = "BSD",
    keywords = "statistics kurtosis skewness live variance",
    #url = "http://packages.python.org/an_example_pypi_project",
    packages=['livestat','examples'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: Apache Software License",
    ],
)
