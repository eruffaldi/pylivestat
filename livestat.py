#
# Python Livestat module
#
# This module provides a simple mechanism for computing statistics of variables as they are produced.
# In particular: count, mean, std, maximum and minimum, span
#
# Two statistics can be merged together
# The core class is LiveStat that supports numbers
#
# Future: numpy arrays, tuples/lists, so far only scalar
#
#
# Last Updated: 31 December 2013
#
# Emanuele Ruffaldi 2012-2014

from collections import defaultdict
import math
try:
    import numpy
except:
    numpy = None


class LiveStat:
    """ LiveStat allows to compute statistics over variables as they are produced"""
    def __init__(self,name=""):
        """Constructor with optional name, used for printing"""
        self.name = name
        self.dirty = False
        self.reset()
    @property
    def empty(self):
        """Returns true when there is no data"""
        return self.vcount == 0
    @property
    def count(self):
        """Returns the number of items seen by the accumulator"""
        return self.vcount
    @property
    def sum(self):
        """Returns the sum of the values. None if no items"""
        return self.vsum
    @property
    def mean(self):
        """Returns the sample mean of the values. None if no items"""
        return self.vmean
    @property
    def span(self):
        """Returns the range of values. None if no items"""
        if self.vcount == 0:
            return None
        else:
            return self.vmax-self.vmin

    @property
    def variance(self):
        """Returns the sample variance of the values. None if no items"""
        if self.dirty:
            self._finalize()
        return self.vstd2

    @property
    def std(self):
        """Returns the sample standard deviation of the values. None if no items"""
        if self.dirty:
            self._finalize()
        return math.sqrt(self.vstd2)

    def reset(self):
        """Resets the accumulator"""
        self.vmin = None
        self.vmax = None
        self.vmean = None
        self.vstd2 = None
        self.vsum = None
        self.vm2 = None
        self.vcount = None
        self.dirty = False

    def __imul__(self,value):
        """Updates the statistics as if all the input values were (x*value)
        """
        if isinstance(value,LiveStat):
            raise Exception ("Product of Statistics is not supported")
        else:
            if self.vmin is not None:
                # mu(s x) = 1/N sum s x = s/N sum x
                self.vmean *= value
                if value < 0:
                    m = self.vmin
                    M = self.vmax
                    self.vmin = M*value
                    self.vmax = m*value
                else:
                    self.vmin *= value
                    self.vmax *= value
                self.vsum *= value
                # vm2(s x) = sum (s x - mu(s x))^2 = sum (s x - s mu(x))^2 = sum s^2 (x - mu(x))^2 = s^2 sum (x - mu(x))^2 = s^2 vm^2
                self.vm2 *= value*value
                self.dirty = True
        return self

    def __idiv__(self,value):
        """Updates the statistics as if all the input values were (x/value)"""
        if isinstance(value,LiveStat):
            raise Exception ("Ratio of Statistics is not supported")
        else:
            if self.vmin is not None:
                # mu(s x) = 1/N sum s x = s/N sum x
                self.vmean /= value
                if value < 0:
                    m = self.vmin
                    M = self.vmax
                    self.vmin = M/value
                    self.vmax = m/value
                else:
                    self.vmin /= value
                    self.vmax /= value
                self.vsum /= value
                # vm2(s x) = sum (s x - mu(s x))^2 = sum (s x - s mu(x))^2 = sum s^2 (x - mu(x))^2 = s^2 sum (x - mu(x))^2 = s^2 vm^2
                self.vm2 /= value*value
                self.dirty = True
        return self


    def __add__(self,value):
        x = self.clone()
        if isinstance(value,LiveStat):
            x.name = "(" + self.name + "+" + value.name + ")"
        else:
            x.name = "(" + self.name + "+ scalar)"
        x += value
        return x
    def __sub__(self,value):
        x = self.clone()
        if isinstance(value,LiveStat):
            x.name = "(" + self.name + "-" + value.name + ")"
        else:
            x.name = "(" + self.name + "- scalar)"
        x -= value
        return x
    def __mul__(self,value):
        x = self.clone()
        if isinstance(value,LiveStat):
            x.name = "(" + self.name + "*" + value.name + ")"
        else:
            x.name = "(" + self.name + "* scalar)"
        x *= value
        return x
    def __div__(self,value):
        x = self.clone()
        if isinstance(value,LiveStat):
            x.name = "(" + self.name + "/" + value.name + ")"
        else:
            x.name = "(" + self.name + "/ scalar)"
        x /= value
        return x    
    def __iadd__(self,value):
        """Updates the statistics as if all the values were (x+scalar) or (x+value)"""
        if isinstance(value,LiveStat):
            if value.vcount < 1 or self.vcount < 1:
                raise Exception("Cannot sum empty statistics")
            else:
                # sum of two considered pairwise: z_i = stat(x_i + y_i)
                #
                # data have different weights due to number of samples.. TODO
                self.vmin += value.vmin 
                self.vmax += value.vmax
                self.vmean += value.vmean
                self.vsum += value.vsum
                # variance is sum of variance?
                self.vm2 += value.vm2
                self.vcount = min(value.vcount,self.vcount)
                self.dirty = True
        else:
            # constant bias
            if self.vmin is not None:
                self.vmin += value
                self.vmax += value
                self.vmean += value
                self.vsum += self.vcount*value
                self.dirty = True
        return self
    def __isub__(self,value):
        """Updates the statistics as if all the values were (x-value) and (x-y)"""
        if isinstance(value,LiveStat):
            if value.vcount < 1 or self.vcount < 1:
                raise Exception("Cannot sum empty statistics")
            else:
                # sum of two considered pairwise: z_i = stat(x_i - y_i)
                #
                # data have different weights due to number of samples.. TODO
                self.vmin = self.vmin-value.vmax
                self.vmax = self.vmax-value.vmin
                self.vmean -= value.vmean
                self.vsum -= value.vsum
                # variance is sum of variance in any case
                self.vm2 += value.vm2
                self.vcount = min(self.vcount,value.vcount)
                self.dirty = True
        else:
            # constant bias
            if self.vmin is not None:
                self.vmin -= value
                self.vmax -= value
                self.vmean -= value
                self.vsum -= self.vcount*value
                self.dirty = True
        return self    
    def clone(self):
        r = LiveStat(self.name)
        r.copy(self)
        return r
    def copy(self,other):
        """Assignment from the other"""
        if other.vcount == 0:
            self.reset()
        else:
            self.vcount = other.vcount
            self.vmin = other.vmin
            self.vmax = other.vmax
            self.dirty = other.dirty
            self.vstd2 = other.vstd2
            self.vm2 = other.vm2
            self.vmean = other.vmean
            self.vsum = other.vsum
            self.name = other.name
        return self
    def add(self,x):
        """Appends a new item"""
        if self.vcount is None:
            self.vcount = 1
            self.vmin = x
            self.vmax = x
            self.vsum = x
            self.vmean = x
            self.vstd2 = 0
            self.vm2 = 0
            self.dirty = False
        else:
            self.vcount += 1
            # multivalue minimum
            if x < self.vmin:
                self.vmin = x
            if x > self.vmax:
                self.vmax = x
            dvold = x-self.vmean
            self.vmean += dvold/self.vcount # incremental mean (good for vectorial)
            self.vm2 += (x-self.vmean)*dvold # incremental quadratic for variance (good for vectorial)
            self.vsum += x
            self.dirty = True
    def _finalize(self):
        """Private Finalize the interal counter to update the variance"""
        if self.vcount > 1:
            self.vstd2 = self.vm2/(self.vcount-1)
        else:
            self.vstd2 = 0
            self.vmean = 0
        self.dirty = False
    def merge(self,other):
        """Merges the current statistics with the other"""
        if self.empty:            
            self.copy(other)
            return self
        elif other.empty:
            return self
        if(other.vmin < self.vmin):
            self.vmin = other.vmin
        if(other.vmax > self.vmax):
            self.vmax = other.vmax

        vcountold = self.vcount;
        self.vcount += other.vcount;
        self.vsum += other.vsum;

        # merge of mean and m2
        delta = other.vmean-self.vmean;
        self.vmean += delta*other.vcount/self.vcount;
        self.vm2 += other.vm2 + delta*delta*(other.vcount*vcountold)/self.vcount;
        self.dirty = True
        return self
    def __str__(self):
        """String representation"""
        self._finalize()
        np = self.name
        if self.name != "":
            np += ","
        if self.vcount > 0:
            return "LiveStat(%smean=%s,std=%s,min=%s,max=%s,count=%d)" % (np,self.vmean,self.std,self.vmin,self.vmax,self.vcount)
        else:
            return "LiveStat(%sempty)" % np

class DeltaLiveStat(LiveStat):
    """Specialization of the LiveStat that manages differential statistics"""
    def __init__(self,name=""):
        self.last = None
        self.dlast = None
        LiveStat.__init__(self,name)
    def reset(self):        
        """Reset"""
        self.last = None
        LiveStat.reset(self)
    def resetlast(self):
        """Reset only the last, but not the inner statistics. Equivalent to adding None"""
        self.last = None
        self.dlast = 0
    def clone(self):
        r = DeltaLiveStat(self.name)
        r.copy(self)
        return r
    def copy(self,other):
        LiveStat.copy(self,other)
        self.last = other.last
        self.dlast = other.dlast
        return self
    def add(self,x):
        """Adds a new item. If x is None this means to reset the input"""
        if x is None:
            self.last = None
        elif self.last is None:
            self.last = x
            self.dlast = 0
        else:
            self.dlast = x-self.last
            LiveStat.add(self,float(self.dlast))
            self.last = x
    def __str__(self):
        self._finalize()
        np = self.name
        if np != "":
            np += ","
        if self.vcount > 0:
            return "DeltaLiveStat(%smean=%s,std=%s,min=%s,max=%s,count=%d)" % (np,self.vmean,self.std,self.vmin,self.vmax,self.vcount)
        else:
            return "DeltaLiveStat(%sempty)" % np


class Counter:
    """Simple counter class with interface similar to LiveStat"""
    def __init__(self):
        self.c = 0
    @property
    def count(self):
        return self.c
    @property
    def empty(self):
        return self.c == 0
    def add(self,x):
        self.c += x
    def __str__(self):
        return str(self.c)
    def _finalize(self):
        pass
    def divide(self,x):
        self.c /= x

class Histogram:
    """Histogram Class"""
    def __init__(self,name,cz=Counter):
        self.name = name
        self.cz = cz
        self.items = None
        self.count = 0
        self.reset()
    @property
    def empty(self):
        return self.count == 0
    @property
    def casescount(self):
        return len(self.items)
    @property
    def cases(self):
        return sorted(self.items.keys())
    def normalizetotal(self):
        n = self.count
        for v in self.items():
            v.divide(n)
    @property
    def count(self):
        return self.count
    def add(self,x,y=1):
        self.items[x].add(y)
        self.count += 1
    def reset(self):
        self.items = defaultdict(self.cz)
        self.count = 0
    def _finalize(self):
        pass
        
if __name__ == "__main__":

    x = LiveStat("x")
    x.add(10)
    x.add(20)
    x.add(15)

    y = LiveStat("y")
    y.add(210)
    y.add(220)
    y.add(215)
    print "x",x
    print "y",y

    print "sum of x and y",y+x
    print "difference of x and y",x-y
    print "merge x and y",y.merge(x)

    print "ops"
    print "x",x
    x += 2
    print "x+2",x
    #x *= -2
    print "(x+2)*-2",x*-2

    x = DeltaLiveStat()
    x.add(10)
    x.add(20)
    x.add(15)
    print x



