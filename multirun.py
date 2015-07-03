import sys, getopt, os, swarced, pickle, run
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
    query_dir = argv[0]
    #print(query_dir)
    qlist = os.listdir(query_dir)
    args = [[fn[4:-2],0,query_dir + fn] for fn in qlist]
    pool = mp.Pool(processes=6)
    pool.map(run.main, args)
    pool.close()
    pool.join()

if __name__ == "__main__":
    main(sys.argv[1:])
