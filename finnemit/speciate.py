""" Speciation conversions. """

import pkg_resources
import pandas as pd


def speciate(infile, outfile=None):

    year = 2017
    yearnam = str(year)
    tdydate = 'TEST_Speciation_04012019'
    firstday = 1
    lastday = 365

    specfile = pkg_resources.resource_filename("finnemit", "data/speciation.csv")
    speciate = pd.read_csv(specfile)

    sav = speciate['Savanna']
    boreal = speciate['Boreal']
    tempfor = speciate['TempFor']
    tropfor = speciate['TropFor']
    shrub = speciate['Shrub']
    ag = speciate['Crop']

    if outfile is None:
        outfile = re.sub("\\.csv$", "_out.csv", infile)

    fire = pd.read_csv(infile)

    longi = fire['longi']
    lati = fire['lat']
    polyid = fire['polyid']
    fireid = fire['fireid']
    jday = fire['jd']
    lct = fire['lct']
    genveg = fire['genLC']
    CO = fire['CO']
    NOX = fire['NOx']
    NO = fire['NO']
    NO2 = fire['NO2']
    NH3 = fire['NH3']
    SO2 = fire['SO2']
    VOC = fire['NMOC']
    PM25 = fire['PM25']
    PM10 = fire['PM10']
    OC = fire['OC']
    BC = fire['BC']
    area = fire['area']
    bmass = fire['bmass']

    nfires = fire.shape[0]

    # TODO deal with leap years & skipping

    # Convert orignial emissions converted to mole/km2/day
    COemis = CO * 1000. / 28.01
    NH3emis = NH3 * 1000 / 17.03
    NOemis = NO * 1000 / 30.01  # added 11/18/2009
    NO2emis = NO2 * 1000 / 46.01
    SO2emis = SO2 * 1000 / 64.06

    # some are not converted
    NOXemis = NOX
    VOCemis = VOC
    OCemis = OC
    BCemis = BC
    PM25emis = PM25
    PM10emis = PM10

    # TODO: pick up here with a loop
    if genveg in [7, 8, 11, 12]:
        raise ValueError('Invalid vegetation type')

    if genveg[i] == 1:
        convert2MOZ4 = sav
    if genveg[i] eq 2:
        convert2MOZ4 = shrub
    if (genveg[i] eq 3) then convert2MOZ4 = tropfor
    if (genveg[i] eq 4) then convert2MOZ4 = tempfor
    if (genveg[i] eq 5) then convert2MOZ4 = boreal
    if (genveg[i] eq 6) then convert2MOZ4 = tempfor
    if (genveg[i] eq 9) then convert2MOZ4 = ag
