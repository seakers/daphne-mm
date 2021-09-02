import numpy as np

from .stiffness import *
from .volume_fraction import *
from .heuristics import *

__all__=['multiobjectives']

def multiobjectives(x_rvar,nucFac,sel,E,r,CA_all,c_ratio):
# This function computes the objectives for the GA to optimize. This is for 
# the real-coded case where the design vector consists of the radius values
# for the trusses between the two corresponding nodes

    # Calculated Inputs
    sidenum = 2*nucFac + 1; # Number of nodes on each size of square grid
    
    # Compute full design vector
    # x_rvar_full = np.hstack([x_rvar[0:8], x_rvar[1], x_rvar[8:16], x_rvar[10], x_rvar[0], x_rvar[3]]);
    x_rvar_full = x_rvar*r

    x_binary = x_rvar_full >= 1e-6; # binary thresholded design vector for
    # feasibility and stability score computation
    x_rvar_updated = x_rvar_full*x_binary; # setting the radii below the 
    # threshold to zero
    
    CA_des = CA_all[x_binary!=0,:];
    
    x_rvar_des = x_rvar_updated[np.nonzero(x_rvar_updated)];
    Avar = np.pi*x_rvar_des**2; # Cross-sectional areas of truss members
    
    # Generate vector with nodal coordinates
    NC = generateNC(sel,sidenum);
    
    # Develop C-matrix from K-matrix (functions below)
    C_des,_,_ = generateC(sel,x_rvar_des,NC,CA_des,Avar,E,sidenum);
    C_des = C_des/nucFac;
    
    # Calculate volume fraction
    volFrac = calcVF(NC,CA_des,x_rvar_des,sel,sidenum);

    if np.isclose(C_des[1,1], 0):
        C_des[1,1] = fiberCalc(NC,CA_des,volFrac,Avar,E,2)/nucFac #1e-3;
        C_des[0,0] = fiberCalc(NC,CA_des,volFrac,Avar,E,1)/nucFac;

    # Compute objectives with interior penalties
    obj = [C_des[1, 1]/E, volFrac];
    
    return np.around(obj,3)









