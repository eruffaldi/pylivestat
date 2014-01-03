
livestat
========

Python module to compute running statistics over data, like when measuring timings from a stream.

Properties:
- count
- min,max,mean
- std and variance
- kurtosis and skewness # allows to measure the "normality of the dataset"

The main class is LiveStat to which data can be appended with append(x). For incremental values the DeltaLiveStat provides an easy to use helper.

Usage:

	from livestat import LiveStat,DeltaLiveStat

	x = LiveStat("optionalname")
	x.append(10)
	x.append(20)
	print x # count is 2

	x = DeltaLiveStat("dt")
	x.append(10)
	x.append(20)
	print x # count is 1 containing the difference

	#also from array
	x.extend([10,20,30,40,50])

Extra Features: 
	
	# the LiveStat objects can be combined for example when performing over different data Windows or in a multiprocessing environment
	x.merge(y) # now x contains the merge of the statistics

	# the LiveStat object can be multipled by scalar or translated, for the objective of performing some unit transformation. All the measures are transformed appropriately
	x + 5
	x * 5

In progress:
- numpy support
- normality test


Related
=========
The faststat package is similar:
	https://pypi.python.org/pypi/faststat/
	https://github.com/doublereedkurt/faststat/


