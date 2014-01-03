# Emanuele Ruffaldi 2013-2014
#
# Compact functions for incrementally computing descriptive statistics properties
# Everything is function oriented and stored using tuples  (n,mean,M2,M3,M4)
#   Mk = sum (x-mean)^k
#   muk = Mk/n
#   
# Allows to compute: mean,std/var,kurtosis,skewness
# Look at livestat.LiveStat for an object oriented organization
#
# Central Moments:
# - The nth central moment is translation-invariant: mu_n(X + c) = mu_n(X)
# - The nth central moment is homogeneous of degree n: mu_n(c X) = c^n mu_n(X)
# - for n in 1:3 we have additivity: mu_n(X+Y) = mu_n(X) + mu_n(Y) if indep
#
# Variance is the 2nd central moment
#
# Standardized Moments: scale invariant because is mu_k/sigma^k
# Skewness is sm of order 3, ku is sm of order 4
#
# Initial Versiom: 31st December 2013
import math

# moments of single value
def momentsofscalar(x):
    return (1,x,0,0,0)

def momentsempty():
    return (0,0,0,0,0)

# update moments as of: s*x with s scalar
def momentsscale(mA,s):
    # sum (x-mu)^n
    # sum (s x - s mu)^n = sum s^n (x - mu)^n
    return (mA[0],s*mA[1],s*s*mA[2],(s**3)*mA[3],(s**4)*mA[4])

# update moments as of: x+t
def momentstranslate(mA,t):
    return (mA[0],mA[1]+t,mA[2],mA[3],mA[4])

# combines two moments description: (count,m1,m2,m3,m4) and combines them
#
# based on general rule for moment combine: Terriberry, Timothy B. (2007), Computing Higher-Order Moments Online
# 
def momentscombine(mA,mB):
    """
    # for the moment disable optimization
    if mB[0] == 0:
        return mA
    elif mA[0] == 0:
        return mB
    elif mB[0] == 1:
        return momentsaddscalar(mA,mB[1])
    elif mA[0] == 1:
        return momentsaddscalar(mB,mA[1])
    else:
    """
    delta = float(mB[1]-mA[1])
    delta2 = delta**2
    delta3 = delta2*delta
    delta4 = delta3*delta
    nA = float(mA[0])
    nB = float(mB[0])
    nAB = nA*nB
    nAA = nA*nA
    nBB = nB*nB
    nX = nA+nB
    nXX = nX*nX
    nXXX = nXX*nX
    m1X = mA[1]+delta*nB/nX
    m2X = mA[2]+mB[2]+delta2*nAB/nX
    m3X = mA[3]+mB[3]+delta3*(nAB*(nA-nB))/nXX + 3*delta*(nA*mB[2]-nB*mA[2])/nX
    m4X = mA[4]+mB[4]+delta4*(nAB*(nAA-nAB+nBB)/nXXX)+6*(delta2)*(nAA*mB[2]+nBB*mA[2])/nXX+4*delta*(nA*mB[3]-nB*mA[3])/nX
    return (mA[0]+mB[0],m1X,m2X,m3X,m4X)

# adds scalar to moments mA
# momentsaddscalar(mA,x) == momentscombine(mA,momentsofscalar(x))
def momentsaddscalar(mA,x):
    delta = float(x-mA[1])
    delta2 = delta**2
    delta3 = delta2*delta
    delta4 = delta3*delta
    nA = float(mA[0])
    nAA = nA*nA
    nX = nA+1
    nXX = nX*nX
    nXXX = nXX*nX
    m1X = mA[1]+delta/nX
    m2X = mA[2]+delta2*nA/nX # same: (x-mA[1])*(x-m1X)
    m3X = mA[3]+delta3*(nA*(nA-1))/nXX - 3*delta*mA[2]/nX
    m4X = mA[4]+delta4*(nA*(nAA-nA+1)/nXXX)+6*(delta2)*mA[2]/nXX-4*delta*mA[3]/nX
    return (mA[0]+1,m1X,m2X,m3X,m4X)

# converts the moments tuple to statistics as dictionary
def moments2stat(mA):
    n,mean,M2,M3,M4 = mA
    nf = float(n)
    v = M2/(nf-1)
    sigma = math.sqrt(v)
    popv = M2/nf # biased

    mu4 = M4/nf
    mu2 = M2/nf
    mu3 = M3/nf
    sk = mu3/(mu2**1.5)
    ku = mu4/(mu2**2)
    return dict(count=n,mean=mean,std=sigma,var=v,popvar=popv,kurtosis=ku,skewness=sk)

# converts statistics dictionary to tuple, inverse of moments2stat
def stat2moments(mA):
    n = int(mA["count"])
    mean = mA["mean"]
    nf = float(n)

    # TODO: workout inconsistent multiple definitions. Now var >> std >> popvar
    if "var" in mA:
        M2 = mA["var"]*(nf-1)
        sigma = math.sqrt(mA["var"])
    elif "std" in mA:
        M2 = (mA["std"]**2)*(nf-1)
        sigma = mA["std"]
    elif "popvar" in mA:
        M2 = mA["popvar"]*nf
        sigma = math.sqrt(mA["popvar"])
    else:
        M2 = 0
        sigma = 0
    sk = mA.get("skewness",0)
    ku = mA.get("kurtosis",0)
    
    mu2 = M2/nf
    M3 = nf*sk*(mu2**1.5)
    M4 = nf*ku*(mu2**2)
    return (n,mean,M2,M3,M4)

# given sequence of number computes moments at once
def momentsfromdata(data):
    # first the means
    n = float(len(data))
    mean = 0
    for x in data:
        mean += x/n        
    M2 = 0
    M3 = 0
    M4 = 0
    for x in data:
        d = x-mean
        M2 += (d**2)
        M3 += (d**3)
        M4 += (d**4)
    # Kurtosis = vm3/ssize
    return (len(data),mean,M2,M3,M4)


# Jarque Beta Test of Guassianity based on kurtosis and skewness
# REQUIRES chiinv
def jarquebetatest(mA,alpha):
    if type(mA) != dict:
        mA = moments2stat(mA)
    n = mA["count"]
    JB = n/6*(mA["skewness"]**2 + 1/4*((mA["kurtosis"]-3)**2))
    # normal test with chi distribution with 2 DOF using 


if __name__ == "__main__":
    X = [0.7481,-0.1924,0.8886,-0.7648,-1.4023,-1.4224,0.4882,-0.1774,-0.1961,1.4193]
    matstat = dict(count=len(X),mean=-0.0611,var=0.9162,skewness=-0.0658,kurtosis=1.9194,std=0.9572)
    print "MATLAB",matstat
    # kurtosis(X) = 1.9194
    # skewness(X) = -0.0658
    # var(X) = 0.9162
    # mean(X) = -0.0611
    # JB = length(X)/6*(skewness(X)^2+1/4*(kurtosis(X)-3)^2); % 0.4937
    # chi2gof(X)
    #
    # %http://www.mathworks.com/help/stats/jbtest.html
    # alpha=0.05;
    # h = jbtest(X,alpha)
    # chi2inv(1-alpha,2) < JB
    print "full data"
    m = momentsfromdata(X)
    print "- full:",moments2stat(m)

    print "combining two parts data"
    map = momentsfromdata(X[0:len(X)/2])
    mbp = momentsfromdata(X[len(X)/2:])
    mabp = momentscombine(map,mbp)
    print "- joint:",moments2stat(mabp)    

    print "by scalar"
    mi = momentsempty()
    for x in X:
        mi = momentsaddscalar(mi,x)
    print "- scalar:",moments2stat(mi)

    print "combining two parts scalar"
    ma = momentsempty()
    mb = momentsempty()
    for x in X[0:len(X)/2]:
        ma = momentsaddscalar(ma,x)
    for x in X[len(X)/2:]:
        mb = momentsaddscalar(mb,x)
    mab = momentscombine(ma,mb)
    print "- scalar joint:",moments2stat(mab)


    print "back op",m
    mr = stat2moments(moments2stat(m))
    print "- back is",mr
