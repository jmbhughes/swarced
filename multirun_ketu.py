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
    query_dir,skipfile,campaign = argv[0], argv[1],argv[2]
    campaign = int(campaign)
    f = open(skipfile,"wb")
    f.close()
    #Get all the content from the query_directory
    content_list = os.listdir(query_dir)
    #Separate out the .result and .query files
    result_list = [fn for fn in content_list if (".result" in fn)]
    query_list = np.array([fn for fn in content_list if (".query" in fn)])
    #make a mask for which .query files don't have a .result file
    not_run = np.array([(query.split(".")[0] + ".result" not in result_list) for query in query_list])
    query_list = query_list[not_run]
    #Format the arguments of epicID, campaign, and absolute path to each query file for the remaining queries
    args = [[fn[4:13], campaign, query_dir + fn, skipfile] for fn in query_list]
    #Farm them to multiprocessing
    pool = mp.Pool(processes=mp.cpu_count())
    results = pool.map(run.main, args)
    pool.close()
    pool.join()
    pickle.dump([time.time() - start, results], open(query_dir + "timing.pkl", "wb"))
        
if __name__ == "__main__":
    main(sys.argv[1:])
