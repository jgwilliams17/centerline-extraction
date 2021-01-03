import numpy as np
from scipy.spatial import Delaunay

def contains_duplicates(X):
        return len(np.unique(X)) != len(X)

def calculateVoronoi(verticesPoints, normalsPoints):
    tri = Delaunay(verticesPoints)
    internalVoronoiVertices = []
    radii = []
    for indx in  range(0, len(tri.simplices)):
        tetra = tri.simplices[indx]
        tetraPoints = verticesPoints[tetra]
        tetraNormals = normalsPoints[tetra]
        ''' 
        Calculate circumcenter of tetrahedron.
        '''
        A = np.matrix([tetraPoints[1]-tetraPoints[0],tetraPoints[2]-tetraPoints[0],tetraPoints[3]-tetraPoints[0]])
        B = (1/2) * np.matrix(([tetraPoints[1].dot(tetraPoints[1])-tetraPoints[0].dot(tetraPoints[0]),tetraPoints[2].dot(tetraPoints[2])-tetraPoints[0].dot(tetraPoints[0]),tetraPoints[3].dot(tetraPoints[3])-tetraPoints[0].dot(tetraPoints[0])]))
        C = A.I.dot(B.T)
        ''''''
        ''' 
        Checks whether connectivity of Voronoi cell is complete - i.e., is it out of range (how many neighbors does Delaunay tehtrahedron have?):
        '''
        if len(np.unique(tri.neighbors[indx])) == len(tri.neighbors[indx]) and all(tri.neighbors[indx] != -1):
            ''' Is circumcenter outside domain? '''
            all_dis=[]
            for i in range(0, 4):
                dis = (tetraPoints[i]-np.array(C.T)).dot(tetraNormals[i])
                all_dis.append(dis)
            if all(np.array(all_dis) > 0):
                internalVoronoiVertices.append(C)
                r = np.sqrt((tetraPoints[0][0]-C[0])**2 + (tetraPoints[0][1]-C[1])**2 + (tetraPoints[0][2]-C[2])**2)
                radii.append(r)
    return internalVoronoiVertices, radii


