"""
Functions and Variables used by ADCS to update and use TLE (two-line element data)

Adapted from the TLE-tools library by @FedericoStra on GitHub for ulab, 
"""

try:
    import ulab.numpy as np  # For CircuitPython
except ImportError:
    import numpy as np  # For GitHub Actions / PC testing

def _gstime(jdut1):
    deg2rad = np.pi / 180.0
    tau = np.pi*2
    tut1 = (jdut1 - 2451545.0) / 36525.0
    temp = -6.2e-6* tut1 * tut1 * tut1 + 0.093104 * tut1 * tut1 + \
            (876600.0*3600 + 8640184.812866) * tut1 + 67310.54841  #  sec
    temp = (temp * deg2rad / 240.0) % tau # 360/86400 = 1/240, to deg, to rad

    #  ------------------------ check quadrants ---------------------
    if temp < 0.0:
        temp += tau

    return temp

def _initl(xke, j2,
            ecco, epoch, inclo, no):
    #  ----------------------- earth constants ----------------------
    #  sgp4fix identify constants and allow alternate values
    #  only xke and j2 are used here so pass them in directly
    #  tumin, mu, radiusearthkm, xke, j2, j3, j4, j3oj2 = whichconst
    x2o3   = 2.0 / 3.0;

    #  ------------- calculate auxillary epoch quantities ----------
    eccsq  = ecco * ecco;
    omeosq = 1.0 - eccsq;
    rteosq = np.sqrt(omeosq);
    cosio  = np.cos(inclo);
    cosio2 = cosio * cosio;

    #  ------------------ un-kozai the mean motion -----------------
    ak    = pow(xke / no, x2o3);
    d1    = 0.75 * j2 * (3.0 * cosio2 - 1.0) / (rteosq * omeosq);
    del_  = d1 / (ak * ak);
    adel  = ak * (1.0 - del_ * del_ - del_ *
            (1.0 / 3.0 + 134.0 * del_ * del_ / 81.0));
    del_  = d1/(adel * adel)
    no    = no / (1.0 + del_)

    ao    = pow(xke / no, x2o3)
    sinio = np.sin(inclo)
    po    = ao * omeosq
    con42 = 1.0 - 5.0 * cosio2
    con41 = -con42-cosio2-cosio2
    posq  = po * po
    rp    = ao * (1.0 - ecco)

    gsto = _gstime(epoch + 2433281.5)

    return (
       no,
       ao,    con41,  con42, cosio,
       cosio2, omeosq, posq,
       rp,    rteosq,sinio , gsto
    )

class Satrec:
    """
    Parameters, constants that are commonly used across the sgp4 logical flow

    Usually built from TLE
    """

    # Error codes
    ECCENTRICITY = 1 # eccentricity is not within 0-1
    MOTION = 2 # error in propagating mean motion
    SEMIRECT = 4 # apoapsis, periapsis characteristics error
    DECAY = 6 # orbit has decayed

    """
    t - time since
    mo, mdot - mean anomaly
    argpo, argpdot - argument of perigee
    nodeo, nodedot, nodecf - RAAN value, drift, and correction respectively
    bstar - atmospheric drag
    cc1, cc4, cc5 - drag coefficient terms
    ecco, inclo - eccentricity, inclination (no derivatives)
    mm, nm - mean motion before and after corrections
    error, error_message - might want to leave this up to cdh but implement
    this here?
    isimp - using simplified model?

    """

    """ Error Messages
    MOTION 
    satrec.error_message = ('mean motion {0:f} is less than zero'
                                .format(nm))
    
    ECCENTRICITY
    satrec.error_message = ('mean eccentricity {0:f} not within'
                                ' range 0.0 <= e < 1.0'.format(em))

    SEMIRECT
    satrec.error_message = ('semilatus rectum {0:f} is less than zero'
                                .format(pl))
    
    DECAY
    satrec.error_message = ('mrt {0:f} is less than 1.0 indicating'
                                ' the satellite has decayed'.format(mrt))
    """

    def __init__(self, satn,   epoch,
                 bstar, ndot, nddot, ecco, argpo,
                 inclo, mo, no_kozai,
                 nodeo
                 ):
        
        temp4    =   1.5e-12

        # Near Earth Variables
        self.isimp   = 0;   self.aycof  = 0.0
        self.con41   = 0.0; self.cc1    = 0.0; self.cc4      = 0.0
        self.cc5     = 0.0; self.d2     = 0.0; self.d3       = 0.0
        self.d4      = 0.0; self.delmo  = 0.0; self.eta      = 0.0
        self.argpdot = 0.0; self.omgcof = 0.0; self.sinmao   = 0.0
        self.t       = 0.0; self.t2cof  = 0.0; self.t3cof    = 0.0
        self.t4cof   = 0.0; self.t5cof  = 0.0; self.x1mth2   = 0.0
        self.x7thm1  = 0.0; self.mdot   = 0.0; self.nodedot  = 0.0
        self.xlcof   = 0.0; self.xmcof  = 0.0; self.nodecf   = 0.0
        
        # Earth Constants
        self.mu     = 398600.5;            #  in km3 / s2
        self.radiusearthkm = 6378.137      #  km
        self.xke    = 0.07436685317
        self.tumin  = 13.44685108
        self.j2     =  0.00108262998905
        self.j3     = -0.00000253215306
        self.j4     = -0.00000161098761
        self.j3oj2  = -0.002338890559

        ss = 1.012229276
        qzms2ttemp = 0.00658499496
        qzms2t = qzms2ttemp * qzms2ttemp * qzms2ttemp * qzms2ttemp;
        x2o3   =  2.0 / 3.0

        # -- initialisation markers
        self.init = 'y'
        self.t	 = 0.0

        # -- 
        self.satnum_str = satn
        self.classification = 'U'

        # --
        self.bstar   = bstar
        self.ndot    = ndot
        self.nddot   = nddot
        self.ecco    = ecco
        self.argpo   = argpo
        self.inclo   = inclo
        self.mo	     = mo
        self.nodeo   = nodeo
        self.no_kozai = no_kozai

        # single averaged mean elements
        self.am = 0.0
        self.em = 0.0
        self.im = 0.0
        self.Om = 0.0
        self.mm = 0.0
        self.nm = 0.0

        self.error = 0

        # -- 
        (
        self.no_unkozai,
        ao,    self.con41,  con42, cosio,
        cosio2, omeosq, posq,
        rp,    rteosq,sinio , self.gsto,
        ) = _initl(
            self.xke, self.j2, self.ecco, epoch, self.inclo, self.no_kozai
            )
        self.a    = pow( self.no_unkozai*self.tumin , (-2.0/3.0) );
        self.alta = self.a*(1.0 + self.ecco) - 1.0;
        self.altp = self.a*(1.0 - self.ecco) - 1.0;
    
        if omeosq >= 0.0 or self.no_unkozai >= 0.0:
            self.isimp = 0
            if rp < 220.0 / self.radiusearthkm + 1.0:
                self.isimp = 1
            sfour  = ss
            qzms24 = qzms2t
        pinvsq = 1.0 / posq;

        tsi  = 1.0 / (ao - sfour);
        self.eta  = ao * self.ecco * tsi;
        etasq = self.eta * self.eta;
        eeta  = self.ecco * self.eta;
        psisq = np.fabs(1.0 - etasq);
        coef  = qzms24 * pow(tsi, 4.0);
        coef1 = coef / pow(psisq, 3.5);
        cc2   = coef1 * self.no_unkozai * (ao * (1.0 + 1.5 * etasq + eeta *
                    (4.0 + etasq)) + 0.375 * self.j2 * tsi / psisq * self.con41 *
                    (8.0 + 3.0 * etasq * (8.0 + etasq)));
        self.cc1   = self.bstar * cc2;
        cc3   = 0.0;
        if self.ecco > 1.0e-4:
            cc3 = -2.0 * coef * tsi * self.j3oj2 * self.no_unkozai * sinio / self.ecco;
        self.x1mth2 = 1.0 - cosio2;
        self.cc4    = 2.0* self.no_unkozai * coef1 * ao * omeosq * \
                        (self.eta * (2.0 + 0.5 * etasq) + self.ecco *
                        (0.5 + 2.0 * etasq) - self.j2 * tsi / (ao * psisq) *
                        (-3.0 * self.con41 * (1.0 - 2.0 * eeta + etasq *
                        (1.5 - 0.5 * eeta)) + 0.75 * self.x1mth2 *
                        (2.0 * etasq - eeta * (1.0 + etasq)) * np.cos(2.0 * self.argpo)));
        self.cc5 = 2.0 * coef1 * ao * omeosq * (1.0 + 2.75 *
                    (etasq + eeta) + eeta * etasq);
        cosio4 = cosio2 * cosio2;
        temp1  = 1.5 * self.j2 * pinvsq * self.no_unkozai;
        temp2  = 0.5 * temp1 * self.j2 * pinvsq;
        temp3  = -0.46875 * self.j4 * pinvsq * pinvsq * self.no_unkozai;
        self.mdot     = self.no_unkozai + 0.5 * temp1 * rteosq * self.con41 + 0.0625 * \
                        temp2 * rteosq * (13.0 - 78.0 * cosio2 + 137.0 * cosio4);
        self.argpdot  = (-0.5 * temp1 * con42 + 0.0625 * temp2 *
                            (7.0 - 114.0 * cosio2 + 395.0 * cosio4) +
                            temp3 * (3.0 - 36.0 * cosio2 + 49.0 * cosio4));
        xhdot1            = -temp1 * cosio;
        self.nodedot = xhdot1 + (0.5 * temp2 * (4.0 - 19.0 * cosio2) +
                            2.0 * temp3 * (3.0 - 7.0 * cosio2)) * cosio;
        self.omgcof   = self.bstar * cc3 * np.cos(self.argpo);
        self.xmcof    = 0.0;
        if self.ecco > 1.0e-4:
            self.xmcof = -x2o3 * coef * self.bstar / eeta;
        self.nodecf = 3.5 * omeosq * xhdot1 * self.cc1;
        self.t2cof   = 1.5 * self.cc1;
        
        if np.fabs(cosio+1.0) > 1.5e-12:
            self.xlcof = -0.25 * self.j3oj2 * sinio * (3.0 + 5.0 * cosio) / (1.0 + cosio);
        else:
            self.xlcof = -0.25 * self.j3oj2 * sinio * (3.0 + 5.0 * cosio) / temp4;
        self.aycof   = -0.5 * self.j3oj2 * sinio;
        
        delmotemp = 1.0 + self.eta * np.cos(self.mo);
        self.delmo   = delmotemp * delmotemp * delmotemp;
        self.sinmao  = np.sin(self.mo);
        self.x7thm1  = 7.0 * cosio2 - 1.0;

        if self.isimp != 1:
           cc1sq          = self.cc1 * self.cc1;
           self.d2    = 4.0 * ao * tsi * cc1sq;
           temp           = self.d2 * tsi * self.cc1 / 3.0;
           self.d3    = (17.0 * ao + sfour) * temp;
           self.d4    = 0.5 * temp * ao * tsi * (221.0 * ao + 31.0 * sfour) * \
                            self.cc1;
           self.t3cof = self.d2 + 2.0 * cc1sq;
           self.t4cof = 0.25 * (3.0 * self.d3 + self.cc1 *
                            (12.0 * self.d2 + 10.0 * cc1sq));
           self.t5cof = 0.2 * (3.0 * self.d4 +
                            12.0 * self.cc1 * self.d3 +
                            6.0 * self.d2 * self.d2 +
                            15.0 * cc1sq * (2.0 * self.d2 + cc1sq));

        # need to propagate to epoch 0.0 to really instantiate everything else before
        # init flag is set to 'n'

        return True

    @classmethod
    def from_tle_array(cls):

        obj = cls()

        return obj

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
    