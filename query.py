def build_query(epicID, campaign, directory,basispath,catalogpath,time_spacing=0.02, durations=[0.05,0.1,0.2]\
 ,min_period = 0.5,max_period=70.0,initial_time = 1975.,tail=''):
    '''Allows the construction of a customized query
        Key-words:
            epicID--the designation for your object
            campaign--which K2 campaign the object is in
            directory--this is the path to where the lightcurves folder is: on linux '/k2_data/'; on macs '/Volumes/k2_data/'
            basispath--the path to the basis catalog of eigenlightcurves "/k2_data/elcs/c2-norm.h5"
            catalogpath-the path to the catalog for EPIC "/k2_data/catalogs/epic.h5"
            time_spacing--the grid resolution in days
            durations--the tranist durations in days to test
            min_period--the minimum period in days to test
            max_period--the maximum period in days to test
    '''
    epicIDstr, campaignstr = str(epicID), str(campaign)
    path = get_lc_path(epicID, campaign, directory, tail=tail)
    
	q = dict(
        light_curve_file=path,
        basis_file = basispath,
        nbasis = 150,
        initial_time = initial_time,
        catalog_file = catalogpath, 
        time_spacing = time_spacing,
        durations = durations,
        min_period = min_period,
        max_period = max_period,
    )
    return q

def get_planet_default(epicID, campaign,directory):
    '''Format a default query for the ketu pipeline
    key-words:
        epicID--the EPIC designation for your target
        campaign--the K2 campaign of that EPIC designation
        directory--this is the path to where the lightcurves folder is: on linux '/k2_data/'; on macs '/Volumes/k2_data/'
    '''
    epicIDstr, campaignstr = str(epicID), str(campaign)
    #Default path to lightcurve
    path = get_lc_path(epicID, campaign, directory)
    #Construct the dictionary query object
    q = dict(
        light_curve_file = path,
        initial_time=1940.,
        basis_file= "/k2_data/elcs/c1.h5",
        nbasis=150,
        catalog_file= "/k2_data/catalogs/epic.h5",
        time_spacing=0.02,
        durations=[0.05, 0.1, 0.2],
        min_period=0.5,
        max_period=70.0,
    )
    if campaign == "0":
        q['basis_file'] = "/k2_data/elcs/c0.h5"
    elif campaign == "2":
        q['basis_file'] = "/k2_data/elcs/c2-norm.h5"
    else:
        q['basis_file'] = "/k2_data/elcs/c?-norm.h5"
    return q

def save(query, f):
    '''Saves a query in a pickled format with name f'''
    pickle.dump(query, f)
