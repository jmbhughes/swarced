import os, pickle, bls, time, sys, data
from astropy.io import ascii
import numpy as np
import multiprocessing as mp

def blswrap_broad(epicid, campaign, initial_time,directory):
    #try:
        start = time.time()
        initial_time = float(initial_time)
        t, f = data.retrieve(epicid, campaign, directory=directory)
        if initial_time != 0:
            t, f = t[t>initial_time], f[t>initial_time]
        u, v = np.zeros(len(t)), np.zeros(len(f))
        #minfreq, dfreq, nfreq = 1/70., 4.082799167108228e-06, 1000000
        minfreq, dfreq, nfreq = 0.015, 2.0437359493152146e-05,100000
        nbin = 100
        minduration, maxduration = 0.01, 0.05
        results = bls.eebls(t, f, u, v, nfreq, minfreq, dfreq, 10, minduration, maxduration)
        end = time.time()
        print(epicid, end - start)
        return epicid, results[1:]
    #except:
    #    print("SKIPPING epicid")

        
def blswrap_fine(epicid, campaign, initial_time,directory):
    try:
        start = time.time()
        initial_time = float(initial_time)
        t, f = data.retrieve(epicid, campaign, directory=directory)
        if initial_time != 0:
            t, f = t[t>initial_time], f[t>initial_time]
        u, v = np.zeros(len(t)), np.zeros(len(f))
        minfreq, dfreq, nfreq = 1/70., 4.082799167108228e-06/10, 1000000*10
        #minfreq, dfreq, nfreq = 0.015, 2.0437359493152146e-05,100000
        nbin = 100
        minduration, maxduration = 0.01, 0.05
        results = bls.eebls(t, f, u, v, nfreq, minfreq, dfreq, 10, minduration, maxduration)
        end = time.time()
        print(epicid, end - start)
        return epicid, results[1:]
    except:
        print("SKIPPING epicid")

        

#def single_test(epicid):
#    return blswrap(epicid, campaign, initial_time)
