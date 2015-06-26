def find_phase(time, period, center):
    return (time  - center) % period / period

def clip_eclipses(phase, period, sep, pwid, swid):
    ph, sh = 0.5*(pwid + 0.01), 0.5*(swid+0.01)
    mask = (phase > ph)  * (phase < 1-ph) * ((phase < sep - sh) | (phase > sep + sh))
    return mask
