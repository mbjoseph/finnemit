""" Speciation conversions. """

import pkg_resources
import pandas as pd
import re


def speciate(infile, outfile=None, sfile=None):
    """Get speciated estimates with FINN

    Args:
        infile (str) - path to input file (this should be an outfile file
            written by the get_emissions() function).
        outfile (str) - optional path to output file. If None, then this is
            constructed by appending '_species' to the input filename.
        sfile (str) - optional path to a speciation file. This must be
            formatted like the file finnemit/data/speciation.csv.

    Returns:
        A dictionary summarizing emission totals, and writes a file to outfile.
    """
    if sfile is None:
        sfile = pkg_resources.resource_filename("finnemit", "data/speciation.csv")
    speciate = pd.read_csv(sfile)

    sav = speciate["Savanna"]
    boreal = speciate["Boreal"]
    tempfor = speciate["TempFor"]
    tropfor = speciate["TropFor"]
    shrub = speciate["Shrub"]
    ag = speciate["Crop"]

    if outfile is None:
        outfile = re.sub("\\.csv$", "_species.csv", infile)

    fire = pd.read_csv(infile)
    longi = fire["longi"]
    lati = fire["lat"]
    polyid = fire["polyid"]
    fireid = fire["fireid"]
    jday = fire["jd"]
    lct = fire["lct"]
    genveg = fire["genLC"]
    CO = fire["CO"]
    NOX = fire["NOx"]
    NO = fire["NO"]
    NO2 = fire["NO2"]
    NH3 = fire["NH3"]
    SO2 = fire["SO2"]
    VOC = fire["NMOC"]
    PM25 = fire["PM25"]
    PM10 = fire["PM10"]
    OC = fire["OC"]
    BC = fire["BC"]
    area = fire["area"]
    bmass = fire["bmass"]

    nfires = fire.shape[0]

    # Convert orignial emissions converted to mole/km2/day
    COemis = CO * 1000.0 / 28.01
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

    # set up empty speciated VOC arrays
    APINemis = [None] * nfires
    BENZENEemis = [None] * nfires
    BIGALKemis = [None] * nfires
    BIGENEemis = [None] * nfires
    BPINemis = [None] * nfires
    BZALDemis = [None] * nfires
    C2H2emis = [None] * nfires
    C2H4emis = [None] * nfires
    C2H6emis = [None] * nfires
    C3H6emis = [None] * nfires
    C3H8emis = [None] * nfires
    CH2Oemis = [None] * nfires
    CH3CH2OHemis = [None] * nfires
    CH3CHOemis = [None] * nfires
    CH3CNemis = [None] * nfires
    CH3COCH3emis = [None] * nfires
    CH3COOHemis = [None] * nfires
    CH3OHemis = [None] * nfires
    CRESOLemis = [None] * nfires
    GLYALDemis = [None] * nfires
    HCNemis = [None] * nfires
    HCOOHemis = [None] * nfires
    HONOemis = [None] * nfires
    HYACemis = [None] * nfires
    ISOPemis = [None] * nfires
    LIMONemis = [None] * nfires
    MACRemis = [None] * nfires
    MEKemis = [None] * nfires
    MGLYemis = [None] * nfires
    MVKemis = [None] * nfires
    MYRCemis = [None] * nfires
    PHENOLemis = [None] * nfires
    TOLUENEemis = [None] * nfires
    XYLENEemis = [None] * nfires
    XYLOLemis = [None] * nfires

    for i in range(nfires):
        if genveg[i] in [7, 8, 11, 12]:
            raise ValueError("Invalid vegetation type")

        if genveg[i] == 1:
            convert2MOZ4 = sav
        if genveg[i] == 2:
            convert2MOZ4 = shrub
        if genveg[i] == 3:
            convert2MOZ4 = tropfor
        if genveg[i] == 4:
            convert2MOZ4 = tempfor
        if genveg[i] == 5:
            convert2MOZ4 = boreal
        if genveg[i] == 6:
            convert2MOZ4 = tempfor
        if genveg[i] == 9:
            convert2MOZ4 = ag

        # Speciate VOC emissoins.
        # VOC is in kg and the output of this is mole MOZ4 species
        # 0 APIN
        # 1 BENZENE
        # 2 BIGALK
        # 3 BIGENE
        # 4 BPIN
        # 5 BZALD
        # 6 C2H2
        # 7 C2H4
        # 8 C2H6
        # 9 C3H6
        # 10  C3H8
        # 11  CH2O
        # 12  CH3CH2OH
        # 13  CH3CHO
        # 14  CH3CN
        # 15  CH3COCH3
        # 16  CH3COOH
        # 17  CH3OH
        # 18  CRESOL
        # 19  GLYALD
        # 20  HCN
        # 21  HCOOH
        # 22  HONO
        # 23  HYAC
        # 24  ISOP
        # 25  LIMON
        # 26  MACR
        # 27  MEK
        # 28  MGLY
        # 29  MVK
        # 30  MYRC
        # 31  PHENOL
        # 32  TOLUENE
        # 33  XYLENE
        # 34  XYLOL
        APINemis[i] = VOC[i] * convert2MOZ4[0]
        BENZENEemis[i] = VOC[i] * convert2MOZ4[1]
        BIGALKemis[i] = VOC[i] * convert2MOZ4[2]
        BIGENEemis[i] = VOC[i] * convert2MOZ4[3]
        BPINemis[i] = VOC[i] * convert2MOZ4[4]
        BZALDemis[i] = VOC[i] * convert2MOZ4[5]
        C2H2emis[i] = VOC[i] * convert2MOZ4[6]
        C2H4emis[i] = VOC[i] * convert2MOZ4[7]
        C2H6emis[i] = VOC[i] * convert2MOZ4[8]
        C3H6emis[i] = VOC[i] * convert2MOZ4[9]
        C3H8emis[i] = VOC[i] * convert2MOZ4[10]
        CH2Oemis[i] = VOC[i] * convert2MOZ4[11]
        CH3CH2OHemis[i] = VOC[i] * convert2MOZ4[12]
        CH3CHOemis[i] = VOC[i] * convert2MOZ4[13]
        CH3CNemis[i] = VOC[i] * convert2MOZ4[14]
        CH3COCH3emis[i] = VOC[i] * convert2MOZ4[15]
        CH3COOHemis[i] = VOC[i] * convert2MOZ4[16]
        CH3OHemis[i] = VOC[i] * convert2MOZ4[17]
        CRESOLemis[i] = VOC[i] * convert2MOZ4[18]
        GLYALDemis[i] = VOC[i] * convert2MOZ4[19]
        HCNemis[i] = VOC[i] * convert2MOZ4[20]
        HCOOHemis[i] = VOC[i] * convert2MOZ4[21]
        HONOemis[i] = VOC[i] * convert2MOZ4[22]
        HYACemis[i] = VOC[i] * convert2MOZ4[23]
        ISOPemis[i] = VOC[i] * convert2MOZ4[24]
        LIMONemis[i] = VOC[i] * convert2MOZ4[25]
        MACRemis[i] = VOC[i] * convert2MOZ4[26]
        MEKemis[i] = VOC[i] * convert2MOZ4[27]
        MGLYemis[i] = VOC[i] * convert2MOZ4[28]
        MVKemis[i] = VOC[i] * convert2MOZ4[29]
        MYRCemis[i] = VOC[i] * convert2MOZ4[30]
        PHENOLemis[i] = VOC[i] * convert2MOZ4[31]
        TOLUENEemis[i] = VOC[i] * convert2MOZ4[32]
        XYLENEemis[i] = VOC[i] * convert2MOZ4[33]
        XYLOLemis[i] = VOC[i] * convert2MOZ4[34]

    # Save output as csv file
    out_data = {
        "day": jday,
        "polyid": polyid,
        "fireid": fireid,
        "genveg": genveg,
        "lati": lati,
        "longi": longi,
        "area": area,
        "bmass": bmass,
        "CO": COemis,
        "NOx": NOXemis,
        "NO": NOemis,
        "NO2": NO2emis,
        "SO2": SO2emis,
        "NH3": NH3emis,
        "PM25": PM25emis,
        "OC": OCemis,
        "BC": BCemis,
        "PM10": PM10emis,
        "NMOC": VOCemis,
        "APIN": APINemis,
        "BENZENE": BENZENEemis,
        "BIGALK": BIGALKemis,
        "BIGENE": BIGENEemis,
        "BPIN": BPINemis,
        "BZALD": BZALDemis,
        "C2H2": C2H2emis,
        "C2H4": C2H4emis,
        "C2H6": C2H6emis,
        "C3H6": C3H6emis,
        "C3H8": C3H8emis,
        "CH2O": CH2Oemis,
        "CH3CH2OH": CH3CH2OHemis,
        "CH3CHO": CH3CHOemis,
        "CH3CN": CH3CNemis,
        "CH3COCH3": CH3COCH3emis,
        "CH3COOH": CH3COOHemis,
        "CH3OH": CH3OHemis,
        "CRESOL": CRESOLemis,
        "GLYALD": GLYALDemis,
        "HCN": HCNemis,
        "HCOOH": HCOOHemis,
        "HONO": HONOemis,
        "HYAC": HYACemis,
        "ISOP": ISOPemis,
        "LIMON": LIMONemis,
        "MACR": MACRemis,
        "MEK": MEKemis,
        "MGLY": MGLYemis,
        "MVK": MVKemis,
        "MYRC": MYRCemis,
        "PHENOL": PHENOLemis,
        "TOLUENE": TOLUENEemis,
        "XYLENE": XYLENEemis,
        "XYLOL": XYLOLemis,
    }

    out_df = pd.DataFrame(data=out_data)
    out_df.to_csv(outfile)

    # Generate log
    logfile_name = re.sub("\\.csv$", "_log.txt", outfile)
    with open(logfile_name, "w") as log:
        log.write(" " + "\n")
        log.write("The input file was: " + infile + "\n")
        log.write("The speciation file was: " + sfile + "\n")
        log.write(" " + "\n")
        log.write("Original from fire emissions model before speciation" + "\n")
        log.write(
            "The total CO emissions (moles, Tg) =  "
            + str(sum(COemis))
            + ","
            + str(sum(CO) / 1.0e9)
            + "\n"
        )
        log.write(
            "The total NO emissions (moles, Tg) =  "
            + str(sum(NOemis))
            + ","
            + str(sum(NO) / 1.0e9)
            + "\n"
        )
        log.write(
            "The total NOx emissions (Tg) = " + str(sum(NOX) / 1.0e9) + "\n"
        )
        log.write(
            "The total NO2 emissions (moles, Tg) = "
            + str(sum(NO2emis))
            + ","
            + str(sum(NO2) / 1.0e9)
            + "\n"
        )
        log.write(
            "The total SO2 emissions (moles, Tg) = "
            + str(sum(SO2emis))
            + ","
            + str(sum(SO2) / 1.0e9)
            + "\n"
        )
        log.write(
            "The total NH3 emissions (moles, Tg) = "
            + str(sum(NH3emis))
            + ","
            + str(sum(NH3) / 1.0e9)
            + "\n"
        )
        log.write(
            "The total VOC emissions (Tg) = " + str(sum(VOC) / 1.0e9) + "\n"
        )
        log.write(
            "The total OC emissions (Tg) = " + str(sum(OCemis) / 1.0e9) + "\n"
        )
        log.write(
            "The total BC emissions (Tg) = " + str(sum(BCemis) / 1.0e9) + "\n"
        )
        log.write(
            "The total PM10 emissions (Tg) = "
            + str(sum(PM10emis) / 1.0e9)
            + "\n"
        )
        log.write(
            "The total PM2.5 emissions (Tg) = "
            + str(sum(PM25emis) / 1.0e9)
            + "\n"
        )
        log.write(" " + "\n")
        log.write("SUMMARY FROM MOZART4 speciation" + "\n")
        log.write(
            "The total BIGENE emissio (moles) = " + str(sum(BIGENEemis)) + "\n"
        )
        log.write(
            "The total C2H6 emissions (moles) = "
            + str(sum(C2H6emis))
            + ", and in Tg = "
            + str(sum(C2H6emis) * 30.07 / 1.0e12)
            + "\n"
        )
        log.write(
            "The total MEK emissions (moles) = " + str(sum(MEKemis)) + "\n"
        )
        log.write(
            "The total TOLUENE emiss (moles) = "
            + str(sum(TOLUENEemis))
            + ", and in Tg = "
            + str(sum(TOLUENEemis) * 90.1 / 1.0e12)
            + "\n"
        )
        log.write(
            "The total CH2O emissions (moles) = "
            + str(sum(CH2Oemis))
            + ", and in Tg = "
            + str(sum(CH2Oemis) * 30.3 / 1.0e12)
            + "\n"
        )
        log.write(
            "The total HCOOH emissions (moles) = "
            + str(sum(HCOOHemis))
            + ", and in Tg = "
            + str(sum(HCOOHemis) * 47.02 / 1.0e12)
            + "\n"
        )
        log.write(
            "The total C2H2 emissions (moles) = "
            + str(sum(C2H2emis))
            + ", and in Tg = "
            + str(sum(C2H2emis) * 26.04 / 1.0e12)
            + "\n"
        )
        log.write(
            "The total GLYALD emissions (moles) = "
            + str(sum(GLYALDemis))
            + "\n"
        )
        log.write(
            "The total ISOPRENE emissions (moles) = "
            + str(sum(ISOPemis))
            + ", and in Tg = "
            + str(sum(ISOPemis) * 68.12 / 1.0e12)
            + "\n"
        )
        log.write(
            "The total HCN emissions (moles) = "
            + str(sum(HCNemis))
            + ", and in Tg = "
            + str(sum(HCNemis) * 27.025 / 1.0e12)
            + "\n"
        )
        log.write(
            "The total CH3CN emissions (moles) = "
            + str(sum(CH3CNemis))
            + ", and in Tg = "
            + str(sum(CH3CNemis) * 41.05 / 1.0e12)
            + "\n"
        )
        log.write(
            "The total CH3OH emissions (moles) = "
            + str(sum(CH3OHemis))
            + ", and in Tg = "
            + str(sum(CH3OHemis) * 32.04 / 1.0e12)
            + "\n"
        )
        log.write(
            "The total C2H4 emissions (moles) = "
            + str(sum(C2H4emis))
            + ", and in Tg = "
            + str(sum(C2H4emis) * 28.05 / 1.0e12)
            + "\n"
        )
        log.write("" + "\n")
        log.write("" + "\n")

        # regional sums
        log.write("GLOBAL TOTALS (Tg Species)" + "\n")
        log.write("CO, " + str(sum(CO) / 1.0e9) + "\n")
        log.write("NOX, " + str(sum(NOX) / 1.0e9) + "\n")
        log.write("NO, " + str(sum(NO) / 1.0e9) + "\n")
        log.write("NO2, " + str(sum(NO2) / 1.0e9) + "\n")
        log.write("NH3, " + str(sum(NH3) / 1.0e9) + "\n")
        log.write("SO2, " + str(sum(SO2) / 1.0e9) + "\n")
        log.write("VOC, " + str(sum(VOC) / 1.0e9) + "\n")
        log.write("OC, " + str(sum(OC) / 1.0e9) + "\n")
        log.write("BC, " + str(sum(BC) / 1.0e9) + "\n")
        log.write("PM2.5, " + str(sum(PM25) / 1.0e9) + "\n")
        log.write("PM20, " + str(sum(PM10) / 1.0e9) + "\n")

        # WESTERN U.S.
        westUS = (lati.between(24, 49) & longi.between(-125, -100)).values
        log.write("Western US (Gg Species)" + "\n")
        log.write("CO, " + str(sum(CO[westUS]) / 1.0e6) + "\n")
        log.write("NOX, " + str(sum(NOX[westUS]) / 1.0e6) + "\n")
        log.write("NO, " + str(sum(NO[westUS]) / 1.0e6) + "\n")
        log.write("NO2, " + str(sum(NO2[westUS]) / 1.0e6) + "\n")
        log.write("NH3, " + str(sum(NH3[westUS]) / 1.0e6) + "\n")
        log.write("SO2, " + str(sum(SO2[westUS]) / 1.0e6) + "\n")
        log.write("VOC, " + str(sum(VOC[westUS]) / 1.0e6) + "\n")
        log.write("OC, " + str(sum(OC[westUS]) / 1.0e6) + "\n")
        log.write("BC, " + str(sum(BC[westUS]) / 1.0e6) + "\n")
        log.write("PM2.5, " + str(sum(PM25[westUS]) / 1.0e6) + "\n")
        log.write("PM10, " + str(sum(PM10[westUS]) / 1.0e6) + "\n")

        # EASTERN U.S.
        eastUS = (lati.between(24, 49) & longi.between(-100, -60)).values
        log.write("Eastern US (Gg Species)" + "\n")
        log.write("CO, " + str(sum(CO[eastUS]) / 1.0e6) + "\n")
        log.write("NOX, " + str(sum(NOX[eastUS]) / 1.0e6) + "\n")
        log.write("NO, " + str(sum(NO[eastUS]) / 1.0e6) + "\n")
        log.write("NO2, " + str(sum(NO2[eastUS]) / 1.0e6) + "\n")
        log.write("NH3, " + str(sum(NH3[eastUS]) / 1.0e6) + "\n")
        log.write("SO2, " + str(sum(SO2[eastUS]) / 1.0e6) + "\n")
        log.write("VOC, " + str(sum(VOC[eastUS]) / 1.0e6) + "\n")
        log.write("OC, " + str(sum(OC[eastUS]) / 1.0e6) + "\n")
        log.write("BC, " + str(sum(BC[eastUS]) / 1.0e6) + "\n")
        log.write("PM2.5, " + str(sum(PM25[eastUS]) / 1.0e6) + "\n")
        log.write("PM10, " + str(sum(PM10[eastUS]) / 1.0e6) + "\n")

        # CANADA/AK
        CANAK = (lati.between(49, 70) & longi.between(-170, -55)).values
        log.write("Canada/Alaska (Gg Species)" + "\n")
        log.write("CO, " + str(sum(CO[CANAK]) / 1.0e6) + "\n")
        log.write("NOX, " + str(sum(NOX[CANAK]) / 1.0e6) + "\n")
        log.write("NO, " + str(sum(NO[CANAK]) / 1.0e6) + "\n")
        log.write("NO2, " + str(sum(NO2[CANAK]) / 1.0e6) + "\n")
        log.write("NH3, " + str(sum(NH3[CANAK]) / 1.0e6) + "\n")
        log.write("SO2, " + str(sum(SO2[CANAK]) / 1.0e6) + "\n")
        log.write("VOC, " + str(sum(VOC[CANAK]) / 1.0e6) + "\n")
        log.write("OC, " + str(sum(OC[CANAK]) / 1.0e6) + "\n")
        log.write("BC, " + str(sum(BC[CANAK]) / 1.0e6) + "\n")
        log.write("PM2.5, " + str(sum(PM25[CANAK]) / 1.0e6) + "\n")
        log.write("PM10, " + str(sum(PM10[CANAK]) / 1.0e6) + "\n")

        # Mexico and Central America
        MXCA = (lati.between(10, 28) & longi.between(-120, -65)).values
        log.write("Mexico/Central America (Gg Species)" + "\n")
        log.write("CO, " + str(sum(CO[MXCA]) / 1.0e6) + "\n")
        log.write("NOX, " + str(sum(NOX[MXCA]) / 1.0e6) + "\n")
        log.write("NO, " + str(sum(NO[MXCA]) / 1.0e6) + "\n")
        log.write("NO2, " + str(sum(NO2[MXCA]) / 1.0e6) + "\n")
        log.write("NH3, " + str(sum(NH3[MXCA]) / 1.0e6) + "\n")
        log.write("SO2, " + str(sum(SO2[MXCA]) / 1.0e6) + "\n")
        log.write("VOC, " + str(sum(VOC[MXCA]) / 1.0e6) + "\n")
        log.write("OC, " + str(sum(OC[MXCA]) / 1.0e6) + "\n")
        log.write("BC, " + str(sum(BC[MXCA]) / 1.0e6) + "\n")
        log.write("PM2.5, " + str(sum(PM25[MXCA]) / 1.0e6) + "\n")
        log.write("PM10, " + str(sum(PM10[MXCA]) / 1.0e6) + "\n")
