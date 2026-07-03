"""
Sun position algorithm adapted from https://aa.usno.navy.mil/faq/sun_approx
"""

import numpy as np

J2000 = 2451545.0 #For Julian Date January 1st 2000 12:00 UTC 

def dist_sun_from_earth(jd, fr):
    """
    Calculating Earth to Sun vector from Julian Date NOTE: Is it sun to earth or earth to sun...
    """
    
    #Days Since Epoch J2000: D = JD - 2451545.0
    d = (jd + fr) - J2000
    print("days since j2000: ", d) 

    #Mean Anomaly of Sun Equation in degrees: g = 357.529 + 0.98560028D 
    #In radians: g = 6.24004 + 0.017201970D
    g_deg = 357.529 + 0.98560028 * d 
    g = 6.24004 + 0.017201970 * d 
    g_rad = np.deg2rad(g_deg)
    print("g new: ", g)               #using converted equations
    print("g deg to rad: ", g_rad)    #og equations

    #Mean Longitude of Sun in degrees: q = 280.459 + 0.98564736D
    #In radians: q = 4.89493 + 0.017202792D
    q_deg = 280.459 + 0.98564736 * d
    q = 4.89493 + 0.017203 * d
    q_rad = np.deg2rad(q_deg)
    print("q new: ", q)
    print("q deg to rad: ", q_rad)
    
    #Mean Eliptical Longitude of Sun in degrees: L = q + 1.915 + sin(g) + 0.020 * sin(2g)
    #In radians: L = q + 0.03342sin(g) + 0.00035sin(2g)
    #NOTE: Add correction for angles not in between 0 to 360 / 0 to 2pi 
    L_deg = q_deg + 1.915 * np.rad2deg(np.sin(g_rad)) + 0.020 * np.rad2deg(np.sin(2 * g_rad))
    L = q + 0.03342 * np.sin(g) + 0.00035 * np.sin(2 * g) 
    L_rad = np.deg2rad(L_deg)
    print("L new: ", L) 
    print("L deg to rad: ", L_rad)

    #Approx Eliptical Latitude 
    b = 0

    #Distance of Sun from Earth using degrees (in AU): r_sun = 1.0014 - 0.01671cos(g) - 0.00014cos(2g)
    #Using radians: r_sun = 0.017478 - 0.0002916cos(g) - 0.0000024cos(2g) 
    r_sun_deg = 1.0014 - 0.01671 * np.rad2deg(np.cos(g_rad)) - 0.00014 * np.rad2deg(np.cos(2 * g_rad))
    r_sun = 0.017478 - 0.0002916 * np.cos(g) - 0.0000024 * np.cos(2 * g) 
    r_sun_rad = np.deg2rad(r_sun_deg)
    print("r sun new: ", r_sun) 
    print("r sun deg to rad: ", r_sun_rad)
    
    #Mean obliquity of ecliptic in degrees: epsilon = 23.439 - 0.00000036D
    epsilon_deg = 23.439 - 0.00000036 * d
    epsilon = 0.40909 - 0.0000000063 * d
    epsilon_rad = np.deg2rad(epsilon_deg) 
    print("ep new: ", epsilon) 
    print("ep deg to rad: ", epsilon_rad)

    
    #Right ascension of Sun: tan(alpha) = cos(epsilon) * sin(L) / cos(L) 
    alpha_rad = np.arctan(np.cos(epsilon_rad) * np.sin(L_rad) / np.cos(L_rad))
    alpha = np.arctan(np.cos(epsilon) * np.sin(L) / np.cos(L))
    print("alpha new: ", alpha) 
    print("alpha rad: ", alpha_rad)
          
    #Declination of sun: sin(delta) = sin(epsilon) * sin(L) 
    delta_rad = np.arcsin(np.sin(epsilon_rad) * np.sin(L_rad))
    delta = np.arcsin(np.sin(epsilon) * np.sin(L))
    print("delta new: ", delta)
    print("delta rad: ", delta_rad)
                
    return r_sun

if __name__ == '__main__':
        jd = 2461221
        fr = 10446
        print("Returned: " + str(dist_sun_from_earth(jd, fr)))
    

