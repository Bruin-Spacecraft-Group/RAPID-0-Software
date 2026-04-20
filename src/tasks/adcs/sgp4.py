"""
Simplified General Perturbations Model 4 Implementation for Orbit Propagation

As outlined in https://celestrak.org/publications/AIAA/2008-6770/AIAA-2008-6770.pdf
"""

from tle import Satrec

# Error codes
ECCENTRICITY = 1 # eccentricity is not within 0-1
MOTION = 2 # error in propagating mean motion
SEMIRECT = 4 # apoapsis, periapsis characteristics error
DECAY = 6 # orbit has decayed

try:
    import ulab.numpy as np  # For CircuitPython
except ImportError:
    import numpy as np  # For GitHub Actions / PC testing

def sgp4_update(satrec: Satrec, tsince):
    """
    Transforms to cartesian (r, v) from a Satrec (TLE 7+) input, then performs matrix operations
    to propagate the system 

    Current implementation uses an analytical approach to compute the Jacobian A matrix
    Possible alternative is numerical stepping (for lower accuracy) of associated partials
    """
    # -- Set mathematical constants
    x2o3  = 2.0 / 3.0;
    tau = 2.0 * np.pi
    vkmpersec = satrec.radiusearthkm * satrec.xke/60.0;

    satrec.t = tsince

    # -- Update for secular gravity and atmospheric drag
    xmdf    = satrec.mo + satrec.mdot * satrec.t;
    argpdf  = satrec.argpo + satrec.argpdot * satrec.t;
    nodedf  = satrec.nodeo + satrec.nodedot * satrec.t;
    argpm   = argpdf
    mm      = xmdf
    t2      = satrec.t * satrec.t;
    nodem   = nodedf + satrec.nodecf * t2;
    tempa   = 1.0 - satrec.cc1 * satrec.t;
    tempe   = satrec.bstar * satrec.cc4 * satrec.t;
    templ   = satrec.t2cof * t2;

    # -- Extra mean quantities

    # -- Add lunar-solar periodics

    # -- Long period periodics

    # -- Solve Kepler's

    #  -- Short period
    # Preliminary quantities

        # - Update for short period periodics

        # - Orientation vectors

        # - Compute r and v
    if satrec.isimp != 1:

        delomg = satrec.omgcof * satrec.t;
        #  sgp4fix use mutliply for speed instead of pow
        delmtemp =  1.0 + satrec.eta * np.cos(xmdf);
        delm   = satrec.xmcof * \
                (delmtemp * delmtemp * delmtemp -
                satrec.delmo);
        temp   = delomg + delm;
        mm     = xmdf + temp;
        argpm  = argpdf - temp;
        t3     = t2 * satrec.t;
        t4     = t3 * satrec.t;
        tempa  = tempa - satrec.d2 * t2 - satrec.d3 * t3 - \
                        satrec.d4 * t4;
        tempe  = tempe + satrec.bstar * satrec.cc5 * (np.sin(mm) -
                        satrec.sinmao);
        templ  = templ + satrec.t3cof * t3 + t4 * (satrec.t4cof +
                        satrec.t * satrec.t5cof);

    nm    = satrec.no_unkozai;
    em    = satrec.ecco;
    inclm = satrec.inclo;

    if nm <= 0.0:

        satrec.error_message = ('mean motion {0:f} is less than zero'
                                .format(nm))
        satrec.error = MOTION
        #  sgp4fix add return
        return False, False;

    am = pow((satrec.xke / nm),x2o3) * tempa * tempa;
    nm = satrec.xke / pow(am, 1.5);
    em = em - tempe;

    #  fix tolerance for error recognition
    #  sgp4fix am is fixed from the previous nm check
    if em >= 1.0 or em < -0.001:  # || (am < 0.95)

        satrec.error_message = ('mean eccentricity {0:f} not within'
                                ' range 0.0 <= e < 1.0'.format(em))
        satrec.error = ECCENTRICITY
        #  sgp4fix to return if there is an error in eccentricity
        return False, False;

    #  sgp4fix fix tolerance to avoid a divide by zero
    if em < 1.0e-6:
        em  = 1.0e-6;
    mm     = mm + satrec.no_unkozai * templ;
    xlm    = mm + argpm + nodem;
    emsq   = em * em;
    temp   = 1.0 - emsq;

    nodem  = nodem % tau if nodem >= 0.0 else -(-nodem % tau)
    argpm  = argpm % tau
    xlm    = xlm % tau
    mm     = (xlm - argpm - nodem) % tau

    # sgp4fix recover singly averaged mean elements
    satrec.am = am;
    satrec.em = em;
    satrec.im = inclm;
    satrec.Om = nodem;
    satrec.om = argpm;
    satrec.mm = mm;
    satrec.nm = nm;

    #  ----------------- compute extra mean quantities -------------
    sinim = np.sin(inclm);
    cosim = np.cos(inclm);

    #  -------------------- add lunar-solar periodics --------------
    ep     = em;
    xincp  = inclm;
    argpp  = argpm;
    nodep  = nodem;
    mp     = mm;
    sinip  = sinim;
    cosip  = cosim;

    #  -------------------- long period periodics ------------------
    axnl = ep * np.cos(argpp);
    temp = 1.0 / (am * (1.0 - ep * ep));
    aynl = ep* np.sin(argpp) + temp * satrec.aycof;
    xl   = mp + argpp + nodep + temp * satrec.xlcof * axnl;

    #  --------------------- solve kepler's equation ---------------
    u    = (xl - nodep) % tau
    eo1  = u;
    tem5 = 9999.9;
    ktr = 1;
    #    sgp4fix for kepler iteration
    #    the following iteration needs better limits on corrections
    while np.fabs(tem5) >= 1.0e-12 and ktr <= 10:

        sineo1 = np.sin(eo1);
        coseo1 = np.cos(eo1);
        tem5   = 1.0 - coseo1 * axnl - sineo1 * aynl;
        tem5   = (u - aynl * coseo1 + axnl * sineo1 - eo1) / tem5;
        if np.fabs(tem5) >= 0.95:
            tem5 = 0.95 if tem5 > 0.0 else -0.95;
        eo1    = eo1 + tem5;
        ktr = ktr + 1;

    #  ------------- short period preliminary quantities -----------
    ecose = axnl*coseo1 + aynl*sineo1;
    esine = axnl*sineo1 - aynl*coseo1;
    el2   = axnl*axnl + aynl*aynl;
    pl    = am*(1.0-el2);
    if pl < 0.0:

        satrec.error_message = ('semilatus rectum {0:f} is less than zero'
                                .format(pl))
        satrec.error = SEMIRECT
        #  sgp4fix add return
        return False, False;

    else:

        rl     = am * (1.0 - ecose);
        rdotl  = np.sqrt(am) * esine/rl;
        rvdotl = np.sqrt(pl) / rl;
        betal  = np.sqrt(1.0 - el2);
        temp   = esine / (1.0 + betal);
        sinu   = am / rl * (sineo1 - aynl - axnl * temp);
        cosu   = am / rl * (coseo1 - axnl + aynl * temp);
        su     = np.atan2(sinu, cosu);
        sin2u  = (cosu + cosu) * sinu;
        cos2u  = 1.0 - 2.0 * sinu * sinu;
        temp   = 1.0 / pl;
        temp1  = 0.5 * satrec.j2 * temp;
        temp2  = temp1 * temp;

        #  -------------- update for short period periodics ------------
        mrt   = rl * (1.0 - 1.5 * temp2 * betal * satrec.con41) + \
                0.5 * temp1 * satrec.x1mth2 * cos2u;
        su    = su - 0.25 * temp2 * satrec.x7thm1 * sin2u;
        xnode = nodep + 1.5 * temp2 * cosip * sin2u;
        xinc  = xincp + 1.5 * temp2 * cosip * sinip * cos2u;
        mvt   = rdotl - nm * temp1 * satrec.x1mth2 * sin2u / satrec.xke;
        rvdot = rvdotl + nm * temp1 * (satrec.x1mth2 * cos2u +
                1.5 * satrec.con41) / satrec.xke;

        #  --------------------- orientation vectors -------------------
        sinsu =  np.sin(su);
        cossu =  np.cos(su);
        snod  =  np.sin(xnode);
        cnod  =  np.cos(xnode);
        sini  =  np.sin(xinc);
        cosi  =  np.cos(xinc);
        xmx   = -snod * cosi;
        xmy   =  cnod * cosi;
        ux    =  xmx * sinsu + cnod * cossu;
        uy    =  xmy * sinsu + snod * cossu;
        uz    =  sini * sinsu;
        vx    =  xmx * cossu - cnod * sinsu;
        vy    =  xmy * cossu - snod * sinsu;
        vz    =  sini * cossu;

        #  --------- position and velocity (in km and km/sec) ----------
        _mr = mrt * satrec.radiusearthkm
        r = (_mr * ux, _mr * uy, _mr * uz)
        v = ((mvt * ux + rvdot * vx) * vkmpersec,
            (mvt * uy + rvdot * vy) * vkmpersec,
            (mvt * uz + rvdot * vz) * vkmpersec)

    #  sgp4fix for decaying satellites
    if mrt < 1.0:

        satrec.error_message = ('mrt {0:f} is less than 1.0 indicating'
                                ' the satellite has decayed'.format(mrt))
        satrec.error = DECAY

    return r, v
    

