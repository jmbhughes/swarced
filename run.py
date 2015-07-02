import sys, getopt
import swarced
import pickle

#Executes ketu from the command line

def main(argv):
    epicID, campaign, query_path = argv
    epicID, campaign = str(epicID), str(campaign)
    query = pickle.load(open(query_path, 'r'))
    result = swarced.analyze(query)
    pickle.dump(result.response, open("k2_epic" + epicID + ".pkl", "wb"))

if __name__ == "__main__":
    main(sys.argv[1:])
