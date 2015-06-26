import sys, getopt
import swarced

#Executes ketu from the command line

def main(argv):
    epicID, campaign, query_path = argv
    epicID, campaign = str(epicID), str(campaign)
    #Format the local path (could be a download step)
    path = "/k2_data/lightcurves/" + "c" + campaign + "/"
    path = path + epicID[0:4] + "0000/" + epicID[4:6] + "000/"
    #Generate the filename
    fn = "ktwo" + epicID + "-c0" + campaign + "_lpd-lc.fits"
    fn = path + fn #omit if downloaded
    #read in the query as a dictionary (for ketu)
    with open(query_path) as fd:
        query = dict(line.strip().split(None, 1) for line in fd)
    query['light_curve_file'] = fn
    peaks = swarced.analyze(query).response['peaks']
    for i in range(len(peaks)):
        out =  str(i) + " " 
        peak = peaks[i]
        out = out + peak['depth'] + " " + peak['depth_ivar']
        out = out + peak['duration'] + " " + peak['period']
        out = out + peak['s2n'] + " " + peak['t0'] + "/n"
    print(out)

if __name__ == "__main__":
    main(sys.argv[1:])
