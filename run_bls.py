'''A wrapper for BLS
How to run:
    1. generate a list of lightcurves with absolute paths in a text file
    2. Make sure retrieve in data.py is suited for your use (i.e. it is
    lightcurves from Foreman-Mackey formatting, not straight from STSCI)
    3. Determine an initial_time that you want to include all lightcurve data
    after from (e.g. in Campaign 2 the first several data points before 2456900
    were always bad. If you give that time in JD anything before then is not
    included in the BLS analysis
    4. Decide where to save the files. 
    5. nbins is the number of windows in the BLS code, used 5 for now. 
    6. Run from the command line:
        python run_bls.py /path/to/your/list/of/lcs #ofCAMPAIGN INITIAL_TIME
        /where/to/save/the/output nbin

        ex:
        python run_bls.py /k2_data/all_c2_lcs 2 2456900 /k2_data/c2_eb/bls.pkl
        5

Note the output is a pickled list of tuples. Where each tuple is the
abbreviated BLS response for that EPIC: (EPIC, (best_period, best_power, depth,
q, in1, in2)) where 
best_period is the best-fit period in the same units as time,
best_power is the power at best_period,
depth is the depth of the transit at best_period,
q is the fractional transit duration,
in1 is the bin index at the start of transit, and
in2 is the bin index at the end of transit.
 '''

import os, pickle, bls, time, sys, data
from astropy.io import ascii
import numpy as np
import multiprocessing as mp

script, all_lc_path, directory, campaign, initial_time, save_path, nbin = sys.argv

def blswrap(epicid, campaign, initial_time):
    global nbin
    try:
        start = time.time()
        initial_time = float(initial_time)
        t, f = data.retrieve(epicid, campaign, directory=directory)
        if initial_time != 0:
            t, f = t[t>initial_time], f[t>initial_time]
        u, v = np.zeros(len(t)), np.zeros(len(f))
        #minfreq, dfreq, nfreq = 1/70., 4.082799167108228e-06, 1000000
        minfreq, dfreq, nfreq = 0.015, 2.0437359493152146e-05,100000
        #nbin = 100
        minduration, maxduration = 0.01, 0.05
        results = bls.eebls(t, f, u, v, nfreq, minfreq, dfreq, nbin, minduration, maxduration)
        end = time.time()
        print(epicid, end - start)
        return epicid, results[1:]
    except:
        print("SKIPPING " + str(epicid))

def single_test(epicid):
    return blswrap(epicid, campaign, initial_time)

if os.path.isfile(save_path):
    raise IOError("File already exists! Please give a different save_path")

pickle.dump([],open(save_path,"wb"))
all_lc_list = ascii.read(all_lc_path)
all_lc_epic = [int(lc.split("/")[-1][4:13]) for lc in all_lc_list['filenames'] if ".fits" in lc]

start = time.time()
pool = mp.Pool(processes=mp.cpu_count())
results = pool.map(single_test, all_lc_epic)
pool.close()
pool.join()
end = time.time()
print("Beginning save")
pickle.dump(results,open(save_path,"wb"))
print("Finished in " + str(int(end-start)) + " seconds")
