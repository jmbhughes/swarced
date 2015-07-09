import sys, getopt, os, swarced, pickle, run, time
import numpy as np
import multiprocessing as mp

'''You can execute many ketu runs from the commandline using this program.
Runs should be formatted like:
python multirun.py path_to_query_directory
The query directory should contain all the query pickled dictionaries you wish
to run. There can only be one per EPIC_ID. The output files will be paced in the
same location. 
Using this naming convention, you can only have one query for a particular
epicID in each location or else it will be overwritten!
'''

def main(argv):
    start = time.time()
    query_dir = argv[0]
    qlist = os.listdir(query_dir)
    qlist = [fn for fn in qlist if (".query" in fn)]
    args = [[fn[4:13],2,query_dir + fn] for fn in qlist]
    pool = mp.Pool(processes=mp.cpu_count())
    results = pool.map(run.main, args)
    pool.close()
    pool.join()
    pickle.dump([time.time() - start, results], open(query_dir + "timing.pkl", "wb"))
        
if __name__ == "__main__":
    main(sys.argv[1:])
