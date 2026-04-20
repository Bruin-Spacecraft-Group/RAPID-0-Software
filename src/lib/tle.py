"""
Functions and Variables used by ADCS to update and use TLE (two-line element data)

Adapted from the TLE-tools library by @FedericoStra on GitHub for ulab, 
"""

from datastores.adcs import Satrec

def _conv_year(s):
    """Interpret a two-digit year string."""
    if isinstance(s, int):
        return s
    y = int(s)
    return y + (1900 if y >= 57 else 2000)

def _parse_decimal(s):
    """Parse a floating point with implicit leading dot.

    >>> _parse_decimal('378')
    0.378
    """
    return float('.' + s)

def _parse_float(s):
    """Parse a floating point with implicit dot and exponential notation.

    >>> _parse_float(' 12345-3')
    0.00012345
    >>> _parse_float('+12345-3')
    0.00012345
    >>> _parse_float('-12345-3')
    -0.00012345
    """
    return float(s[0] + '.' + s[1:6] + 'e' + s[6:8])

class TLE:
    """
    Two line-elements (TLEs) are unpacked from both given and propagated data.
    This implementation uses Keplerian orbital parameters

    A two-line element set (TLE) is a data format encoding a list of orbital
    elements of an Earth-orbiting object for a given point in time, the epoch.

    All the attributes parsed from the TLE are expressed in the same units that
    are used in the TLE format.

    :str name:
        Name of the satellite.
    :str norad:
        NORAD catalog number (https://en.wikipedia.org/wiki/Satellite_Catalog_Number).
    :str classification:
        'U', 'C', 'S' for unclassified, classified, secret.
    :str int_desig:
        International designator (https://en.wikipedia.org/wiki/International_Designator),
    :int epoch_year:
        Year of the epoch.
    :float epoch_day:
        Day of the year plus fraction of the day.
    :float dn_o2:
        First time derivative of the mean motion divided by 2.
    :float ddn_o6:
        Second time derivative of the mean motion divided by 6.
    :float bstar:
        BSTAR coefficient (https://en.wikipedia.org/wiki/BSTAR).
    :int set_num:
        Element set number.
    :float inc:
        Inclination.
    :float raan:
        Right ascension of the ascending node.
    :float ecc:
        Eccentricity.
    :float argp:
        Argument of perigee.
    :float M:
        Mean anomaly.
    :float n:
        Mean motion.
    :int rev_num:
        Revolution number.
    """

    def __init__(self, name:str,
                 # ID parameters, Line 1
                 norad:str, classification:str, int_desig:str, 
                 # time (derivative) parameters, line 1
                 epoch_year:int, epoch_day:float, dn_o2:float, ddn_o6:float, bstar:float, set_num:int, 
                 # keplerian parameters, line 2
                 inc:float, raan:float, ecc:float, argp:float, M:float, n:float, rev_num:int):
        # Oh my lord prepare for absolute misery on earth
        
        self.name = str.strip(name)

        self.norad = str.strip(norad)
        self.classification = classification
        self.int_desig = str.strip(int_desig)

        self.epoch_year = _conv_year(epoch_year)
        self.epoch_day = epoch_day
        self.dn_o2 = dn_o2
        self.ddn_o6 = ddn_o6
        self.bstar = bstar
        self.set_num = int(set_num)

        self.inc = inc
        self.raan = raan
        self.ecc = ecc
        self.argp = argp
        self.M = M
        self.n = n
        self.rev_num = int(rev_num)
    
    @classmethod
    def from_lines(cls, name, line1, line2):
        """Parse a TLE from its constituent lines.

        All the attributes parsed from the TLE are expressed in the same units that
        are used in the TLE format.
        """
        return cls(
            name=name,
            norad=line1[2:7],
            classification=line1[7],
            int_desig=line1[9:17],
            epoch_year=line1[18:20],
            epoch_day=float(line1[20:32]),
            dn_o2=float(line1[33:43]),
            ddn_o6=_parse_float(line1[44:52]),
            bstar=_parse_float(line1[53:61]),
            set_num=line1[64:68],
            inc=float(line2[8:16]),
            raan=float(line2[17:25]),
            ecc=_parse_decimal(line2[26:33]),
            argp=float(line2[34:42]),
            M=float(line2[43:51]),
            n=float(line2[52:63]),
            rev_num=line2[63:68])

    @classmethod
    def from_file(cls, filename):
        """Load TLE from a file."""
        if isinstance(filename, str):
            with open(filename) as fp:
                return [cls.from_lines(*fp.readlines[:2])]

    @classmethod
    def from_str(cls, string):
        """Load TLE from a string."""
        return [cls.from_lines(*string.split('\n')[:2])]

    def to_array(self):
        """
        Return 2D array of TLE values
        
        Indexed as 
        [line, col]

        n is mean motion, d suggests time derivative

        name: [0,0] 

        norad: [1,0] classification: [1,1] int_desig: [1,2] epoch_year: [1,3] day: [1,4] 
        dn/2: [1,5] ddn/6: [1,6] bstar: [1,7] set_num: [1,8]

        inclination: [2,0] RAAN: [2,1] eccentricity: [2,2] arg_perigee: [2,3] Mean Anomaly: [2,4] n: [2,5] rev_num: [2,6]
        """
        TLE()
        return [
            [self.name], # Line 0
            [self.norad, self.classification, self.int_desig, # line 1 ID
             self.epoch_year, self.epoch_day, self.dn_o2, self.ddn_o6, self.bstar, self.set_num], # line 1 time-derivative
            [self.inc, self.raan, self.ecc, self.argp, self.M, self.n, self.rev_num] # line 2 orbital params
        ]
    
    def to_sgp4_params(self):
        """Return a formatted Satrec object that can immediately used in SGP4"""

        return Satrec.from_tle_array(self.to_array())
    