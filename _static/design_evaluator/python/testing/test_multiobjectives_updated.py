# -*- coding: utf-8 -*-
"""
Testing multiobjectives_updated

@author: roshan94
"""
import numpy as np
import math
import statistics
from itertools import combinations 

#### FUNCTIONS

# Alternate multiobjectives function
def multiobjectives(x_rvar,sidenum,sel,E,r_var,CA_all,c_ratio):
# This function computes the objectives for the GA to optimize. This is for 
# the real-coded case where the design vector consists of the radius values
# for the trusses between the two corresponding nodes

    # Assuming nucFac = 1 
    nucFac = 1
    
    # Compute full design vector
    # x_rvar_full = np.hstack([x_rvar[0:8], x_rvar[1], x_rvar[8:16], x_rvar[10], x_rvar[0], x_rvar[3]]);
    x_rvar_full = np.multiply(x_rvar,r_var)

    x_binary = x_rvar_full >= 1e-6; # binary thresholded design vector for
    # feasibility and stability score computation
    x_rvar_updated = x_rvar_full*x_binary; # setting the radii below the 
    # threshold to zero
    
    #member_index = 0
    #x_rvar_updated = np.zeros((x_rvar.shape[0]))
    #for i in range(x_rvar.shape[0]):
        #if x_rvar[i]:
            #x_rvar_updated[i] = r_var[member_index]
            #member_index = member_index + 1
    
    #x_binary = x_rvar
    
    CA_des = CA_all[x_binary!=0,:];
    
    x_rvar_des = x_rvar_updated[np.nonzero(x_rvar_updated)];
    Avar = np.pi*x_rvar_des**2; # Cross-sectional areas of truss members
    
    NC = generateNC(sel, sidenum)
    
    Avar_mod = modifyAreas(Avar,CA_des,NC,sidenum) # modify for edge members
    
    # Generate vector with nodal coordinates
    NC = generateNC(sel,sidenum);
    
    # Develop C-matrix from K-matrix (functions below)
    C_des,_,_ = generateC(sel,x_rvar_des,NC,CA_des,Avar_mod,E,sidenum);
    C_des = C_des/nucFac;
    
    # Calculate volume fraction
    volFrac = calcVF(NC,CA_des,x_rvar_des,sel,sidenum);

    if np.isclose(C_des[1,1], 0):
        C_des[1,1] = fiberCalc(NC,CA_des,volFrac,Avar_mod,E,2)/nucFac #1e-3;
        C_des[0,0] = fiberCalc(NC,CA_des,volFrac,Avar_mod,E,1)/nucFac;

    # Compute objectives with interior penalties
    obj = [C_des[1, 1]/E, volFrac];
    
    return np.around(obj,3)

# FUNCTION TO GENERATE NODAL COORDINATES BASED ON GRID SIZE
def generateNC(sel,sidenum):
    notchvec = np.linspace(0,1,sidenum);
    NC = [];
    for i in range(sidenum):
        # y_start = i%2
        # direction = 1-2*(i%2)
        for j in range(sidenum):
            NC.append([notchvec[i], notchvec[j]]);
    
    NC = sel*np.array(NC);

    return NC

def fiberCalc(NC,CA,volFrac,Avar,E,dire):    
    # Find effective structural stiffness
    K = E*volFrac;
    
    # Find volume-corrected sum of cosines for all fibers 
    cVsum = 0;
    Vsum = 0;
    for i in range(CA.shape[0]):
        x1 = NC[CA[i,0]-1,0]; x2 = NC[CA[i,1]-1,0];
        y1 = NC[CA[i,0]-1,1]; y2 = NC[CA[i,1]-1,1];
        L = np.sqrt(((x2-x1)**2)+((y2-y1)**2));
        if dire == 1:
            c=(x2-x1)/L; 
        elif dire == 2:
            c=(y2-y1)/L; 
        cVsum = cVsum + (L*(Avar[i])*(c**4));
        Vsum = Vsum + (L*Avar[i]);
    
    # Find desired C-value
    if Vsum!=0:
        Cval = (K*cVsum)/Vsum;
    else:
        Cval=0

    return Cval


# FUNCTION TO FORM GLOBAL STRUCTURAL STIFFNESS MATRIX
def formK(NC,CA,Avar,E):
    # Forming Elemental Stiffness Matrices
    Kbasket = [];
    for i in range(CA.shape[0]):
        x1 = NC[CA[i,0]-1,0]; x2 = NC[CA[i,1]-1,0];
        y1 = NC[CA[i,0]-1,1]; y2 = NC[CA[i,1]-1,1];
        L = np.sqrt((x2-x1)**2+(y2-y1)**2);
        c=(x2-x1)/L; c2 = c**2;
        s=(y2-y1)/L; s2 = s**2;
        ktemp = np.array([[c2,   c*s,  -c2,  -c*s],  
                 [c*s,   s2,  -c*s,  -s2],    
                 [-c2, -c*s,  c2,    c*s], 
                 [-c*s, -s2,  c*s,   s2]]);
        ke = Avar[i]*E/L*ktemp;
        Kbasket.append(ke);

    # Global-to-local-coordinate-system Coordination
    GlobToLoc=np.zeros((CA.shape[0],4));
    for n in [0, 1]: 
        GN=CA[:,n]; 
        for d in [0, 1]:
            GlobToLoc[:,n*2+d]=(GN-1)*2+d;

    GlobToLoc = GlobToLoc.astype(int)

    # Forming Global Truss Stiffness Matrix
    K = np.zeros((2*NC.shape[0],2*NC.shape[0]));
    for e in range(CA.shape[0]):
        ke = Kbasket[e];
        for lr in range(4):
            gr = GlobToLoc[e,lr]; 
            for lc in range(4):
                gc = GlobToLoc[e,lc]; 
                K[gr,gc] = K[gr,gc] + ke[lr,lc];

    return K

# FUNCTION TO CALCULATE C-MATRIX
def generateC(sel,rvar,NC,CA,Avar,E,sidenum):
    # Initialize outputs
    C = []; uBasket = []; FBasket = [];
    
    # Iterate through once for each strain component
    for y in range(3):
        # Define vectors to hold indexes for output forces
        Fi_x = []; Fi_y = []; Fi_xy = [];
    
        # Define strain vector: [e11, e22, e12]'
        strainvec = np.zeros((3,1));

        # set that component equal to a dummy value (0.01 strain), 
        # set all other values to zero
        strainvec[y] = 0.01; 
        strainvec[2] = strainvec[2]*2;

        # use strain relations, BCs, and partitioned K-matrix to 
        # solve for all unknowns
        e11 = strainvec[0]; e22 = strainvec[1]; e12 = strainvec[2];
        if (e11 != 0) or (e22 != 0): # when testing non-zero e11 or e22:
            K = formK(NC,CA,Avar,E); # function for this below
            u_r = []; F_q = []; qvec = []; rvec = [];
            # Assigning Force/Displacement BCs for different nodes/DOFs
            for x in range(NC.shape[0]): # looping through nodes by coordinate
                ND = NC/sel;
                # Separating conditions for exterior nodes
                if (np.isin(ND[x,0],[0,1]) == True) or (np.isin(ND[x,1],[0,1]) == True):
                    # Finding x-DOF
                    if ND[x,0] == 0:
                        # displacement in x = 0
                        u_r.append([0]);
                        rvec.append(2*x);
                    elif ND[x,0] == 1:
                        # displacement in x = e11*sel
                        u_r.append([e11*sel]);
                        rvec.append(2*x);
                        Fi_x.append(2*x);
                    elif (ND[x,1] == 0) and (e22 != 0):
                        # displacement in x = 0
                        u_r.append([0]);
                        rvec.append(2*x);
                    else:
                        # x-direction DOF is a force BC
                        F_q.append([0]);
                        qvec.append(2*x);
                    
                    # Finding y-DOF
                    if ND[x,1] == 0:
                        # displacement in y = 0
                        u_r.append([0]);
                        rvec.append(2*x+1);
                    elif ND[x,1] == 1:
                        # displacement in y = e22*sel
                        u_r.append([e22*sel]);
                        rvec.append(2*x+1);
                        Fi_y.append(2*x+1);
                        Fi_xy.append(2*x);
                    elif (ND[x,0] == 0) and (e11 != 0):
                        # displacement in y = 0
                        u_r.append([0]);
                        rvec.append(2*x);
                    else:
                        # y-direction DOF is a force BC
                        F_q.append([0]);
                        qvec.append(2*x+1);

                else: # Condition for all interior nodes
                    # both x- and y-DOFs are force BCs
                    F_q.extend([[0], [0]]);
                    qvec.extend([2*x, 2*x+1]);

            qrvec = np.hstack([qvec, rvec]);
            newK = np.vstack([K[qvec,:],K[rvec,:]]);
            newK = np.hstack([newK[:,qvec],newK[:,rvec]]);
            K_qq = newK[0:len(qvec),0:len(qvec)];
            K_rq = newK[len(qvec):2*NC.shape[0],0:len(qvec)];
            K_qr = newK[0:len(qvec),len(qvec):2*NC.shape[0]];
            K_rr = newK[len(qvec):2*NC.shape[0], len(qvec):2*NC.shape[0]];
            F_q = np.array(F_q, dtype='float'); u_r = np.array(u_r, dtype='float');
            u_q = np.linalg.lstsq(K_qq, F_q-np.dot(K_qr,u_r), rcond=None)[0]; 
            F_r = np.dot(K_rq, u_q) + np.dot(K_rr, u_r);
            altu = np.vstack([u_q, u_r]); altF = np.vstack([F_q, F_r]);
            F = np.zeros((len(altF),1)); u = np.zeros((len(altu),1));
            for x in range(len(qrvec)):
                F[qrvec[x]] = altF[x];
                u[qrvec[x]] = altu[x];
            
        else: # when testing non-zero e12
            K = formK(NC,CA,Avar,E); # function for this below
            u_r = []; F_q = []; qvec = []; rvec = [];
            # Assigning Force/Displacement BCs for different nodes/DOFs
            for x in range(NC.shape[0]): # looping through nodes by coordinate
                # Separating conditions for exterior nodes 
                ND = NC/sel;
                if (np.isin(ND[x,0],[0,1]) == True) or (np.isin(ND[x,1],[0,1]) == True):
                    # Finding x-DOF
                    if ND[x,0] == 0:
                        # displacement in x is proportional to y-coordinate
                        # (due to nature of shear)
                        u_r.append([e12*sel*ND[x,1]]);
                        rvec.append(2*x);
                    elif ND[x,0] == 1:
                        # displacement in x is proportional to y-coordinate
                        # (due to nature of shear)
                        u_r.append([e12*sel*ND[x,1]]);
                        rvec.append(2*x);
                        Fi_x.append(2*x);
                    elif ND[x,1] == 1:
                        # displacement in x = e12*sel
                        u_r.append([e12*sel]);
                        rvec.append(2*x);
                    elif ND[x,1] == 0:
                        # displacement in x = 0
                        u_r.append([0]);
                        rvec.append(2*x);
                    else:
                        # x-direction DOF is a force BC
                        F_q.append([0]);
                        qvec.append(2*x);
                    
                    # Finding y-DOF
                    if ND[x,1] == 0:
                        # displacement in y = 0
                        u_r.append([0]);
                        rvec.append(2*x+1);
                    elif ND[x,1] == 1:
                        # displacement in y = 0
                        u_r.append([0]);
                        rvec.append(2*x+1);
                        Fi_y.append(2*x+1);
                        Fi_xy.append(2*x);
                    else:
                        # y-direction DOF is a force BC
                        F_q.append([0]);
                        qvec.append(2*x+1);
                    
                else: # Blanket condition for all interior nodes
                    # both x- and y-DOFs are force BCs
                    F_q.extend([[0], [0]]);
                    qvec.extend([2*x, 2*x+1]);

            qrvec = np.hstack([qvec, rvec]);
            newK = np.vstack([K[qvec,:],K[rvec,:]]);
            newK = np.hstack([newK[:,qvec],newK[:,rvec]]);
            K_qq = newK[0:len(qvec),0:len(qvec)];
            K_rq = newK[len(qvec):2*NC.shape[0],0:len(qvec)];
            K_qr = newK[0:len(qvec),len(qvec):2*NC.shape[0]];
            K_rr = newK[len(qvec):2*NC.shape[0], len(qvec):2*NC.shape[0]];
            F_q = np.array(F_q, dtype='float'); u_r = np.array(u_r, dtype='float')
            u_q = np.linalg.lstsq(K_qq, F_q-np.dot(K_qr,u_r), rcond=None)[0]; 
            F_r = np.dot(K_rq, u_q) + np.dot(K_rr, u_r);
            altu = np.vstack([u_q, u_r]); altF = np.vstack([F_q, F_r]);
            F = np.zeros((len(altF),1)); u = np.zeros((len(altu),1));
            for x in range(len(qrvec)):
                F[qrvec[x]] = altF[x];
                u[qrvec[x]] = altu[x];

    #   Finding average side "thicknesses" due to differing element radii
        horizrads = [];
        for i in range(CA.shape[0]):
            if ((CA[i,0] + sidenum) == CA[i,1]) and (NC[CA[i,0],1] == sel):
                horizrads.append(rvar[i]);
            
        vertrads = [];
        for i in range(CA.shape[0]):
            if ((CA[i,0] + 1) == CA[i,1]) and (NC[CA[i,0],0] == sel):
                vertrads.append(rvar[i]);
           
        horizmean = np.mean(horizrads);
        vertmean = np.mean(vertrads);
    
    #   use system-wide F matrix and force relations to solve for 
    #       stress vector [s11,s22,s12]'
        F_x = 0; F_y = 0; F_xy = 0;
        Fi_xy = np.array(Fi_xy, dtype='int32')
        for n in range(Fi_xy.shape[0]):
            F_x = F_x + F[Fi_x[n]];
            F_y = F_y + F[Fi_y[n]];
            F_xy = F_xy + F[Fi_xy[n]];
        
        stressvec = np.vstack([F_x/(sel*2*vertmean), F_y/(sel*2*horizmean),
                     F_xy/(sel*2*horizmean)]);

    #   use strain and stress vectors to solve for the corresponding
    #       row of the C matrix
        Cdummy = stressvec/strainvec[:,None];
        Cdummy = np.nan_to_num(Cdummy, nan=0, posinf=0, neginf=0)
        Cdummy_y = Cdummy[y]
        Cdummy_list = [x[0] for x in Cdummy_y]
        C.append(Cdummy_list)
        #C.append(Cdummy[:,y])
        FBasket.append([F]);
        uBasket.append([u]);

    C = np.transpose(np.array(C))
    FBasket = np.array(FBasket).T
    uBasket = np.array(uBasket).T

    return C,uBasket,FBasket

## ADDED BY ROSHAN

# FUNCTION TO GENERATE FULL CA
def generate_full_CA(sidenum):
    nodes_list = np.arange(sidenum**2)
    nodes_list = nodes_list + 1
    
    return np.array(list(combinations(nodes_list,2)))

# FUNCTION TO MODIFY AREAS FOR EDGE MEMBERS
def modifyAreas(Avar,CA,NC,sidenum):
    # Identify edge nodes
    left_edgenodes = list(range(1,sidenum+1))
    right_edgenodes = list(range(((sidenum**2)-sidenum+1),((sidenum**2)+1)))
    bottom_edgenodes = list(range(sidenum+1,((sidenum**2)-sidenum),sidenum))
    top_edgenodes = list(range(2*sidenum,sidenum**2,sidenum))
    edge_nodes = left_edgenodes + bottom_edgenodes + top_edgenodes + right_edgenodes 
    
    # Identify members connecting solely to edge nodes
    edge_connectors = np.zeros((CA.shape[0]))
    for i in range(CA.shape[0]):
        member = CA[i]
        edge_connectors[i] = np.all(np.isin(list(member),edge_nodes))
    
    # Isolate edge members based on angle
    #edge_logical = np.transpose(np.vstack((edge_connectors, edge_connectors)))
    #CA_edgenodes_wz = np.multiply(CA,edge_logical)
    #CA_edgenodes_nzrows = np.where(np.array(CA_edgenodes_wz).any(axis=0))
    #CA_edgenodes = np.array(CA_edgenodes_wz)[CA_edgenodes_nzrows]
    CA_edgenodes = CA[edge_connectors > 0.5]
    angles = np.zeros(CA_edgenodes.shape[0])
    for i in range(CA_edgenodes.shape[0]):
        # Finding element length from nodal coordinates
        x1 = NC[CA_edgenodes[i,0]-1,0]; x2 = NC[CA_edgenodes[i,1]-1,0];
        y1 = NC[CA_edgenodes[i,0]-1,1]; y2 = NC[CA_edgenodes[i,1]-1,1];
        L = np.sqrt(((x2-x1)**2)+((y2-y1)**2));
        angles[i] = np.degrees(np.abs(np.arccos((x2-x1)/L)))
        
    edgerows = [(x == 0) or (x == 90) for x in angles]
    CA_edgy = CA_edgenodes[edgerows]
    
    # Find and modify areas of edge members
    if list(CA_edgy):
        for edge_member in CA_edgy:
            member_index = np.argwhere(np.all(CA == edge_member,axis=1))[0,0]
            Avar[member_index] = Avar[member_index]/2
            
    return Avar

# FUNCTION TO COMPUTE VOLUME FRACTION (EDGE AND NODAL OVERLAP CORRECTED)
def calcVF(NC,CA,rvar,sel,sidenum):
    # Calculate Avar and modify edge member areas
    Avar = math.pi*(rvar**2)
    Avar_mod = modifyAreas(Avar, CA, NC, sidenum)
    
    # Calculate cumulative volume of all individual members
    totalTrussVol = 0
    totl = sel
    singl = totl/(sidenum-1)
    for i in range(CA.shape[0]):
        # Finding element length from nodal coordinates
        x1 = NC[CA[i,0]-1,0]
        x2 = NC[CA[i,1]-1,0]
        y1 = NC[CA[i,0]-1,1]
        y2 = NC[CA[i,1]-1,1]
        L = np.sqrt(((x2-x1)**2)+((y2-y1)**2))
        
        # Adding current element to total volume of trusses
        totalTrussVol = totalTrussVol + L*Avar_mod[i]
    
    # Modify total volume based on overlaps at nodes
    
    #r = rvar[0] # It is assumed that all members at equal radius (THIS MUST BE MODIFIED)
    totalTrussVol_mod = subNodOLVol(NC, CA, totalTrussVol, rvar)

    # Finding average side "thickness" due to differing element radii
    horizrads = []
    for i in range(CA.shape[0]):
        for j in range(sidenum-1):
            x1 = NC[CA[i,0]-1,0]
            x2 = NC[CA[i,1]-1,0]
            y1 = NC[CA[i,0]-1,1]
            y2 = NC[CA[i,1]-1,1]
            L = np.sqrt(((x2-x1)**2)+((y2-y1)**2))
            angle = np.arccos((x2-x1)/L)
            if ((CA[i,0] + ((j+1)*sidenum) == CA[i,1]) and ((NC[CA[i,0]-1,1] == totl) or (NC[CA[i,0]-1,1] == 0)) and (angle == 0)):
                for k in range(math.floor(L/singl)):
                    horizrads.append(rvar[i])
            elif ((CA[i,0] - ((j+1)*sidenum) == CA[i,1]) and ((NC[CA[i,0]-1,1] == totl) or (NC[CA[i,0]-1,1] == 0)) and (angle == 0)):
                for k in range(math.floor(L/singl)):
                    horizrads.append(rvar[i])
    vertrads = []
    for i in range(CA.shape[0]):
        for j in range(sidenum-1):
            x1 = NC[CA[i,0]-1,0]
            x2 = NC[CA[i,1]-1,0]
            y1 = NC[CA[i,0]-1,1]
            y2 = NC[CA[i,1]-1,1]
            L = np.sqrt(((x2-x1)**2)+((y2-y1)**2))
            angle = np.arccos((x2-x1)/L)
            if ((CA[i,0] + (j+1) == CA[i,1]) and ((NC[CA[i,0]-1,0] == totl) or (NC[CA[i,0]-1,0] == 0)) and (angle == np.pi/2)): 
                for k in range(math.floor(L/singl)):
                    vertrads.append(rvar[i])
            elif ((CA[i,0] - (j+1) == CA[i,1]) and ((NC[CA[i,0]-1,0] == totl) or (NC[CA[i,0]-1,0] == 0)) and (angle == np.pi/2)):
                for k in range(math.floor(L/singl)):
                    vertrads.append(rvar[i])
                                    
    thick = statistics.mean([statistics.mean(horizrads),statistics.mean(vertrads)])
    
    # Calculate volume fraction (using a solid square with 2 * avg. thickness as a baseline)
    volFrac = totalTrussVol_mod/(2*thick*(totl**2))
    return volFrac                

# FUNCTION TO SUBTRACT VOLUME OVERLAP AT NODES
def subNodOLVol(NC,CA,tTV,r_var):
    CA_col1 = [x[0] for x in CA]
    CA_col2 = [x[1] for x in CA]
    for i in range(NC.shape[0]):
        # Isolate members starting/ending at current node
        indiOne = [m for m in range(len(CA_col1)) if CA_col1[m] == i+1]
        indiTwo = [m for m in range(len(CA_col2)) if CA_col2[m] == i+1]
        mCAone = CA[indiOne]
        mCAtwo = CA[indiTwo]
        
        #common_elems_ind_mCAone = (mCAone[:, None] == mCAtwo).all(-1).any(-1)
        #diff_elems_ind_mCAone = [not elem for elem in common_elems_ind_mCAone]
        #common_elems_ind_mCAtwo = (mCAtwo[:, None] == mCAone).all(-1).any(-1)
        #diff_elems_ind_mCAtwo = [not elem for elem in common_elems_ind_mCAtwo]
        
        #mCA = np.vstack((diff_elems_ind_mCAone,diff_elems_ind_mCAtwo))
        
        mCAone_set = set([tuple(x) for x in mCAone])
        mCAtwo_set = set([tuple(x) for x in mCAtwo])
        
        diff_elems_mCAone = np.asarray(list(mCAone_set - mCAtwo_set))
        diff_elems_mCAtwo = np.asarray(list(mCAtwo_set - mCAone_set))
        
        if ((diff_elems_mCAtwo.shape[0] == 0) and (diff_elems_mCAone.shape[0] != 0)):
            mCA = diff_elems_mCAone
        elif ((diff_elems_mCAone.shape[0] == 0) and (diff_elems_mCAtwo.shape[0] != 0)):
            mCA = diff_elems_mCAtwo
        else:
            mCA = np.vstack((diff_elems_mCAone,diff_elems_mCAtwo))
            
        #mCA = mCA[mCA[:,0].argsort()]
        
        # Loop through each pair of connecting members at the current node
        for i in range(mCA.shape[0]):
            for j in range(mCA.shape[0]): 
                if i != j:
                    # Find the sweep angle between the connecting members 
                    p1 = np.array([NC[mCA[i,0]-1,0], NC[mCA[i,0]-1,1]])
                    q1 = np.array([NC[mCA[i,1]-1,0], NC[mCA[i,1]-1,1]])
                    p2 = np.array([NC[mCA[j,0]-1,0], NC[mCA[j,0]-1,1]])
                    q2 = np.array([NC[mCA[j,1]-1,0], NC[mCA[j,1]-1,1]])
                    v1 = np.array([q1[0],q1[1],0]) - np.array([p1[0],p1[1],0]) 
                    v2 = np.array([q2[0],q2[1],0]) - np.array([p2[0],p2[1],0])
                    
                    alpha = np.arccos(np.max([np.min([np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)),1]),-1]))
                    theta = math.pi - alpha
                    
                    # Check if members overlap
                    if ((np.abs(theta - math.pi) < 1e-5) or (np.abs(theta) < 1e-5)):
                        continue
                    else:
                        # Find the volume of each overlap sphere sector, subtract from the total truss volume
                        frac = theta/(2*math.pi)
                        member_index_i = np.argwhere(np.all(CA == mCA[i],axis=1))[0,0]
                        member_index_j = np.argwhere(np.all(CA == mCA[j],axis=1))[0,0]
                        r_member_i = r_var[member_index_i]
                        r_member_j = r_var[member_index_j]
                        r_avg = np.mean(np.array([r_member_i, r_member_j]))
                        VOL = ((4*math.pi)/3)*(r_avg**3)*frac
                        tTV = tTV - VOL
                        
    return tTV

#### TESTING FUNCTION ON RANDOM DESIGN 

sel = 10e-3
sidenum = 3
E = 1.8162e6
c_ratio = 1
CA = np.array([[1,2],[2,3],[1,4],[1,5],[2,5],[3,5],[3,6],[4,5],[5,6],[4,7],[5,7],[5,8],[5,9],[6,9],[7,8],[8,9]])
CA = CA[np.argsort(CA[:,0])]
CA_full = generate_full_CA(sidenum)

x_rvar = np.zeros((CA_full.shape[0]))
for i in range(CA_full.shape[0]):
    member = CA_full[i]
    if list(member) in CA.tolist():
        x_rvar[i] = 1

rvar = x_rvar*(250e-6)
objs = multiobjectives(x_rvar,sidenum,sel,E,rvar,CA_full,c_ratio)

## The expected output for the example, based on the original Matlab code is:
# C = [1.9308, 0.5043, 0.000;
#      0.5043, 1.9308, 0;
#      0, 0, 0.5043] * 1e5
# vol_frac = 0.2354

