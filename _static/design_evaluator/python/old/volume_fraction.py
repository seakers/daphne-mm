import numpy as np

# FUNCTION TO CALCULATE VOLUME FRACTION 
def calcVF(NC,CA,rvar,sel,sidenum):
    totalTrussVol = 0;
    for i in range(CA.shape[0]):
        # Finding element length from nodal coordinates
        x1 = NC[CA[i,0],0]; x2 = NC[CA[i,1],0];
        y1 = NC[CA[i,0],1]; y2 = NC[CA[i,1],1];
        L = np.sqrt(((x2-x1)**2)+((y2-y1)**2));
        # Adding current element to total volume of trusses
        totalTrussVol = totalTrussVol + L*(np.pi*rvar[i]**2);
    
    
    # Finding average side "thickness" due to differing element radii
    # horizrads = [];
    # for i in range(CA.shape[0]):
    #     if ((CA[i,0] + sidenum) == CA[i,1]) and (NC[CA[i,0],1] == sel):
    #         horizrads.append(rvar[i]);
        
    # vertrads = [];
    # for i in range(CA.shape[0]):
    #     if ((CA[i,0] + 1) == CA[i,1]) and (NC[CA[i,0],0] == sel):
    #         vertrads.append(rvar[i]);

    # thick = np.mean([np.mean(horizrads), np.mean(vertrads)]);
    try:
        thick = np.max(rvar)
    except ValueError:
        thick = 5e-04
    
    # Calculating volume fraction (using a solid square with 2*(avg 
    #   thickness) as a baseline)
    volFrac = totalTrussVol/(2*thick*(sel**2)); 

    if volFrac>1:
        volFrac=1

    return volFrac