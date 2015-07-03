import sys, getopt, os, swarced, pickle, run

#Executes ketu from the command line in a multiprocessing fashion

def main(argv):
    query_dir = argv
    qlist = os.listdir(query_dir)
    args = np.vstack(([fn[4:-2] for fn in qlist],#epicid
                      np.zeros(len(qlist)),#campaign number
                      qlist))#query list
    pool = mp.Pool(processes=6)
    pool.map(run.main, args)
    pool.close()
    pool.join()

if __name__ == "__main__":
    main(sys.argv[1:])
