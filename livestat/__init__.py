"""Python Live Statistics Module

.. moduleauthor:: Emanuele Ruffaldi <e.ruffaldi@sssup.it>

This module provides a simple mechanism for computing statistics of variables as they are produced.
In particular: count, mean, std, maximum and minimum, span

"""
from livestat import *

__all__ = ["LiveStat", "DeltaLiveStat","Counter","Histogram"]
