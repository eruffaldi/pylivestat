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
    version = "0.1",
    author = "Emanuele Ruffaldi",
    author_email = "e.ruffaldi@sssup.it",
    description = ("Computing descriptive statistics over streaming data"),
    license = "BSD",
    keywords = "statistics kurtosis skewness live variance",
    #url = "http://packages.python.org/an_example_pypi_project",
    packages=['livestat'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Math",
        "License :: OSI Approved :: Apache 2 License",
    ],
)
