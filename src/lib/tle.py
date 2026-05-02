"""
Functions and Variables used by ADCS to update and use TLE (two-line element data)

Adapted from the TLE-tools library by @FedericoStra on GitHub for ulab, 
"""

from sgp4 import sgp4_init, sgp4_update

try:
    import ulab.numpy as np  # For CircuitPython
except ImportError:
    import numpy as np  # For GitHub Actions / PC testing

minutes_per_day = 1440
epoch0 = 2433281.5 # jan 0 1950

def _day_of_year_to_month_day(day_of_year, is_leap):
    """Core logic for turning days into months, for easy testing."""
    february_bump = (2 - is_leap) * (day_of_year >= 60 + is_leap)
    august = day_of_year >= 215
    month, day = divmod(2 * (day_of_year - 1 + 30 * august + february_bump), 61)
    month += 1 - august
    day //= 2
    day += 1
    return month, day

def _jday(year, mon, day, hr, minute, sec):
    """Return two floats (jd, fr) that, when added, produce the specified Julian date
    jd (Julian Date) and fr (Fractional) components

    >>> jd, fr = jday(2020, 2, 11, 13, 57, 0)
    >>> jd
    2458890.5
    >>> fr
    0.58125

    Note the first float, which gives the moment of midnight that
    commences the given calendar date, always ends in
    ``.5`` because Julian dates begin and end at noon.  This made
    Julian dates more convenient for astronomers in Europe, by making
    the whole night belong to a single Julian date.
    """
    jd = (367.0 * year
         - 7 * (year + ((mon + 9) // 12.0)) * 0.25 // 1.0
	   + 275 * mon / 9.0 // 1.0
	   + day
         + 1721013.5)
    fr = (sec + minute * 60.0 + hr * 3600.0) / 86400.0;
    return jd, fr

def _days2mdhms(year, days, round_to_microsecond=6):
    """Convert a float point number of days into the year into date and time.

    >>> days2mdhms(2000, 32.0)  # February 1
    (2, 1, 0, 0, 0.0)
    >>> days2mdhms(2000, 366.0)  # December 31, since 2000 was a leap year
    (12, 31, 0, 0, 0.0)

    The floating point seconds are rounded to an even number of
    microseconds if ``round_to_microsecond`` is true.
    """
    second = days * 86400.0
    if round_to_microsecond:
        second = round(second, round_to_microsecond)

    minute, second = divmod(second, 60.0)
    if round_to_microsecond:
        second = round(second, round_to_microsecond)

    minute = int(minute)
    hour, minute = divmod(minute, 60)
    day_of_year, hour = divmod(hour, 24)

    is_leap = year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)
    month, day = _day_of_year_to_month_day(day_of_year, is_leap)
    if month == 13:  # behave like the original in case of overflow
        month = 12
        day += 31

    return month, day, int(hour), int(minute), second

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

class Satrec:
    """
    Satellite record object
    Includes parameters, constants that are commonly used across the sgp4 logical flow

    In this implementation, built from TLE data

    Two line-elements (TLEs) are unpacked from both given and propagated data.
    This implementation uses Keplerian orbital parameters

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
    :float dn:
        First time derivative of the mean motion (divided by 2 in TLE)
    :float ddn:
        Second time derivative of the mean motion (divided by 6 in TLE).
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

    # Error codes
    ECCENTRICITY = 1 # eccentricity is not within 0-1
    MOTION = 2 # error in propagating mean motion
    SEMIRECT = 4 # apoapsis, periapsis characteristics error
    DECAY = 6 # orbit has decayed

    def __init__(self, name:str,
                 # ID parameters, Line 1
                 norad:str, classification:str, int_desig:str, 
                 # time (derivative) parameters, line 1
                 epoch_year:int, epoch_day:float, dn:float, ddn:float, bstar:float, ephtype: str, set_num:int, 
                 # keplerian parameters, line 2
                 inc:float, raan:float, ecc:float, argp:float, M:float, n:float, rev_num:int,
                 # for the purposes of keeping the tle around as future-proofing
                 tle_str:str ):
        
        self.name = str.strip(name) 

        self.norad = str.strip(norad)
        self.classification = classification
        self.int_desig = str.strip(int_desig)

        self.epoch_year = _conv_year(epoch_year)
        self.epoch_day = epoch_day
        self.dn = dn
        self.ddn = ddn
        self.bstar = bstar
        self.ephtype = ephtype
        self.set_num = int(set_num)

        self.inc = inc
        self.raan = raan
        self.ecc = ecc
        self.argp = argp
        self.M = M 
        self.n = n # mean motion
        self.rev_num = int(rev_num)

        self.tle_str = tle_str
    
    @classmethod
    def from_tle_lines(cls, name, line1, line2):
        """Parse a TLE from its constituent lines.

        All the attributes parsed from the TLE are expressed in the same units that
        are used in the TLE format.
        """
        return cls(
            name=name,
            norad=line1[2:7],
            classification=line1[7] or 'U',
            int_desig=line1[9:17],
            epoch_year=line1[18:20],
            epoch_day=float(line1[20:32]),
            dn=float(line1[33:43]),
            ddn=_parse_float(line1[44:52]),
            bstar=_parse_float(line1[53:61]),
            ephtype = line1[62],
            set_num=line1[64:68],
            inc=float(line2[8:16]),
            raan=float(line2[17:25]),
            ecc=_parse_decimal(line2[26:33]),
            argp=float(line2[34:42]),
            M=float(line2[43:51]),
            n=float(line2[52:63]),
            rev_num=line2[63:68])

    @classmethod
    def from_tle_file(cls, filename):
        """Load TLE from a file."""
        if isinstance(filename, str):
            with open(filename) as fp:
                return [cls.from_lines(*fp.readlines[:2])]

    @classmethod
    def from_tle_str(cls, string):
        """Load TLE from a string."""
        return [cls.from_lines(*string.split('\n')[:2])]

    @classmethod
    def sgp4_init(cls, tle: Satrec):
        """
        Creates a satrec object specifically modified to be used in sgp4.

        Changes units, activates certain new parameters, etc. 
        """

        self = tle

        # constants for unit change
        deg2rad  =  np.pi / 180.0;         #    0.0174532925199433
        xpdotp   =  1440.0 / (2.0 *np.pi);  #  229.1831180523293

        #  ---- convert to sgp4 units ----
        self.n = self.n / xpdotp
        self.dn = self.dn  / (xpdotp*1440.0)
        self.ddn= self.ddn / (xpdotp*1440.0*1440)

        #  ---- find standard orbital elements ----
        self.inc = self.inc  * deg2rad
        self.raan = self.raan  * deg2rad
        self.argp = self.argp  * deg2rad
        self.M    = self.M     * deg2rad

        yr = self.epoch_year

        # Build Julian Date
        if yr < 57:
            year = yr + 2000
        else:
            year = yr + 1900

        mon,day,hr,minute,sec = _days2mdhms(year, self.epoch_day)
        self.jdsatepoch = _jday(year,mon,day,hr,minute,sec);
        epoch0 = 2433281.5

        sgp4_init(self, self.set_num, self.jdsatepoch - epoch0, self.bstar,
                  self.dn, self.ddn, self.ecc, self.argp, self.inc, self.n, 
                  self.raan)
        
        return self

    def to_array(self):
        """
        Return 2D array of TLE values
        
        Indexed as 
        [line, col]

        n is mean motion, d suggests time derivative

        name: [0,0] 

        norad: [1,0] classification: [1,1] int_desig: [1,2] epoch_year: [1,3] day: [1,4] 
        dn: [1,5] ddn: [1,6] bstar: [1,7] set_num: [1,8]

        inclination: [2,0] RAAN: [2,1] eccentricity: [2,2] arg_perigee: [2,3] Mean Anomaly: [2,4] n: [2,5] rev_num: [2,6]
        """
    
        return [
            [self.name], # Line 0
            [self.norad, self.classification, self.int_desig, # line 1 ID
             self.epoch_year, self.epoch_day, self.dn, self.ddn, self.bstar, self.set_num], # line 1 time-derivative
            [self.inc, self.raan, self.ecc, self.argp, self.M, self.n, self.rev_num] # line 2 orbital params
        ]
    
    
    def sgp4_update(self, jd, fr):
        """
        For a julian date (jd) and its fractional representation (fr), 
        propagate Satrec using sgp4
        """

        tsince = ((jd - self.sat_epoch) * minutes_per_day +
                  (fr - self.sat_epochF) * minutes_per_day)
        r, v = sgp4_update(self, tsince)

        return self.error, r, v

    def error_message(self):
        if self.error == self.MOTION:
            return ('mean motion {0:f} is less than zero'
                                .format(self.n))
