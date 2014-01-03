from livestat import *

x = LiveStat("x")
x.append(10)
x.append(20)
x.append(15)

y = LiveStat("y")
y.append(210)
y.append(220)
y.append(215)
print "x",x
print "y",y

#M3 and M4 prevent this: print "sum of x and y",y+x
#M3 and M4 prevent this: print "difference of x and y",x-y
print "merge x and y",y.merge(x)

print "ops"
print "x",x
x += 2
print "x+2",x
#x *= -2
print "(x+2)*-2",x*-2

x = DeltaLiveStat()
x.append(10)
x.append(20)
x.append(15)
print x

X = [0.7481,-0.1924,0.8886,-0.7648,-1.4023,-1.4224,0.4882,-0.1774,-0.1961,1.4193]
matstat = dict(count=len(X),mean=-0.0611,var=0.9162,skewness=-0.0658,kurtosis=1.9194,std=0.9572)
print "MATLAB",matstat    
s = LiveStat("x")
for x in X:
    s.append(x)
print s 
s = LiveStat("x")
s.extend(X)
print s 