"""This is an improvement on hackathon_stable_5.py
The physics engine computes the location independent of update() and then the data can be selectively animted with FuncAnimation
The angle theta problem is FIXED
True Newtonian physics is turned ON, and the bug that causes very little acceleration is FIXED
There's still hardcode to be done on line 96... help?
last edited by DY on 11/11/2018
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
import sys
from datetime import datetime
import time

#settings
# everything time related are in seconds
global sim_time, animation_start, animation_end, dt
sim_time = int(1e10)
dt = int(3600)
animation_start = 0
animation_end = sim_time
frame_skip = 5              # number of frames skipped per each frame
laser_power = 1e17
burn_time = 1000000

class point():
    """returns an object that is a list of two dimensional 'vectors'
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

class body():
    """return a body that has a location (2d vector), mass, velocity, name
    """
    def __init__(self, location:  float, mass, velocity, name = ''):
        self.location = location
        self.mass = mass
        self.velocity = velocity
        self.name = name
        self.x_hist = [self.location.x]
        self.y_hist = [self.location.y]

def calculate_single_body_acceleration(bodies, body_index, n, laser_power, burn_time):
    """ return the acceleration on a body in bodies caused by other bodies
    using F = G*m1*m2/r^2
    """
    g_constant = 6.6740831 *10 **(-11)
    acceleration = point(0,0)    #initializing a zero acceleration vector
    target_body = bodies[body_index]
    for index, other_body in enumerate(bodies):    #gives a list like [(1,sun),(2,earth),....]
        if index != body_index:     # the hack that only runs the physics of the Sun is turned off
            r = math.sqrt((target_body.location.x - other_body.location.x)**2 + (target_body.location.y - other_body.location.y)**2)
            try:
                temp_acc = (g_constant * other_body.mass)/r**3    #this value multiplied by the distance in 1 dimension will give the acceleration
            except ZeroDivisionError:
                print ("ZeroDivisionError occured in computing acceleration: r = 0")
                temp_acc = 0
            acceleration.x += temp_acc*(other_body.location.x - target_body.location.x)         # bug is fixed. acceleration was not additive
            acceleration.y += temp_acc*(other_body.location.y - target_body.location.y)
        else:
            pass
    if target_body.name == "asteroid":
        ax, ay = laser_acc(bodies, n, laser_power, burn_time)
        acceleration.x += ax
        acceleration.y += ay
    return acceleration

def laser_acc(bodies, n, laser_power, burn_time):
    for body in bodies:
        if body.name == "asteroid":
            laser_power = float(laser_power)
            burn_time = float(burn_time)

            laser_force = math.sqrt(1.596e-3*(laser_power-1358.41))   # in N
            number_of_time_intervals = burn_time//dt
            length = len(body.x_hist)
            if n - 2 <= number_of_time_intervals and n >= 2:      # makes sure acc isnt calculated for the first 2 ticks and stops the burn
                x1 = body.x_hist[length-2]
                x2 = body.x_hist[length-1]
                y1 = body.y_hist[length-2]
                y2 = body.y_hist[length-1]
                delta_x = x2 - x1
                delta_y = y2 - y1
                if delta_x > 0 and delta_y > 0:             # extreme hardcoding
                    theta = math.atan(delta_y/delta_x)
                elif delta_x < 0 and delta_y > 0:
                    theta = np.pi - math.atan(delta_y/abs(delta_x))
                elif delta_x < 0 and delta_y < 0:
                    theta = np.pi + math.atan(abs(delta_y)/abs(delta_x))
                elif delta_x > 0 and delta_y < 0:
                    theta = -1*math.atan(abs(delta_y)/delta_x)
                else:
                    return 0, 0             # hardcoding not done yet. cases delta_x = 0 and delta_y = 0

                acc_x = (math.cos(theta)*laser_force)/body.mass
                acc_y = (math.sin(theta)*laser_force)/body.mass
                return acc_x, acc_y
            elif n == number_of_time_intervals:
                print ("Burn finished!")   #optional
                return 0 , 0
            else:
                return 0 , 0
        else:
            pass


def calculate_velocity(bodies, n, dt, laser_power, burn_time):    # dt is equivalent to 4hrs, so 6 updates per day
    """compute all the velocity after dt and change the velocity attributes in the bodies
    """
    for body_index, target_body in enumerate(bodies):
        acceleration = calculate_single_body_acceleration(bodies, body_index, n, laser_power, burn_time)
        target_body.velocity.x += acceleration.x * dt
        target_body.velocity.y += acceleration.y * dt

def calculate_position(bodies, dt):   # dt = 4 hours, 6 ticks/day
    for body in bodies:
        body.location.x += body.velocity.x * dt
        body.location.y += body.velocity.y *dt
        body.x_hist.append(body.location.x)
        body.y_hist.append(body.location.y)


def compute_gravity_step(bodies, n, dt, laser_power, burn_time):
    calculate_velocity(bodies, n, dt, laser_power, burn_time)
    calculate_position(bodies, dt)

def progress_bar(count, total):
    bar_length = 60
    filled_length = int(round(bar_length*count/total))
    percentage = round(100*(count/total))
    bar = '='*filled_length + '-'*(bar_length-filled_length)
    print("%s  %s%s" %(bar,percentage,'%'), end='\r')

sun = {"location":point(0,0), "mass":2e30, "velocity":point(0,0)}     #sun mass = 2e30
mercury = {"location":point(0,5.7e10), "mass":3.285e23, "velocity":point(47000,0)}
venus = {"location":point(0,1.1e11), "mass":4.8e24, "velocity":point(35000,0)}
earth = {"location":point(-9.124e10,-7.830e10), "mass":6e24, "velocity":point(-2.629e4,2.417e4)}
mars = {"location":point(0,2.2e11), "mass":2.4e24, "velocity":point(24000,0)}
jupiter = {"location":point(0,7.7e11), "mass":1e28, "velocity":point(13000,0)}
saturn = {"location":point(0,1.4e12), "mass":5.7e26, "velocity":point(9000,0)}
uranus = {"location":point(0,2.8e12), "mass":8.7e25, "velocity":point(6835,0)}
neptune = {"location":point(0,4.5e12), "mass":1e26, "velocity":point(5477,0)}
pluto = {"location":point(0,3.7e12), "mass":1.3e22, "velocity":point(4748,0)}
asteroid = {"location":point(-7.133e10,-1.159e11),"mass":27e9,"velocity":point(-2.812e4,1.409e4)}

bodies = [
        body( location = sun["location"], mass = sun["mass"], velocity = sun["velocity"], name = "sun"),
        body( location = earth["location"], mass = earth["mass"], velocity = earth["velocity"], name = "earth"),
        body( location = asteroid["location"], mass = asteroid["mass"], velocity = asteroid["velocity"], name = "asteroid"),
        body( location = mars["location"], mass = mars["mass"], velocity = mars["velocity"], name = "mars"),
        body( location = venus["location"], mass = venus["mass"], velocity = venus["velocity"], name = "venus"),
        body( location = jupiter["location"], mass = jupiter["mass"], velocity = jupiter["velocity"], name = "jupiter"),
        body( location = mercury["location"], mass = mercury["mass"], velocity = mercury["velocity"], name = "mercury")]


fig, ax = plt.subplots()
ax.set_facecolor('xkcd:black')
ax.set_xlim(-1e12, 1e12)
ax.set_ylim(-1e12, 1e12)

global rock_plot, trace, sun_plot, earth_plot, text
rock_plot, = plt.plot([],[],'ro',markersize=6, animated=True)
trace, = plt.plot([],[],'bo', markersize=0.1, animated=True)
sun_plot, = plt.plot([],[],'yo',markersize=12, animated=True)
earth_plot, = plt.plot([],[], color='#2b63d8',marker='o',markerfacecolor='#2b63d8', markersize=7, animated=True)
mars_plot, = plt.plot([],[], color='#f58061',marker='o',markerfacecolor='#f58061', markersize=6, animated=True)
venus_plot, = plt.plot([],[], color="#c28033", marker='o',markerfacecolor='#c28033',markersize=5, animated=True)
mercury_plot, = plt.plot([],[], color="#d5d2d1", marker='o',markerfacecolor='#d5d2d1',markersize=4, animated=True)
jupiter_plot, = plt.plot([],[], color='#efd9a7',marker='o',markerfacecolor='#efd9a7',markersize=11, animated=True)

text = ax.text(0, 0, '', color="white", transform=ax.transAxes,fontsize=10)

def update(frame):
    start_frame = animation_start//dt
    end_frame = animation_end//dt
    frame = frame*(frame_skip+1) + int(start_frame)
    if frame == end_frame:
        print("Animation finished: start = %ds   end = %ds " %(animation_start, animation_end))
        sys.exit(0)
    for body in bodies:
        x_data, y_data = [],[]
        x_data.append(body.x_hist[frame])
        y_data.append(body.y_hist[frame])
        if body.name == "asteroid":
            rock_plot.set_data(x_data,y_data)
        elif body.name == "sun":
            sun_plot.set_data(x_data,y_data)
        elif body.name == "earth":
            earth_plot.set_data(x_data,y_data)
        elif body.name == "mars":
            mars_plot.set_data(x_data,y_data)
        elif body.name == 'venus':
            venus_plot.set_data(x_data,y_data)
        elif body.name == 'jupiter':
            jupiter_plot.set_data(x_data,y_data)
        elif body.name == 'mercury':
            mercury_plot.set_data(x_data,y_data)

    trace_x, trace_y = [],[]
    for body in bodies:
        trace_x.append(body.x_hist[0:frame])
        trace_y.append(body.y_hist[0:frame])
    trace.set_data(trace_x,trace_y)
    text.set_text(str("Time elapsed: "+ str(frame*4)+" hours"))
    return rock_plot, sun_plot, trace, earth_plot, mars_plot, venus_plot, jupiter_plot,mercury_plot, text

def main(laser_power=1e18, burn_time=100000000):
    sim_start = datetime.now()
    start_second = time.time()
    print ("Physics simulation started at %s" %(sim_start))
    frames = int(sim_time//dt)
    for t in range(0,frames):
        compute_gravity_step(bodies, t, dt, laser_power, burn_time)
        if t%(int(frames/100)) == 0:        # this hack makes the whole program run 45% faster!!
            progress_bar(t,frames)
    sim_end = datetime.now()
    end_second = time.time()
    print ("Physics simulation ended at %s, time elapsed = %s seconds" %(sim_end,round(end_second-start_second)))

    ani = FuncAnimation(fig, update, interval=1, blit=True)
    plt.show()


if __name__ == '__main__':
    main(laser_power, burn_time)
