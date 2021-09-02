# -*- coding: utf-8 -*-
"""
updated volume_fraction.py

@author: roshan94
"""
import numpy as np
import math
import statistics

_all_ = ['calcVF', 'modifyAreas', 'subNodOLVol']

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
        x1 = NC[CA[i,0],0]
        x2 = NC[CA[i,1],0]
        y1 = NC[CA[i,0],1]
        y2 = NC[CA[i,1],1]
        L = np.sqrt(((x2-x1)**2)+((y2-y1)**2))
        
        # Adding current element to total volume of trusses
        totalTrussVol = totalTrussVol + L*Avar_mod[i]
    
    # Modify total volume based on overlaps at nodes
    
    #r = rvar[0] # It is assumed that all members at equal radius (THIS MUST BE MODIFIED)
    totalTrussVol_mod = subNodOLVol(NC, CA, totalTrussVol, rvar)

    # Finding average side "thickness" due to differing element radii
    # horizrads = []
    # for i in range(CA.shape[0]):
    #     for j in range(sidenum-1):
    #         x1 = NC[CA[i,0],0]
    #         x2 = NC[CA[i,1],0]
    #         y1 = NC[CA[i,0],1]
    #         y2 = NC[CA[i,1],1]
    #         L = np.sqrt(((x2-x1)**2)+((y2-y1)**2))
    #         angle = np.arccos((x2-x1)/L)
    #         if ((CA[i,0] + ((j+1)*sidenum) == CA[i,1]) and ((NC[CA[i,0],1] == totl) or (NC[CA[i,0],1] == 0)) and (angle == 0)):
    #             for k in range(math.floor(L/singl)):
    #                 horizrads.append(rvar[i])
    #         elif ((CA[i,0] - ((j+1)*sidenum) == CA[i,1]) and ((NC[CA[i,0],1] == totl) or (NC[CA[i,0],1] == 0)) and (angle == 0)):
    #             for k in range(math.floor(L/singl)):
    #                 horizrads.append(rvar[i])
    # vertrads = []
    # for i in range(CA.shape[0]):
    #     for j in range(sidenum-1):
    #         x1 = NC[CA[i,0],0]
    #         x2 = NC[CA[i,1],0]
    #         y1 = NC[CA[i,0],1]
    #         y2 = NC[CA[i,1],1]
    #         L = np.sqrt(((x2-x1)**2)+((y2-y1)**2))
    #         angle = np.arccos((x2-x1)/L)
    #         if ((CA[i,0] + (j+1) == CA[i,1]) and ((NC[CA[i,0],0] == totl) or (NC[CA[i,0],0] == 0)) and (angle == np.pi/2)): 
    #             for k in range(math.floor(L/singl)):
    #                 vertrads.append(rvar[i])
    #         elif ((CA[i,0] - (j+1) == CA[i,1]) and ((NC[CA[i,0],0] == totl) or (NC[CA[i,0],0] == 0)) and (angle == np.pi/2)):
    #             for k in range(math.floor(L/singl)):
    #                 vertrads.append(rvar[i])
                                    
    # thick = np.mean([np.mean(horizrads),np.mean(vertrads)])
    thick = np.mean(rvar)
    
    # Calculate volume fraction (using a solid square with 2 * avg. thickness as a baseline)
    volFrac = totalTrussVol_mod/(2*thick*(totl**2))
    return volFrac  

# FUNCTION TO MODIFY AREAS FOR EDGE MEMBERS
def modifyAreas(Avar,CA,NC,sidenum):
    # Identify edge nodes
    left_edgenodes = np.arange(1,sidenum)
    right_edgenodes = np.arange(((sidenum**2)-sidenum+1),(sidenum**2))
    bottom_edgenodes = np.arange(sidenum,((sidenum**2)-sidenum),sidenum)
    top_edgenodes = np.arange(2*sidenum-1,sidenum**2-1,sidenum)
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
        x1 = NC[CA_edgenodes[i,0],0]; x2 = NC[CA_edgenodes[i,1],0];
        y1 = NC[CA_edgenodes[i,0],1]; y2 = NC[CA_edgenodes[i,1],1];
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

# FUNCTION TO SUBTRACT VOLUME OVERLAP AT NODES
def subNodOLVol(NC,CA,tTV,r_var):
    CA_col1 = [x[0] for x in CA]
    CA_col2 = [x[1] for x in CA]
    for i in range(NC.shape[0]):
        # Isolate members starting/ending at current node
        indiOne = [m for m in range(len(CA_col1)) if CA_col1[m] == i]
        indiTwo = [m for m in range(len(CA_col2)) if CA_col2[m] == i]
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
        
        if mCA.size==0:
            continue

        #mCA = mCA[mCA[:,0].argsort()]
        # Loop through each pair of connecting members at the current node
        for i in range(mCA.shape[0]):
            for j in range(mCA.shape[0]): 
                if i != j:
                    # Find the sweep angle between the connecting members 
                    p1 = np.array([NC[mCA[i,0],0], NC[mCA[i,0],1]])
                    q1 = np.array([NC[mCA[i,1],0], NC[mCA[i,1],1]])
                    p2 = np.array([NC[mCA[j,0],0], NC[mCA[j,0],1]])
                    q2 = np.array([NC[mCA[j,1],0], NC[mCA[j,1],1]])
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
                