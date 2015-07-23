import os, pickle, bls, time, sys, data, scoop, socket
from astropy.io import ascii
import numpy as np
import multiprocessing as mp


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
        print("SKIPPING " + str(epicid))

def single_test(epicid):
    return blswrap(epicid, campaign, initial_time)

if os.path.isfile(save_path):
    raise IOError("File already exists! Please give a different save_path")

if __name__ == "__main__":
    script, all_lc_path, directory, campaign, initial_time, save_path = sys.argv

    pickle.dump([],open(save_path,"wb"))
    all_lc_list = ascii.read(all_lc_path)
    all_lc_epic = [int(lc.split("/")[-1][4:13]) for lc in all_lc_list['filenames'] if ".fits" in lc]

    start = time.time()
    results = list(scoop.futures.map_as_completed(single_test,all_lc_epic))
    pool.join()
    end = time.time()
    print("Beginning save")
    pickle.dump(results,open(save_path,"wb"))
    print("Finished in " + str(int(end-start)) + " seconds")
