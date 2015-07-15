def validate_eb(epicid, campaign, result_path):
    print("-" * 79)
    result = pickle.load(open(result_path, "r"))
    #print(result)
    print("Recovered Period: {0:5.2f}, t0: {5:5.5f}, Depth: {1:5.2f}, Depth_s2n: {2:5.2f}, Depth_var: {3:5.4f}, Phic_same: {4:5.2f}".format(result['peaks'][0]['period'], result['peaks'][0]['depth'],result['peaks'][0]['depth_s2n'], 1/result['peaks'][0]['depth_ivar'],result['peaks'][0]['phic_same'],result['peaks'][0]['t0']))
    #result['peaks'][0][
    period, center = result['peaks'][0]['period'], result['peaks'][0]['t0']
    plot_lc(epicid, campaign)
    plot_periodogram(epicid, result)
    phase, flux = plot_phase(epicid,campaign,period,center)
    print("-" * 79)
    return phase, flux