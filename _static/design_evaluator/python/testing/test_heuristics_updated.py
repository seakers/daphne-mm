# -*- coding: utf-8 -*-
"""
Testing feasibility and connectivity functions from heuristics_updated.py

@author: roshan94
"""
import numpy as np
import networkx as nx

#### FUNCTIONS

# FUNCTION TO GENERATE NODAL COORDINATES BASED ON GRID SIZE
def findLineSegIntersection(p1,q1,p2,q2):
# This boolean function determines whether two line segments intersect,
# given their endpoints as inputs
    if (findOrientation(p1,q1,p2) != findOrientation(p1,q1,q2)) and (findOrientation(p2,q2,p1) != findOrientation(p2,q2,q1)):
        if np.all(np.isclose(p1,p2)) or np.all(np.isclose(q1,q2)) or np.all(np.isclose(p1,q2)) or np.all(np.isclose(q1,p2)):
            intersect = False; 
        else:
            intersect = True;
    else:
        intersect = False;
    
    return intersect

def findOrientation(p,q,r):
# This function finds the orientation of an ordered triplet (p, q, r)
# The function returns one of three following values:
# 0 --> p, q and r are colinear 
# 1 --> Clockwise 
# 2 --> Counterclockwise 
    val = (q[1]-p[1])*(r[0]-q[0])-(q[0]-p[0])*(r[1]-q[1]);
    if val == 0:
        orientation = 0;
    elif val > 0:
        orientation = 1;
    else:
        orientation = 2;
    
    return orientation

def findSlope(x1, y1, x2, y2):
    den = x2-x1
    num = y2-y1
    m = num/den if den!=0 else 1000;
    return m

def createGraph(NC, CA):
    G = nx.Graph()
    G.add_nodes_from(range(9))
    G.add_edges_from(CA)
    return G

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

# FUNCTION TO COMPUTE DESIGN FEASIBILITY
def feasibility(NC,CA_des,sidenum):
# This function computes the feasibility score for a design 
# Inputs: nodal position matrix NC 
#         Design Connectivity Array CA_des         
    feasibilityScore = 1;

    # FIRST CONSTRAINT: members only intersect at nodes (no crossing)
    # Sort points from left to right by x-position
    SortedCA = CA_des[np.argsort(CA_des, axis=0)[:,0]]
    
    # Develop 4xM matrix of line segment endpoint coordinates, where M is 
    #   the number of truss members.  Each row of format (x1,y1,x2,y2),
    #   where point 1 is leftmost, point 2 is rightmost
    PosA = np.vstack([ NC[SortedCA[:,0]-1,0], NC[SortedCA[:,0]-1,1], NC[SortedCA[:,1]-1,0], NC[SortedCA[:,1]-1,1] ]).T;

    # Loop through each pair of elements
    for i in range(PosA.shape[0]):
        for j in range(PosA.shape[0]):
            if i==j:
                continue
            # Determine whether the given pair of elements intersects
            intersect = findLineSegIntersection([PosA[i,0],PosA[i,1]],[PosA[i,2],PosA[i,3]],[PosA[j,0],PosA[j,1]],[PosA[j,2],PosA[j,3]]);
            # Throw an error, given an intersection
            if intersect == True:
                feasibilityScore = feasibilityScore - 0.05;
                if feasibilityScore < 0.05:
                    return feasibilityScore
                #{
                # print(i, j)
                #D = ['The element from ('+str(PosA[i,0])+','+
                     #str(PosA[i,1])+') to ('+str(PosA[i,2])+
                     #','+str(PosA[i,3])+') intersects with the' +
                     #' element from (',str(PosA[j,0])+',' +
                     #str(PosA[j,1])+') to (',str(PosA[j,2])+','+
                     #str(PosA[j,3])+')'];
                # print(D);
                #}
                
        # This constraint is not included in this version because the definition of edges does not allow overallping.
    # SECOND CONSTRAINT: Elements (of either the same or different lengths) 
    #   cannot overlap
    # Loop through each element
    #for k in range(SortedCA.shape[0]):
    #     # Loop through each element again, to consider each possible pair of elements
    #     mk = findSlope(NC[SortedCA[k,0]-1,0], NC[SortedCA[k,0]-1,1], NC[SortedCA[k,1]-1,0], NC[SortedCA[k,1]-1,1]);
    #
    #     for q in range(SortedCA.shape[0]):
    #        # If the same element is being compared twice, move on
    #        if k == q:
    #            continue
    #
    #        # Check if both elements share a common startpoint
    #        if (NC[SortedCA[k,0]-1,0] == NC[SortedCA[q,0]-1,0]) and (NC[SortedCA[k,0]-1,1] == NC[SortedCA[q,0]-1,1]):
    #             # Check if both elements have the same slope (and reject the design if so)
    #             mq = findSlope(NC[SortedCA[q,0]-1,0], NC[SortedCA[q,0]-1,1], NC[SortedCA[q,1]-1,0], NC[SortedCA[q,1]-1,1]);
    #             if mk == mq:
    #                 feasibilityScore = feasibilityScore - 0.1;
    #                 if feasibilityScore < 0.1:
    #                     return feasibilityScore
    #               
    #                #{
    #                #D = ['The element from ('+str(PosA[k,0])+','+
    #                  #str(PosA[k,1])+') to ('+str(PosA[k,2])+
    #                  #','+str(PosA[k,3])+') overlaps with the'+
    #                  #' element from ('+str(PosA[q,0])+','+
    #                  #str(PosA[q,1])+') to ('+str(PosA[q,2])+','+
    #                  #str(PosA[q,3])+')'];
    #               #print(D);
    #               #}

    # THIRD CONSTRAINT: Metamaterial should be internally connected. (intracell connectivity)
    # The bottom layer and the top layer should be connected at at least one node.
    # Left layer and right layer should be connected at at least one node
    G = createGraph(NC, SortedCA)
    connected_components = list(nx.connected_components(G))
    horz_connecting_nodes = [[0,6], [1,7], [2,8]]
    vert_connecting_nodes = [[0,2], [3,5], [6,8]]
    diag_connecting_nodes = [[[1,5], [3,7]], [[1,3], [5,7]], [[0,8],[0,8]], [[2,6],[2,6]]]

    horz_bool = []
    vert_bool = []
    diag_bool = []

    for g in connected_components:
        g = list(g)
        horz_bool.append(np.any(np.all(np.isin(horz_connecting_nodes, g), axis=1)))
        vert_bool.append(np.any(np.all(np.isin(vert_connecting_nodes, g), axis=1)))
        diag_bool.append(np.all(np.isin(diag_connecting_nodes, g), axis=-1))

    horz_bool = np.array(horz_bool)
    vert_bool = np.array(vert_bool)
    diag_bool = np.all(np.any(np.array(diag_bool), axis=0), axis=-1)

    # diagonal_connecting_nodes = [[[1,5], [3, 7]], [[1,3], [5,7]]]
    # connecting_diagonal_pair_present = any([ all(ls in SortedCA.tolist() for ls in lists) for lists in diagonal_connecting_nodes])

    if sum([np.any(diag_bool), np.any(horz_bool), np.any(vert_bool)])<2:
        if np.all(~horz_bool):
            feasibilityScore = feasibilityScore - 0.1;
            if feasibilityScore < 0.1:
                return feasibilityScore
        if np.all(~vert_bool):
            feasibilityScore = feasibilityScore - 0.1;
            if feasibilityScore < 0.1:
                return feasibilityScore
            
    # FOURTH CONSTRAINT: Metamaterial unit cell must be connected to its neighbouring unit cells. (Intercell connectivity)
    # Check if design has at least one repeated external contact point in the x and y directions
    left_edgenodes = np.arange(2,sidenum)
    right_edgenodes = np.arange(((sidenum**2)-sidenum+2),((sidenum**2)))
    bottom_edgenodes = np.arange(sidenum+1,((sidenum**2)-sidenum),sidenum)
    top_edgenodes = np.arange(2*sidenum,sidenum**2,sidenum)
    
    corner_nodes = np.array([1,sidenum,((sidenum**2)-sidenum+1),sidenum**2])
    lr_nodepairs = np.vstack((left_edgenodes,right_edgenodes))
    tb_nodepairs = np.vstack((bottom_edgenodes,top_edgenodes))
    
    used_nodes = np.unique(SortedCA)
    
    # Determine if design has atleast one repeated external point
    contactbool_x = False
    contactbool_y = False
    for y in range(used_nodes.shape[0]):
        other_nodes = np.delete(used_nodes,y)
        if np.isin(used_nodes[y],corner_nodes):
            cnodes = corner_nodes[corner_nodes!=used_nodes[y]]
            if np.any(np.isin(cnodes,other_nodes)):
                contactbool_x = True
                contactbool_y = True
                break
        elif np.isin(used_nodes[y],lr_nodepairs):
            indices = np.where(lr_nodepairs == used_nodes[y])
            if indices[1] == 0:
                if np.isin(lr_nodepairs[indices[0],1],other_nodes):
                    contactbool_x = True
                    if contactbool_y:
                        break
            elif indices[1] == 1:
                if np.isin(lr_nodepairs[indices[0],0],other_nodes):
                    contactbool_x = True
                    if contactbool_y:
                        break
        elif np.isin(used_nodes[y],tb_nodepairs):
            indices = np.where(tb_nodepairs == used_nodes[y])
            if indices[1] == 0:
                if np.isin(tb_nodepairs[indices[0],1],other_nodes):
                    contactbool_y = True
                    if contactbool_x:
                        break
            elif indices[1] == 1:
                if np.isin(tb_nodepairs[indices[0],0],other_nodes):
                    contactbool_y = True
                    if contactbool_x:
                        break
                    
    # Score design unilaterally based on absence of contact points
    if (not (contactbool_x and contactbool_y)):
        feasibilityScore = feasibilityScore - 0.1;
        if feasibilityScore < 0.1:
            return feasibilityScore

    return np.around(feasibilityScore,2)

# FUNCTION TO TEST 2D TRUSS CONNECTIVITY
def connectivity_PBC(sidenum,CA,NC,sel):
    # Initialize connectivity score
    connectivityScore = 1;
    ND = NC/sel

    # Add up counters based on nodal connectivities
    N,_ = np.histogram(CA, NC.shape[0]);
    
    CA_col1 = [x[0] for x in CA]
    CA_col2 = [x[1] for x in CA]
    
    ## NEW
    for i in range(NC.shape[0]):
        # Isolate members starting/ending at current node
        indiOne = [m for m in range(len(CA_col1)) if CA_col1[m] == i+1]
        indiTwo = [m for m in range(len(CA_col2)) if CA_col2[m] == i+1]
        mCAone = CA[indiOne]
        mCAtwo = CA[indiTwo]
        
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
        
        corner_node = False
        
        # Consider elements present due to repeatability (corner nodes)
        if ((ND[i,0] == 0) and (ND[i,1] == 0)): # node in bottom left corner
            corner_node = True
            # Identify opposite node
            opp_node = i+(sidenum**2)
            
            # Identify adjacent nodes
            adjnode_b = i+sidenum
            adjnode_a = i+(sidenum*(sidenum-1))+1
            
        elif ((ND[i,0] == 0) and (ND[i,1] == 1)): # node in top left corner
            corner_node = True
            # Identify opposite node
            opp_node = i+((sidenum-1)**2)+1
            
            # Identify adjacent nodes
            adjnode_b = i-(sidenum-1)+1
            adjnode_a = i+(sidenum*(sidenum-1))+1
            
        elif ((ND[i,0] == 1) and (ND[i,1] == 0)): # node in bottom right corner
            corner_node = True
            # Identify opposite node
            opp_node = i-((sidenum-1)**2)+1
            
            # Identify adjacent nodes
            adjnode_b = i+sidenum
            adjnode_a = i-(sidenum*(sidenum-1))+1
            
        elif ((ND[i,0] == 1) and (ND[i,1] == 1)): # node in top right corner
            corner_node = True
            # Identify opposite node
            opp_node = i-((sidenum**2)-1)+1
            
            # Identify adjacent nodes
            adjnode_b = i-(sidenum-1)+1
            adjnode_a = i-(sidenum*(sidenum-1))+1
            
        if corner_node:
            # Find elements connecting to/from opp_node
            indiOne_opp = [m for m in range(len(CA_col1)) if CA_col1[m] == opp_node]
            indiTwo_opp = [m for m in range(len(CA_col2)) if CA_col2[m] == opp_node]
            onCAone = CA[indiOne_opp]
            onCAtwo = CA[indiTwo_opp]
        
            onCAone_set = set([tuple(x) for x in onCAone])
            onCAtwo_set = set([tuple(x) for x in onCAtwo])
        
            diff_elems_onCAone = np.asarray(list(onCAone_set - onCAtwo_set))
            diff_elems_onCAtwo = np.asarray(list(onCAtwo_set - onCAone_set))
        
            if ((diff_elems_onCAtwo.shape[0] == 0) and (diff_elems_onCAone.shape[0] != 0)):
                onCA = diff_elems_onCAone
            elif ((diff_elems_onCAone.shape[0] == 0) and (diff_elems_onCAtwo.shape[0] != 0)):
                onCA = diff_elems_onCAtwo
            else:
                onCA = np.vstack((diff_elems_onCAone,diff_elems_onCAtwo))
    
            # Find elements connecting to/from adjacent nodes
            indOne_b = [m for m in range(len(CA_col1)) if CA_col1[m] == adjnode_b]
            indTwo_b = [m for m in range(len(CA_col2)) if CA_col2[m] == adjnode_b]
            onCAone_b = CA[indOne_b]
            onCAtwo_b = CA[indTwo_b]
            
            onCAone_set_b = set([tuple(x) for x in onCAone_b])
            onCAtwo_set_b = set([tuple(x) for x in onCAtwo_b])
        
            diff_elems_onCAone_b = np.asarray(list(onCAone_set_b - onCAtwo_set_b))
            diff_elems_onCAtwo_b = np.asarray(list(onCAtwo_set_b - onCAone_set_b))
        
            if ((diff_elems_onCAtwo_b.shape[0] == 0) and (diff_elems_onCAone_b.shape[0] != 0)):
                onCA_b = diff_elems_onCAone_b
            elif ((diff_elems_onCAone_b.shape[0] == 0) and (diff_elems_onCAtwo_b.shape[0] != 0)):
                onCA_b = diff_elems_onCAtwo_b
            else:
                onCA_b = np.vstack((diff_elems_onCAone_b,diff_elems_onCAtwo_b))
        
            indOne_a = [m for m in range(len(CA_col1)) if CA_col1[m] == adjnode_a]
            indTwo_a = [m for m in range(len(CA_col2)) if CA_col2[m] == adjnode_a]
            onCAone_a = CA[indOne_a]
            onCAtwo_a = CA[indTwo_a]
            
            onCAone_set_a = set([tuple(x) for x in onCAone_a])
            onCAtwo_set_a = set([tuple(x) for x in onCAtwo_a])
        
            diff_elems_onCAone_a = np.asarray(list(onCAone_set_a - onCAtwo_set_a))
            diff_elems_onCAtwo_a = np.asarray(list(onCAtwo_set_a - onCAone_set_a))
        
            if ((diff_elems_onCAtwo_a.shape[0] == 0) and (diff_elems_onCAone_a.shape[0] != 0)):
                onCA_a = diff_elems_onCAone_a
            elif ((diff_elems_onCAone_a.shape[0] == 0) and (diff_elems_onCAtwo_a.shape[0] != 0)):
                onCA_a = diff_elems_onCAtwo_a
            else:
                onCA_a = np.vstack((diff_elems_onCAone_a,diff_elems_onCAtwo_a))
        
            # Based on location of node i relative to adjacent nodes, add additional connections
            for q in range(onCA_b.shape[0]):
                if ((ND[onCA_b[q,0]-1,0] != ND[onCA_b[q,1]-1,0]) and (ND[onCA_b[q,0]-1,1] != ND[onCA_b[q,1]-1,1])):
                    mCA = np.vstack((mCA,onCA_b[q,:]))
                    N[i] = N[i] + 1
                if ((ND[onCA_a[q,0]-1,0] != ND[onCA_a[q,1]-1,0]) and (ND[onCA_a[q,0]-1,1] != ND[onCA_a[q,1]-1,1])):
                    mCA = np.vstack((mCA,onCA_a[q,:]))
                    N[i] = N[i] + 1
                
            # Add connections from opposite node to mCA
            mCA = np.vstack((mCA,onCA))
            N[i] = N[i] + onCA.shape[0]
            
        # Consider elements present due to repeatability (edge nodes)
        edge_node = False
        if ((ND[i,0] == 0) and (not corner_node)): # edge node is on left side
            edge_node = True
            # Identify opposite node
            opp_node = i+(sidenum*(sidenum-1))+1
            
        elif ((ND[i,0] == 1) and (not corner_node)): # edge node is on right side
            edge_node = True
            # Identify opposite node
            opp_node = i-(sidenum*(sidenum-1))+1
            
        elif ((ND[i,1] == 0) and (not corner_node)): # edge node is on bottom side
            edge_node = True
            # Identify opposite node
            opp_node = i+sidenum
            
        elif ((ND[i,1] == 1) and (not corner_node)): # edge node is on top side
            edge_node = True
            # Identify opposite node
            opp_node = i-(sidenum-1)+1
        
        if edge_node:
            # Find elements connecting to/from opp_node
            indiOne_opp = [m for m in range(len(CA_col1)) if CA_col1[m] == opp_node]
            indiTwo_opp = [m for m in range(len(CA_col2)) if CA_col2[m] == opp_node]
            onCAone = CA[indiOne_opp]
            onCAtwo = CA[indiTwo_opp]
        
            onCAone_set = set([tuple(x) for x in onCAone])
            onCAtwo_set = set([tuple(x) for x in onCAtwo])
        
            diff_elems_onCAone = np.asarray(list(onCAone_set - onCAtwo_set))
            diff_elems_onCAtwo = np.asarray(list(onCAtwo_set - onCAone_set))
        
            if ((diff_elems_onCAtwo.shape[0] == 0) and (diff_elems_onCAone.shape[0] != 0)):
                onCA = diff_elems_onCAone
            elif ((diff_elems_onCAone.shape[0] == 0) and (diff_elems_onCAtwo.shape[0] != 0)):
                onCA = diff_elems_onCAtwo
            else:
                onCA = np.vstack((diff_elems_onCAone,diff_elems_onCAtwo))
            
            # Based on location of node i/opp_node, add additional elements
            for q in range(onCA.shape[0]):
                if (ND[onCA[q,0]-1,1] != ND[onCA[q,1]-1,1]):
                    mCA = np.vstack((mCA,onCA[q,:]))
                    N[i] = N[i] + 1
            
        # Determine whether node has sufficient connectivity components 
        if (N[i] < 2):
            # node is an unstable connection point
            connectivityScore = connectivityScore - 0.1
            if connectivityScore < 0.1:
                return connectivityScore
    
    return np.around(connectivityScore,2)

#### TESTING FUNCTIONS ON RANDOM DESIGN 

sel = 10e-3
sidenum = 3
CA = np.array([[1,2],[2,3],[1,4],[1,5],[2,5],[3,5],[3,6],[4,5],[5,6],[4,7],[5,7],[5,8],[5,9],[6,9],[7,8],[8,9]])
CA = CA[np.argsort(CA[:,0])]
NC = generateNC(sel, sidenum)

feas = feasibility(NC,CA,sidenum) # expected value is 1
conn = connectivity_PBC(sidenum,CA,NC,sel) # expected value is 1