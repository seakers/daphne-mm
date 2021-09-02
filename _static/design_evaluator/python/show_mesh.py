import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections

__all__ = ['show_meshplot', 'repeatable_des']

def repeatable_des(_X):
    x = _X
    
    x[-2]=x[0]=max(x[-2],x[0]) #7-8=1-2
    x[-1]=x[5]=max(x[-1],x[5]) #8-9=2-3
    x[11]=x[3]=max(x[11],x[3]) #3-6=1-4
    x[18]=x[23]=max(x[18],x[23])#6-9=4-7

    return x

def show_meshplot(nodes, elements, x, r, ifMatrix=False, ax=None, plotNodes=False):
    if not ax: ax=plt.gca()
        
    y = nodes[:,0]
    z = nodes[:,1]
    
    if ifMatrix:
        idx = np.array(np.nonzero(np.triu(x))).T
        widths = (elements[:,None]==idx).all(-1).any(-1).astype(int)
    else:
        widths= r

    #https://stackoverflow.com/questions/49640311/matplotlib-unstructered-quadrilaterals-instead-of-triangles
    def quatplot(y,z, quatrangles, ax=None, **kwargs):

        if not ax: ax=plt.gca()
        yz = np.c_[y,z]
        verts= yz[quatrangles]
        pc = matplotlib.collections.PolyCollection(verts, **kwargs)
        ax.add_collection(pc)
        ax.autoscale()

#     plt.figure()
    ax.set_aspect('equal')

    quatplot(y,z, np.asarray(elements), ax=ax, linewidths=widths, color="black", facecolor="None")
    if plotNodes:            
        ax.plot(y,z, marker="o", ls="", color="black")
        
    ax.axis('off')