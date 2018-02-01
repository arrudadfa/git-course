import math

G = 6.67408e-11
MASS_E = 5.972e24
RADIUS_E = 6371000.0
SAMPLE_TO_PRINT = 10000
ATMOSPHERE = 100000.00
GOLDEN_RATIO = (math.sqrt(5) + 1) / 2
MACH_RATIO_SEA_LEVEL = 0.00291545

# MK21 stats
MK21_MASS = 270
MK21_RADIUS = .28
MK21_BC = 150000
MK21_CD = 0.005739795918367346
# Warhead defaults
MASS = MK21_MASS
RADIUS = MK21_RADIUS
BC = MK21_BC
CD = MK21_CD


DENSITIES = {
    0: 12.25,
    1000: 11.12,
    2000: 10.07,
    3000: 9.093,
    4000: 8.194,
    5000: 7.364,
    6000: 6.601,
    7000: 5.9,
    8000: 5.258,
    9000: 4.671,
    10000: 4.135,
    15000: 1.948,
    20000: 0.8891,
    25000: 0.4008,
    30000: 0.1841,
    40000: 0.03996,
    50000: 0.01027,
    60000: 0.003097,
    70000: 0.0008283,
    80000: 0.0001846}


def get_cd(bc=MK21_BC, mass=MK21_MASS, radius=MK21_RADIUS):
    diameter = 2.0 * float(radius)
    return float(mass) / (float(diameter ** 2.0) * float(bc))


def get_drag(velocity, altitude):
    if altitude > ATMOSPHERE:
        return 0
    velocity, altitude = float(velocity), float(altitude)
    density = DENSITIES.get(
        altitude, DENSITIES[min(DENSITIES.keys(),
                                key=lambda k: abs(k - altitude))])
    cd = MK21_CD
    area = math.pi * float(RADIUS) ** 2
    force = 1.0 * .5 * density * cd * area * velocity**2
    a = float(force) / float(MASS)
    return a


def get_gravitational_acceleration(altitude):
    altitude = float(altitude)
    return -1.0 * float(G * MASS_E) / float(RADIUS_E + altitude)**2.0


def get_acceleration(altitude, velocity):
    return get_drag(velocity=velocity, altitude=altitude) + \
        get_gravitational_acceleration(altitude)


def calc_reenty(altitude, velocity=0.0, dt=.01, target_altitude=0.0):
    # cast everything to floats cause python sucks
    altitude, velocity, dt, target_altitude = float(
        altitude), float(velocity), float(dt), float(target_altitude)
    total_time = 0.0
    sample = 0

    # repeat until at target
    while(altitude >= target_altitude):

        a = get_acceleration(altitude, velocity)
        velocity = velocity + a * dt
        altitude = altitude + velocity * dt + 1.0 / 2.0 * a * dt**2.0
        total_time = total_time + dt
        sample += 1
        '''
        if sample % 50 == 0:
            print "Altitude:", altitude, "Accel:", a, "Velocity:", velocity
        '''
    return {"time": total_time, "velocity": velocity}


def gss(f, a, b, tol=1e-5):
    '''
    golden section search
    to find the minimum of f on [a,b]
    f: a strictly unimodal function on [a,b]
    example:
    >>> f = lambda x: (x-2)**2
    >>> x = gss(f, 1, 5)
    >>> x
    2.000009644875678
    '''
    c = b - (b - a) / GOLDEN_RATIO
    d = a + (b - a) / GOLDEN_RATIO
    while abs(c - d) > tol:
        if f(c) < f(d):
            b = d
        else:
            a = c

        # we recompute both c and d here to avoid loss of precision which may
        # lead to incorrect results or infinite loop
        c = b - (b - a) / GOLDEN_RATIO
        d = a + (b - a) / GOLDEN_RATIO

    return (b + a) / 2


def altitude_from_time(time_seconds):
    def f(altitude):
        time = calc_reenty(altitude)["time"]
        return abs(time - time_seconds)
    return gss(f, 0, 10000e3)


# Determine altitude for given reentry time

target_time = 30 / 2.0 * 60.0
altitude_guess = altitude_from_time(target_time)
altitude_guess_km = altitude_guess / 1000.0
print ("Target Time (s)", target_time, \
    "Required altitude (km)", altitude_guess_km)
    


# Guess reentry times and speeds
altitude = 2150e3
print ("Altitude (km)", round(altitude / 1000.0, 0))
to_atmosphere = calc_reenty(altitude, 0.0, .01, ATMOSPHERE)
to_atmosphere_speed = round(
    to_atmosphere["velocity"] *
    MACH_RATIO_SEA_LEVEL,
    2)
to_atmosphere_time = round(to_atmosphere["time"], 2)

to_ground = calc_reenty(altitude, 0.0, .01, 0.0)
to_ground_speed = round(to_ground["velocity"] * MACH_RATIO_SEA_LEVEL, 2)
to_ground_time = round(to_ground["time"], 2)


print ("Reentry time (s)", to_atmosphere_time, \
    "Reentry speed (mach)", to_atmosphere_speed)
print ("Impact time (s)", to_ground_time, \
    "Impact speed (mach)", to_ground_speed, \
    "Estimated flight time (min)", to_ground_time * 2.0 / 60.0)
