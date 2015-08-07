'''This tool runs ketu on a directory of files using a network of computers
the query_dir is the path to the directory where all the query files are for your run
the skipfile is just a text file to note any lightcurves skipped over
campaign is the campaign of all the data... all data must be from one campaign
Script to be launched with:  
python -m scoop --tunnel --hostfile ../hosts.txt --python-interpreter 'python' -p /mnt/k2_data/swarced/ scoop_ketu.py /mnt/k2_data/injection_trial_three/ /mnt/k2_data/injection_trial_three/skips 2
python -m scoop --tunnel --hostfile /path/to/host/file --python-interpreter 'python' -p /path/to/this/directory/on/remote/computer scoop_ketu.py /path/to/directory/of/queries/on/remote/computer /path/to/skip/file/on/remote/computer campaign
'''

import scoop, socket, time,sys
import numpy as np 
sys.path.append("../")
import getopt, os, swarced, pickle, run_ketu, time

if __name__ == "__main__":
    start = time.time()
    print("Script begun")
    argv = sys.argv[1:]
    query_dir,skipfile,campaign = argv[0], argv[1],argv[2]
    campaign = int(campaign)
    #print(skipfile)
    #print("start")
    #f = open(skipfile,'w')
    #f.write("test")
    #f.close()
    #print("end")
    try:
        print("Appending skip file")
        f = open(skipfile,"a")
        f.close()
    except:
        print("Making new skip file")
        f = open(skipfile,'w')
        print("Done making new")
        f.close()
    print("testing file saving")
    pickle.dump([], open(query_dir + "timing.pkl", "wb"))
    #Get all the content from the query_directory
    print("Formulating query list")
    content_list = os.listdir(query_dir)
    #print(content_list)
    #Separate out the .result and .query files
    result_list = [fn for fn in content_list if (".result" in fn)]
    print(result_list)
    query_list = np.array([fn for fn in content_list if (".query" in fn)])
    #print(query_list)
    #make a mask for which .query files don't have a .result file
    not_run = np.array([(query.split(".")[0] + ".result" not in result_list) for query in query_list])
    #print(not_run)
    query_list = query_list[not_run]
    #print(query_list)
    #Format the arguments of epicID, campaign, and absolute path to each query file for the remaining queries
    print("Formatting arguments")
    args = [[fn[4:13], campaign, query_dir + fn, skipfile] for fn in query_list]
    print("Starting scoop run!")
    returnValues = list(scoop.futures.map_as_completed(run_ketu.main, args))
    print("Finished scoop run!")
    pickle.dump([time.time() - start, returnValues], open(query_dir + "timing.pkl", "wb"))
    for message in returnValues:
        print "%s" % message