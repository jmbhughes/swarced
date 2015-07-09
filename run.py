import os, pickle, sys, getopt, swarced

'''You can execute a ketu run from the commandline using this program.
Runs should be formatted like:
python run.py EPIC_ID CAMPAIGN_NUMBER PATH_TO_QUERY
The path to query should have an appropriate query file. You can see the 
form_query.ipynb notebook to build those. The result will be a pickled
file with just the results from the last step of the ketu pipeline. 

Using this naming convention, you can only have one query for a particular
epicID in each location or else it will be overwritten!

'''

def main(argv):
    epicID, campaign, query_path = argv
    print(epicID, campaign, query_path)
    epicID, campaign = str(epicID), str(campaign)
    query = pickle.load(open(query_path, 'r'))
    print(query)
    print(type(query))
    print("reached1")
    result = swarced.analyze(query, cache=False)
    print("reached2")
    out_path = "/".join(query_path.split("/")[:-1]) + "/" + query_path.split("/")[-1:][0].split(".")[0] + ".result"
    pickle.dump(result.response, open(out_path, 'wb'))

if __name__ == "__main__":
    main(sys.argv[1:])
