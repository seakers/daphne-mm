import numpy as np
import networkx as nx

__all__ = ['findLineSegIntersection', 'findOrientation', 'feasibility', 'stability', 'orientation', 'triangles',  'density', 'threeStars', 'createGraph']

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

def findSlope(x1, y1, x2, y2):
	den = x2-x1
	num = y2-y1
	m = num/den if den!=0 else 1000;
	return m

def findAngles(NC, CA):
# This function computes the orientation angle wrt x-axis for elements in CA
# Inputs: nodal position matrix NC 
#         Design Connectivity Array CA_des   
	x1 = NC[CA[:,0],0]
	y1 = NC[CA[:,0],1]
	x2 = NC[CA[:,1],0]
	y2= NC[CA[:,1],1]

	L = np.sqrt((x2-x1)**2+(y2-y1)**2);
	angles = np.arccos((x2-x1)/L);

	return angles

def createGraph(NC, CA):
	G = nx.Graph()
	G.add_nodes_from(range(9))
	G.add_edges_from(CA)
	return G

def triangles(NC, CA):
# This function returns the number of triangles in the design
	G = createGraph(NC, CA)
	return sum(nx.triangles(G).values())/3

def density(NC, CA):
	G = createGraph(NC, CA)
	return nx.density(G)

def threeStars(NC, CA):
	G = createGraph(NC, CA)
	stars = np.array(list(dict(nx.degree(G)).values()))
	return sum(stars==3)

def orientation(NC, CA, target=[0, 20]):
# This function returns the number of elements with orientation between the given range
# Inputs: nodal position matrix NC 
#         Design Connectivity Array CA_des
#		  End angles in degrees range = [deg deg]; Angles should be between [0, 180] degrees
	c= np.pi/180
	angles = findAngles(NC, CA)
	return sum((angles>=c*target[0]) & (angles<=c*target[1]))

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

def feasibility(NC,CA_des):
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
	PosA = np.vstack([ NC[SortedCA[:,0],0], NC[SortedCA[:,0],1], NC[SortedCA[:,1],0], NC[SortedCA[:,1],1] ]).T;

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
				D = ['The element from ('+str(PosA[i,0])+','+
					 str(PosA[i,1])+') to ('+str(PosA[i,2])+
					 ','+str(PosA[i,3])+') intersects with the' +
					 ' element from (',str(PosA[j,0])+',' +
					 str(PosA[j,1])+') to (',str(PosA[j,2])+','+
					 str(PosA[j,3])+')'];
				# print(D);
				#}
				
		# This constraint is not included in this version because the definition of edges does not allow overallping.
	# SECOND CONSTRAINT: Elements (of either the same or different lengths) 
	#   cannot overlap
	# Loop through each element
	# for k in range(SortedCA.shape[0]):
	# 	# Loop through each element again, to consider each possible pair 
	# 	#   of elements
	# 	mk = findSlope(NC[SortedCA[k,0],0], NC[SortedCA[k,0],1], NC[SortedCA[k,1],0], NC[SortedCA[k,1],1]);

	# 	for q in range(SortedCA.shape[0]):
	# 		# If the same element is being compared twice, move on
	# 		if k == q:
	# 			continue

	# 		# Check if both elements share a common startpoint
	# 		if (NC[SortedCA[k,0],0] == NC[SortedCA[q,0],0]) and (NC[SortedCA[k,0],1] == NC[SortedCA[q,0],1]):
	# 			# Check if both elements have the same slope (and reject 
	# 			#    the design if so)
	# 			mq = findSlope(NC[SortedCA[q,0],0], NC[SortedCA[q,0],1], NC[SortedCA[q,1],0], NC[SortedCA[q,1],1]);
				
	# 			if mk == mq:
	# 			   feasibilityScore = feasibilityScore - 0.1;
	# 			   if feasibilityScore < 0.1:
	# 				   return feasibilityScore
				   
	# 			   #{
	# 			   D = ['The element from ('+str(PosA[k,0])+','+
	# 				 str(PosA[k,1])+') to ('+str(PosA[k,2])+
	# 				 ','+str(PosA[k,3])+') overlaps with the'+
	# 				 ' element from ('+str(PosA[q,0])+','+
	# 				 str(PosA[q,1])+') to ('+str(PosA[q,2])+','+
	# 				 str(PosA[q,3])+')'];
				   # print(D);
				   #}

	# THIRD CONSTRAINT: Metamaterial should be connected.
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

	return np.around(feasibilityScore,2)

# FUNCTION TO TEST 2D TRUSS STABILITY 
def stability(sidenum,CA,NC):
	# Initialize stability score
	stabilityScore = 1;

	# Add up counters based on nodal connectivities
	N,_ = np.histogram(CA, NC.shape[0]);
	
	# First stability check: number of "holes" (unconnected nodes) in truss
	#   should be less than or equal to [(number of side nodes) - 2]
	zeros = np.argwhere(N==0);
	if np.sum(zeros) > (sidenum-2):
		stabilityScore = stabilityScore - 0.1;
		if stabilityScore < 0.1:
			return stabilityScore
	
	# Second stability check: nodes with connections are connected to at
	#   least three other nodes apiece (except for the corner nodes)
	idx = np.r_[1:(sidenum-2), sidenum:(sidenum**2-sidenum-1), (sidenum**2-(sidenum-2)-1):(sidenum**2-2)]
	Ns = N[idx];
	Nnz = Ns[Ns>0];
	for a in range(len(Nnz)):
	   if (Nnz[a] == 1) or (Nnz[a] == 2):
		   stabilityScore = stabilityScore - 0.1;
		   if stabilityScore < 0.1:
			   return stabilityScore
	
	# Third stability check: corner nodes have at least two connections
	Nc = N[[0, sidenum-1, sidenum^2-sidenum-1, sidenum^2-1]];
	for a in range(len(Nc)):
	   if Nc[a] == 1:
		   stabilityScore = stabilityScore - 0.2;
		   if stabilityScore < 0.1:
			   return stabilityScore;
	
	# Fourth stability check: at least one diagonal member present
	nodiags = True;
	for i in range(CA.shape[0]):
		if CA[i,0]+sidenum == CA[i,1]:
			nodiags = True;
		elif CA[i,0]-sidenum == CA[i,1]:
			nodiags = True;
		elif CA[i,0]+1 == CA[i,1]:
			nodiags = True;
		elif CA[i,0]-1 == CA[i,1]:
			nodiags = True;
		else:
			nodiags = False;
			break
		
	if nodiags == True:
		stabilityScore = stabilityScore - 0.2;
		if stabilityScore < 0.1:
			return stabilityScore
	
	# Assign value to stability boolean
	#stabilityBool = true;
	#if stabilityScore < 1
		#stabilityBool = false;
	#end
	return np.around(stabilityScore,2)