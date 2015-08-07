'''This is a wrapper for a ketu pipeline run'''

import ketu

def analyze(query,cache=False):
    '''Pass a target through the ketu pipeline
    Key Terms:
    query-- a dictionary with query terms from either build_query or get_query
    cache-- if False does not cache, otherwise designate directory to cache at
    Return:
    A pipeline result object for examination
    '''
    if cache == False:
        pipe = ketu.k2.Data(cache=False)
        pipe = ketu.k2.Likelihood(pipe,cache=False)
        pipe = ketu.OneDSearch(pipe,cache=False)
        pipe = ketu.TwoDSearch(pipe,cache=False)
        pipe = ketu.PeakDetect(pipe,cache=False)
    else:#do cache!
        pipe = ketu.k2.Data(basepath=cache)
        pipe = ketu.k2.Likelihood(pipe)
        pipe = ketu.OneDSearch(pipe)
        pipe = ketu.TwoDSearch(pipe)
        pipe = ketu.PeakDetect(pipe)
    result = pipe.query(**query)
    return result