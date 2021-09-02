import numpy as np

__all__=['generateNC', 'fiberCalc', 'formK', 'generateC']

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
        x1 = NC[CA[i,0],0]; x2 = NC[CA[i,1],0];
        y1 = NC[CA[i,0],1]; y2 = NC[CA[i,1],1];
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
		x1 = NC[CA[i,0],0]; x2 = NC[CA[i,1],0];
		y1 = NC[CA[i,0],1]; y2 = NC[CA[i,1],1];
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
			GlobToLoc[:,n*2+d]=GN*2+d;

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
						rvec.append(2*x-1);
					elif ND[x,0] == 1:
						# displacement in x is proportional to y-coordinate
						# (due to nature of shear)
						u_r.append([e12*sel*ND[x,1]]);
						rvec.append(2*x-1);
						Fi_x.append(2*x-1);
					elif ND[x,1] == 1:
						# displacement in x = e12*sel
						u_r.append([e12*sel]);
						rvec.append(2*x-1);
					elif ND[x,1] == 0:
						# displacement in x = 0
						u_r.append([0]);
						rvec.append(2*x-1);
					else:
						# x-direction DOF is a force BC
						F_q.append([0]);
						qvec.append(2*x-1);
					
					# Finding y-DOF
					if ND[x,1] == 0:
						# displacement in y = 0
						u_r.append([0]);
						rvec.append(2*x);
					elif ND[x,1] == 1:
						# displacement in y = 0
						u_r.append([0]);
						rvec.append(2*x);
						Fi_y.append(2*x);
						Fi_xy.append(2*x-1);
					else:
						# y-direction DOF is a force BC
						F_q.append([0]);
						qvec.append(2*x);
					
				else: # Blanket condition for all interior nodes
					# both x- and y-DOFs are force BCs
					F_q.extend([[0], [0]]);
					qvec.extend([2*x-1, 2*x]);

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
		C.append(Cdummy[:,y])
		FBasket.append([F]);
		uBasket.append([u]);

	C = np.array(C).T[0]
	FBasket = np.array(FBasket).T
	uBasket = np.array(uBasket).T

	return C,uBasket,FBasket

