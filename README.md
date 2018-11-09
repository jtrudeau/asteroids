# asteroids
Simulating deflection of an asteroid on a collision course with Earth using lasers and other means.
Changes to Hackathon file:
- Physics simulation is running first and it's independent to FuncAnimation
- Useless printing is deleted
- Structural changes in main()
- Can now animate a slice of the simulation
- Weird angle bug is FIXED!! (there's some hardcoding to be done on line 96)
- the ability to skip a certain number of frames to make animation run faster without compromising simulation


Upcoming changes:
- Entering burn_time, laser_power and other settings at runtime
- Accepts polar coordinates as initial data (physics will still run with pseudo integration, no plan to use Keplerian orbits to this file)
- Better aesthetics
