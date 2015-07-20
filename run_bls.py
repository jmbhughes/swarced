import os, pickle, bls, time, sys, data
from astropy.io import ascii
import numpy as np
import multiprocessing as mp

script, all_lc_path, directory, campaign, initial_time, save_path = sys.argv

def blswrap(epicid, campaign, initial_time):
    try:
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
    except:
        print("SKIPPING epicid")

def single_test(epicid):
    return blswrap(epicid, campaign, initial_time)

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
