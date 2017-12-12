'''
This script shows an example of how to use the model_PsiNA class
together with the model_column time-stepping method to integrate
a simple diffusive thermocline problem forward in time 
The boundary conditions here are identical to the exmple_iteration,
and thus is the equilibrium solutions. However, the equilibrium is here approached
with a real time-stepping, which allows us to analyze the transient approach
-- but this calculation is significantly slower if we are only interested 
in the equilibrium solution
'''
import sys
sys.path.append('../Modules')
from model_PsiNA import Model_PsiNA
from model_column import Model_Column
import numpy as np
from matplotlib import pyplot as plt

# boundary conditions:
bs=0.03; bbot=-0.0004
# We will here assume b_N=0 (the default)

A_basin=8e13  #area of the basin

dt=60*86400; # timestep
niter=3000; # total number of time steps

# The next few lines are a an example for a reasonable vertically varying kappa profile:
# (to use const. kappa, simply define kappa as scalar)
kappa_back=1e-5
kappa_s=3e-5
kappa_4k=3e-4
kappa = lambda z: (kappa_back + kappa_s*np.exp(z/100)+kappa_4k*np.exp(-z/1000 - 4))  

# create grid
z=np.asarray(np.linspace(-3500, 0, 70))
# we could also use an irregular grid that's finer near the surface:
#z=np.asarray(np.linspace(-(3500.**(3./4.)), 0, 40))
#z[:-1]=-(-z[:-1])**(4./3.) 

# create initial guess for buoyancy profile in the basin
def b_basin(z): return bs*np.exp(z/300.)+bbot

# create overturning model instance
AMOC = Model_PsiNA(z=z,b_basin=b_basin)
# and solve for initial overturning streamfunction:
AMOC.solve()

# Create figure and plot initial conditions:
fig = plt.figure(figsize=(6,10))
ax1 = fig.add_subplot(111)
ax2 = ax1.twiny()
ax1.plot(AMOC.Psi, AMOC.z)
#ax2.plot(m.b_N, m.z)
ax2.plot(b_basin(z), z)
plt.ylim((-4e3,0))
ax1.set_xlim((-5,20))
ax2.set_xlim((-0.01,0.04))


# create adv-diff column model instance for basin
basin= Model_Column(z=z,kappa=kappa,Area=A_basin, b=b_basin,bs=bs,bbot=bbot)

# time-stepping loop to integrate the model
for ii in range(0, niter):    
   # update buoyancy profile
   wA=AMOC.Psi*1e6
   basin.timestep(wA=wA,dt=dt)
 
   # update overturning streamfunction
   AMOC.update(b_basin=basin.b)
   AMOC.solve()
   
   if ii%120==0:
      # Plot updated results:
      ax1.plot(AMOC.Psi, AMOC.z, linewidth=0.5)
      ax2.plot(basin.b, basin.z, linewidth=0.5)
      plt.pause(0.01)
      

# Plot final results:
ax1.plot(AMOC.Psi, AMOC.z,linewidth=2)
ax2.plot(basin.b, basin.z, linewidth=2)

