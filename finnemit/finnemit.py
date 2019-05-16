# -*- coding: utf-8 -*-
""" FINN emissions model utilities.

This script is a translation of IDL code used to estimate wildfire emissions
for a variety of compounds.

"""

import re
import datetime
import pandas as pd
import numpy as np
import pkg_resources


def get_emissions(infile, outfile=None, fuelin=None, emisin=None):
    """Get emissions estimates with FINN

    Args:
        infile (str) - path to input file
        outfile (str) - optional path to output file. If None, then this is
            constructed by appending '_output' to the input filename
        fuelin (str) - optional path to a fuel loading file. This must be
            formatted like the file finnemit/data/fuel-loads.csv
        emisin (str) - optional path to an emissions file. This must be
            formatted like the file finnemit/data/emission-factors.csv

    Returns:
        A dictionary summarizing emission totals, and writes a file to outfile.
    """

    # USER INPUTS --- EDIT DATE AND SCENARIO HERE - this is for file naming
    # NOTE: ONLY LCT - Don't really need this
    scen = 1
    scename = "scen1"

    # SETTING UP VARIABLES To CHECK TOTALS AT THE END OF The FILE

    # Calculating the total biomass burned in each genveg for output file
    TOTTROP = 0.0
    TOTTEMP = 0.0
    TOTBOR = 0.0
    TOTSHRUB = 0.0
    TOTCROP = 0.0
    TOTGRAS = 0.0
    # Calculating total area in each genveg for output log file
    TOTTROParea = 0.0
    TOTTEMParea = 0.0
    TOTBORarea = 0.0
    TOTSHRUBarea = 0.0
    TOTCROParea = 0.0
    TOTGRASarea = 0.0
    # CALCULATING TOTAL CO and PM2.5 for crops
    TOTCROPCO = 0.0
    TOTCROPPM25 = 0.0

    # ASSIGN FUEL LOADS, EMISSION FACTORS FOR GENERIC LAND COVERS AND REGIONS
    # FUEL LOADING FILES
    #  02/04/2019 - removed texas code for this section and pasted in old code
    #  from v1.5 -- going back to global fuel loadings
    #  READ IN FUEL LOADING FILE
    #  02/08/2019: ALL FUEL INPUTS ARE IN g/m2
    if fuelin is None:
        fuelin = pkg_resources.resource_filename("finnemit",
                                                 "data/fuel-loads.csv")
    fuel = pd.read_csv(fuelin)

    #   Set up fuel arrays
    tffuel = fuel["Tropical Forest"].values  # tropical forest fuels
    tefuel = fuel["Temperate Forest"].values  # temperate forest fuels
    bffuel = fuel["Boreal Forest"].values  # boreal forest fuels
    wsfuel = fuel["Woody Savanna"].values  # woody savanna fuels
    grfuel = fuel["Savanna and Grasslands"].values  # grassland and savanna
    # NOTE: Fuels read in have units of g/m2 DM

    # 02/08/2019
    # READ in LCT Fuel loading file from prior Texas FINN study
    # This is a secondary fuel loading file for use in US ONLY
    lctfuelin = pkg_resources.resource_filename(
        "finnemit", "data/land-cover-gm2.csv"
    )
    lctfuel = pd.read_csv(lctfuelin)
    lcttree = lctfuel["final TREE"].values
    lctherb = lctfuel["final HERB"].values

    # EMISSION FACTOR FILE
    if emisin is None:
        emisin = pkg_resources.resource_filename(
            "finnemit", "data/emission-factors.csv"
        )
    emis = pd.read_csv(emisin)

    #   Set up Emission Factor Arrays
    COEF = emis["CO"].values  # CO emission factor
    NMOCEF = emis["NMOC"].values  # NMOC emission factor (added 10/20/2009)
    NOXEF = emis["NOXasNO"].values  # NOx emission factor
    NOEF = emis["NO"].values  # NO emission factors (added 10/20/2009)
    NO2EF = emis["NO2"].values  # NO2 emission factors (added 10/20/2009)
    SO2EF = emis["SO2"].values  # SO2 emission factor
    PM25EF = emis["PM25"].values  # PM2.5 emission factor
    OCEF = emis["OC"].values  # OC emission factor
    BCEF = emis["BC"].values  # BC emission factor
    NH3EF = emis["NH3"].values  # NH3 emission factor
    PM10EF = emis["PM10"].values  # PM10 emission factor (added 08/18/2010)

    print("Finished reading in fuel and emission factor files")

    # READIN IN FIRE AND LAND COVER INPUT FILE (CREATED WITH PREPROCESSOR)
    if outfile is None:
        outfile = re.sub("\\.csv$", "_out.csv", infile)
    map = pd.read_csv(infile)
    map = map[map["v_regnum"].notnull()]

    nfires = map.shape[0]

    polyid = map["polyid"].values
    fireid = map["fireid"].values

    lat = map["cen_lat"].values
    lon = map["cen_lon"].values
    date = map["acq_date_lst"].values
    area = map["area_sqkm"].values
    # CW: Added March 05, 2015  -- NEED set the field

    tree = map["v_tree"].values
    herb = map["v_herb"].values
    bare = map["v_bare"].values

    lct = map["v_lct"].values
    flct = map["f_lct"].values

    globreg = map["v_regnum"].values

    # Total Number of fires input in original input file
    numorig = nfires

    # Added 08/25/08: removed values of -9999 from VCF inputs
    tree[tree < 0] = 0
    herb[herb < 0] = 0
    bare[bare < 0] = 0

    # Calculate the total cover from the VCF product
    # (CHECK TO MAKE SURE PERCENTAGES ADD TO 100%)
    totcov = tree + herb + bare
    # number of records where total coverate is less than 100%
    nummissvcf = sum(totcov < 98)
    assert nummissvcf == 0

    # parse dates
    dates = [datetime.datetime.strptime(d, "%Y-%m-%d") for d in date]

    jd = np.array([d.timetuple().tm_yday for d in dates])  # julian date
    mo = np.array([d.month for d in dates])

    ngoodfires = len(jd)
    print("the number of fires = {}".format(ngoodfires))

    # Set up Counters
    # These are identifying how many fires are in urban areas,
    # or have unidentified VCF or LCT values -->
    # purely for statistics and quality assurance purposes
    lct0 = 0
    spixct = 0
    antarc = 0
    allbare = 0
    genveg0 = 0
    bmass0 = 0
    vcfcount = 0
    vcflt50 = 0
    confnum = 0  # added 08/25/08
    overlapct = 0  # added 02/29/2009
    urbnum = 0  # added 10/20/2009

    # yk: scenuse# actual algorithm being used when falling back to,
    # eg. LCT, for various rasons
    # CW - 02/04/2019 - don't know what this is??
    scenuse = np.ones(ngoodfires) * -99

    # Set totals to 0.0 (FOR OUTPUT LOG FILE)
    COtotal = 0.0
    NMOCtotal = 0.0
    NOXtotal = 0.0
    SO2total = 0.0
    PM25total = 0.0
    OCtotal = 0.0
    BCtotal = 0.0
    NH3total = 0.0
    PM10total = 0.0
    AREAtotal = 0.0  # added 06/21/2011
    bmasstotal = 0.0  # Addded 06/21/2011

    # ****************************************************************************
    # START LOOP OVER ALL FIRES: CALCULATE EMISSIONS
    # ****************************************************************************

    df_rows = list()

    # Start loop over all fires in input file
    for j in range(
        ngoodfires
    ):  # edited this to have ngoodfires instead of nfires on 02.23.2009
        #
        # ##################################################
        #   QA PROCEDURES FIRST
        # ##################################################
        # 1) Correct for VCF product issues
        #   1a) First, correct for GIS processing errors:
        #    Scale VCF product to sum to 100. (DON'T KNOW IF THIS IS AN ISSUE
        #        WITH V2 - BUT LEAVING IN)
        if totcov[j] > 101.0 and totcov[j] < 240.0:
            vcfcount = vcfcount + 1
            tree[j] = tree[j] * 100.0 / totcov[j]
            herb[j] = herb[j] * 100.0 / totcov[j]
            bare[j] = bare[j] * 100.0 / totcov[j]
            totcov[j] = bare[j] + herb[j] + tree[j]

        if totcov[j] < 99.0 and totcov[j] >= 50.0:
            vcfcount = vcfcount + 1
            tree[j] = tree[j] * 100.0 / totcov[j]
            herb[j] = herb[j] * 100.0 / totcov[j]
            bare[j] = bare[j] * 100.0 / totcov[j]
            totcov[j] = bare[j] + herb[j] + tree[j]

        # Second, If no data are assigned to the grid,: scale up, still
        if totcov[j] < 50.0 and totcov[j] >= 1.0:
            vcflt50 = vcflt50 + 1
            tree[j] = tree[j] * 100.0 / totcov[j]
            herb[j] = herb[j] * 100.0 / totcov[j]
            bare[j] = bare[j] * 100.0 / totcov[j]
            totcov[j] = bare[j] + herb[j] + tree[j]

        #   1b) Fires with 100% bare cover or VCF not identified or total cover
        #    is 0,-9999: reassign cover values based on LCT assignment
        if (
            totcov[j] >= 240.0 or totcov[j] < 1.0 or bare[j] == 100
        ):  # this also include where VCF see water (values = 253)
            allbare = allbare + 1
            if lct[j] >= 15:
                continue
                # Skip fires that are all bare and
                # have no LCT vegetation

            if lct[j] <= 5:  # Assign forest to the pixel
                tree[j] = 60.0
                herb[j] = 40.0
                bare[j] = 0.0

            if (
                (lct[j] >= 6 and lct[j] <= 8) or lct[j] == 11 or lct[j] == 14
            ):  # Assign woody savanna to the pixel
                tree[j] = 50.0
                herb[j] = 50.0
                bare[j] = 0.0

            if lct[j] in [9, 10, 12, 13, 16]:  # Assign as grassland
                tree[j] = 20.0
                herb[j] = 80.0
                bare[j] = 0.0

        # 2) Remove fires with no LCT assignment or in water bodies or
        # snow/ice assigned by LCT
        # 02/22/2019 - REMOVED ASSIGNMENT BASED ON GLC
        if lct[j] >= 17 or lct[j] <= 0 or lct[j] == 15:
            # Added Snow/Ice on 10/20/2009
            lct0 = lct0 + 1
            continue

        # yk: make sure that genveg got assigned somewhere for whatever
        # mechanism.
        genveg = -9999

        # SCENARIO #1 = LCT ONLY
        # Assign Generic land cover to fire based on
        #   global location and lct information
        # Generic land cover codes (genveg) are as follows:
        # 1 grassland
        # 2 shrub
        # 3 Tropical Forest
        # 4 Temperate Forest
        # 5 Boreal Forest
        # 6 Temperate Evergreen Forest
        # 7 Pasture
        # 8 Rice
        # 9 Crop (generic)
        # 10  Wheat
        # 11  Cotton
        # 12  Soy
        # 13  Corn
        # 14  Sorghum
        # 15  Sugar Cane

        # yk: record which algorithm used
        scenuse[j] = 1

        # 1) Grasslands and Savanna
        if lct[j] in [9, 10, 11, 14, 16]:
            genveg = 1

        # 2) Woody Savanna/ Shrubs
        if lct[j] >= 6 and lct[j] <= 8:
            genveg = 2

        # 3) Croplands
        if lct[j] == 12:
            genveg = 9

        # 4) Urban
        if lct[j] == 13:  #: assign genveg based on VCF cover in the pixel
            # and reset the lct value (for emission factors)
            urbnum = urbnum + 1
            if tree[j] < 40:
                genveg = 1  # grasslands
                lct[j] = 10  # set to grassland

            if tree[j] >= 40 and tree[j] < 60:
                genveg = 2  # woody savannas
                lct[j] = 8  # set to woody savanna

            if tree[j] >= 60:  # assign forest based on latitude
                if (
                    lat[j] > 50
                ):  # 10/19/2009: Changed the latitude border to 50degrees N
                    # (from 60 before) and none in S. Hemisphere
                    genveg = 5
                    lct[j] = 1  # set to evergreen needleleaf forest
                else:
                    if lat[j] >= -30 and lat[j] <= 30:
                        genveg = 3
                    else:
                        genveg = 4
                    lct[j] = 5  # set to mixed forest

        # 5) Forests (based on latitude)
        if lct[j] == 2:
            if lat[j] >= -23.5 and lat[j] <= 23.5:
                genveg = 3  # Tropical Forest
            else:
                genveg = 4  # Tropical Forest

        if lct[j] == 4:
            genveg = 4  # Temperate Forest

        if lct[j] == 1:  # Evergreen Needleleaf forests
            # (06/20/2014 Changed this)
            if lat[j] > 50.0:
                genveg = 5
            else:
                genveg = 6  # 6/20/2014: Changed this
        # Assign Boreal for Lat > 50# Evergreen needlelead for all else

        if (
            lct[j] == 3
        ):  # deciduous Needleleaf forests -- June 20, 2014: Left LCT = 3 same
            # as old code. ONLY Changed Evergreen needleleaf forests
            if lat[j] > 50.0:
                genveg = 5
            else:
                genveg = 4
                # 10/19/2009: Changed the latitude border to 50degrees N
                # (from 60 before) and none in S. Hemisphere
                # Assign Boreal for Lat > 50# Temperate for all else

        if lct[j] == 5:  # Mixed Forest, Assign Fuel Load by Latitude
            if lat[j] > 50:  # 10/19/2009: Changed lat border to 50degrees N
                # (from 60 before) and none in S. Hemisphere
                genveg = 5
            # yk: tropics -23.5 to +23.5
            if lat[j] >= -23.5 and lat[j] <= 23.5:
                genveg = 3
            else:
                genveg = 4

        # ####################################################
        # Assign Fuel Loads based on Generic land cover
        #   and global region location
        #   units are in g dry mass/m2
        # ####################################################

        reg = globreg[j] - 1  # locate global region, get index
        if reg <= -1 or reg > 100:
            print(
                "Removed fire number:",
                j,
                "Something is WRONG with global regions and fuel loads",
                "Globreg =",
                globreg[j],
            )
            continue

        # bmass now gets calculated as a function of tree cover, too.
        if genveg == 9:
            bmass1 = 902.0  # 02/08/2019 changed from 1200. based on
            # Akagi, van Leewuen and McCarty
            # For Brazil from Elliott Campbell, 06/14/2010
            # specific to sugar case
            if (lon[j] <= -47.323 and lon[j] >= -49.156) and (
                lat[j] <= -20.356 and lat[j] >= -22.708
            ):
                bmass1 = 1100.0

        if genveg == 1:
            bmass1 = grfuel[int(reg)]
        if genveg == 2:
            bmass1 = wsfuel[int(reg)]
        if genveg == 3:
            bmass1 = tffuel[int(reg)]
        if genveg in [4, 6]:
            bmass1 = tefuel[
                int(reg)
            ]  # Added in new genveg == 6 here (06/20/2014)
        if genveg == 5:
            bmass1 = bffuel[int(reg)]

        if genveg == 0:
            print(
                "Removed fire number:",
                j,
                "Something is WRONG with generic vegetation. genveg = 0",
            )
            genveg0 = genveg0 + 1
            continue

        # DEC. 09, 2009: Added correction
        # Assign boreal forests in Southern Asia the biomass density of the
        # temperate forest for the region
        if genveg == 5 and globreg[j] == 11:
            bmass1 = tefuel[int(reg)]

        if bmass1 == -1:
            print("Fire number:", j, " removed. bmass assigned -1!")
            print(
                "    genveg =",
                genveg,
                " and globreg = ",
                globreg[j],
                " and reg = ",
                reg,
            )
            bmass0 = bmass0 + 1
            continue

        # Assign Burning Efficiencies based on Generic
        #   land cover (Hoezelmann et al. [2004] Table 5
        # ASSIGN CF VALUES (Combustion Factors)
        if tree[j] > 60:  # FOREST
            # Values from Table 3 Ito and Penner [2004]
            CF1 = 0.30  # Live Woody
            CF3 = 0.90  # Leafy Biomass
            CF4 = 0.90  # Herbaceous Biomass
            CF5 = 0.90  # Litter Biomass
            CF6 = 0.30  # Dead woody

        if 40 < tree[j] <= 60:  # WOODLAND
            # yk: fixed based on Ito 2004
            # CF3 = exp(-0.013*(tree[j]/100.))
            CF3 = np.exp(-0.013 * tree[j])  # Apply to all herbaceous fuels
            CF1 = 0.30  # Apply to all coarse fuels in woodlands
            # Ito and Penner [2004]

        if tree[j] <= 40:  # GRASSLAND
            CF3 = 0.98  # Range is between 0.44 and 0.98 - Assumed UPPER LIMIT!

        # Calculate the Mass burned of each classification
        # (herbaceous, woody, and forest)
        # These are in units of g dry matter/m2
        # bmass is the total burned biomass
        # Mherb is the Herbaceous biomass burned
        # Mtree is the Woody biomass burned

        pctherb = herb[j] / 100.0
        pcttree = tree[j] / 100.0
        coarsebm = bmass1
        herbbm = grfuel[int(reg)]

        # ###################################################################
        # 02/08/2019
        # Include updated fuel loading for North America (Global Region 1)
        # based on earlier Texas project (FCCS Fuel Loadings)
        # ##################################################################

        # Determine if in North America
        if globreg[j] == 1:
            # Assign coarse and herb biomass based on lct
            coarsebm = lcttree[lct[j]]
            herbbm = lctherb[lct[j]]

        #######################################################################
        # DETERMINE BIOMASS BURNED
        #  Grasslands
        if tree[j] <= 40:
            bmass = (pctherb * herbbm * CF3) + (pcttree * herbbm * CF3)
            # Assumed here that litter biomass = herbaceous biomass and that
            #   the percent tree
            #   in a grassland cell contributes to fire fuels... CHECK THIS!!!
            # Assuming here that the duff and litter around trees burn

        # Woodlands
        if 40 < tree[j] <= 60:
            bmass = (pctherb * herbbm * CF3) + (
                pcttree * (herbbm * CF3 + coarsebm * CF1)
            )

        # Forests
        if tree[j] > 60:
            bmass = (pctherb * herbbm * CF3) + (
                pcttree * (herbbm * CF3 + coarsebm * CF1)
            )

        # ####################################################
        # Assign Emission Factors based on LCT code
        # ####################################################

        # CHRISTINE EDITING YO'S CODE THAT ISN'T COMPILING
        # # Edited again 02/04/2019
        if genveg == -1 or genveg == 0:
            print("Fire_emis> ERROR genveg not set correctly: ")
            print(" scen (orig/used): ", scen, scenuse[j])
            print(" lc_new (M/G/F/FC/T/TC): ", [lct[j]])
            print(" tree: ", tree[j])
            print(" genveg: ", genveg)
            print("Fire_emis> ERROR stopping...")
            raise ValueError

        # Reassigned emission factors based on LCT,
        # not genveg for new emission factor table
        if lct[j] == 1:
            index = 0
        if lct[j] == 2:
            index = 1
        if lct[j] == 3:
            index = 2
        if lct[j] == 4:
            index = 3
        if lct[j] == 5:
            index = 4
        if lct[j] == 6:
            index = 5
        if lct[j] == 7:
            index = 6
        if lct[j] == 8:
            index = 7
        if lct[j] == 9:
            index = 8
        if lct[j] == 10:
            index = 9
        if lct[j] == 11:
            index = 10
        if lct[j] == 12:
            index = 11
        if lct[j] == 14:
            index = 12
        if lct[j] == 16:
            index = 13
        if genveg == 6:
            index = 14
        # Added this on 06/20/2014 to account for temperate evergreen forests

        # ####################################################
        # Calculate Emissions
        # ####################################################
        # Emissions = area*BE*BMASS*EF
        # Convert units to consistent units
        areanow = area[j] * 1.0e6  # convert km2 --> m2
        bmass = bmass / 1000.0  # convert g dm/m2 to kg dm/m2

        # CW: MAY 29, 2015: Scale grassland and cropland fire areas
        # 02/04/2019 - removing ths scaling for crop/grassland fires.
        # See FINNv1.5 - Amber suggested this.
        #   Removing this scaling for now.
        #   if genveg == 1 or genveg >= 8: areanow = 0.75*areanow

        # cw: 04/22/2015 - remove bare fraction from total area
        #     REMOVE on 06/10/2015
        #     Uncommented this 02/04/2019
        areanow = areanow - (
            areanow * (bare[j] / 100.0)
        )  # remove bare area from being burned (04/21/2015)

        # CALCULATE EMISSIONS kg
        CO = COEF[index] * areanow * bmass / 1000.0
        NMOC = NMOCEF[index] * areanow * bmass / 1000.0
        NOX = NOXEF[index] * areanow * bmass / 1000.0
        NO = NOEF[index] * areanow * bmass / 1000.0
        NO2 = NO2EF[index] * areanow * bmass / 1000.0
        SO2 = SO2EF[index] * areanow * bmass / 1000.0
        PM25 = PM25EF[index] * areanow * bmass / 1000.0
        OC = OCEF[index] * areanow * bmass / 1000.0
        BC = BCEF[index] * areanow * bmass / 1000.0
        NH3 = NH3EF[index] * areanow * bmass / 1000.0
        PM10 = PM10EF[index] * areanow * bmass / 1000.0

        # Calculate totals for log file
        bmassburn = bmass * areanow  # kg burned
        bmasstotal = bmassburn + bmasstotal  # kg

        if genveg == 3:
            TOTTROP = TOTTROP + bmassburn
            TOTTROParea = TOTTROParea + areanow

        if genveg == 4:
            TOTTEMP = TOTTEMP + bmassburn
            TOTTEMParea = TOTTEMParea + areanow

        if genveg == 5:
            TOTBOR = TOTBOR + bmassburn
            TOTBORarea = TOTBORarea + areanow

        if genveg == 2:
            TOTSHRUB = TOTSHRUB + bmassburn
            TOTSHRUBarea = TOTSHRUBarea + areanow

        if genveg >= 9:
            TOTCROP = TOTCROP + bmassburn
            TOTCROParea = TOTCROParea + areanow
            TOTCROPCO = TOTCROPCO + CO
            TOTCROPPM25 = TOTCROPPM25 + PM25

        if genveg == 1:
            TOTGRAS = TOTGRAS + bmassburn
            TOTGRASarea = TOTGRASarea + areanow

        # units being output are in kg/day/fire
        df_rows.append(
            (
                lon[j],
                lat[j],
                polyid[j],
                fireid[j],
                date[j],
                jd[j],
                lct[j],
                globreg[j],
                genveg,
                tree[j],
                herb[j],
                bare[j],
                areanow,
                bmass,
                CO,
                NOX,
                NO,
                NO2,
                NH3,
                SO2,
                NMOC,
                PM25,
                PM10,
                OC,
                BC,
            )
        )

        # Calculate Global Sums
        COtotal = CO + COtotal
        NMOCtotal = NMOC + NMOCtotal
        NOXtotal = NOXtotal + NOX
        SO2total = SO2total + SO2
        PM25total = PM25total + PM25
        OCtotal = OCtotal + OC
        BCtotal = BCtotal + BC
        NH3total = NH3total + NH3
        PM10total = PM10total + PM10
        AREAtotal = AREAtotal + areanow  # m2

    # Write output to csv
    index = [
        "longi",
        "lat",
        "polyid",
        "fireid",
        "date",
        "jd",
        "lct",
        "globreg",
        "genLC",
        "pcttree",
        "pctherb",
        "pctbare",
        "area",
        "bmass",
        "CO",
        "NOx",
        "NO",
        "NO2",
        "NH3",
        "SO2",
        "NMOC",
        "PM25",
        "PM10",
        "OC",
        "BC",
    ]
    out_df = pd.DataFrame(df_rows, columns=index)
    out_df = out_df.sort_values(by=["jd"])
    out_df.to_csv(outfile)

    # collect summary json
    summary_dict = {
        "input_file": infile,
        "output_file": outfile,
        "scenario": scename,
        "emissions_file": emisin,
        "fuel_load_file": fuelin,
        "num_fires_total": numorig,
        "num_fires_processed": ngoodfires,
        "num_urban_fires": urbnum,
        "num_removed_for_overlap": overlapct,
        "num_lct<=0|lct>17": lct0,
        "num_antarctic": antarc,
        "num_bare_cover": allbare,
        "num_skipped_genveg_problem": genveg0,
        "num_skipped_bmass_assignment": bmass0,
        "num_scaled_to_100": vcfcount,
        "num_vcf<50": vcflt50,
        "num_fires_skipped": spixct
        + lct0
        + antarc
        + allbare
        + genveg0
        + bmass0
        + confnum,
        "GLOBAL TOTAL (Tg) biomass burned (Tg)": bmasstotal / 1.0e9,
        "Total Temperate Forests (Tg)": TOTTEMP / 1.0e9,
        "Total Tropical Forests (Tg)": TOTTROP / 1.0e9,
        "Total Boreal Forests (Tg)": TOTBOR / 1.0e9,
        "Total Shrublands/Woody Savannah(Tg)": TOTSHRUB / 1.0e9,
        "Total Grasslands/Savannas (Tg)": TOTGRAS / 1.0e9,
        "Total Croplands (Tg)": TOTCROP / 1.0e9,
        "TOTAL AREA BURNED (km2)": AREAtotal / 1000000.0,
        "Total Temperate Forests (km2)": TOTTEMParea / 1000000.0,
        "Total Tropical Forests (km2)": TOTTROParea / 1000000.0,
        "Total Boreal Forests (km2)": TOTBORarea / 1000000.0,
        "Total Shrublands/Woody Savannah(km2)": TOTSHRUBarea / 1000000.0,
        "Total Grasslands/Savannas (km2)": TOTGRASarea / 1000000.0,
        "Total Croplands (km2)": TOTCROParea / 1000000.0,
        "TOTAL CROPLANDS CO (kg)": TOTCROPCO,
        "TOTAL CROPLANDS PM2.5 (kg)": TOTCROPPM25,
        "CO": COtotal / 1.0e9,
        "NMOC": NMOCtotal / 1.0e9,
        "NOx": NOXtotal / 1.0e9,
        "SO2": SO2total / 1.0e9,
        "PM2.5": PM25total / 1.0e9,
        "OC": OCtotal / 1.0e9,
        "BC": BCtotal / 1.0e9,
        "NH3": NH3total / 1.0e9,
        "PM10": PM10total / 1.0e9,
    }
    return summary_dict
