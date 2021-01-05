import numpy as np
from scipy.spatial import Delaunay

''' This script calculates the embedded Voronoi diagram to then use for the shortest path algorithm to compute the centerline. '''
def calculateVoronoi(verticesPoints, normalsPoints):
    tri = Delaunay(verticesPoints)
    internalVoronoiVertices = []
    radii = []
    oldToNew = [] # convert old indices -> new indices to find connection for Voronoi diagram
    indices = [] # indices of tetras we keep 
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
                oldToNew.append([indx, len(radii)-1])
                indices.append(indx)

    all_connected = False
    key = np.array(oldToNew)
    while all_connected == False:
        oldToConnected = []
        allNeighbors = []
        indices_new = []
        ''' Check if connectivity is complete:
        '''
        connected_indices=[]
        internalVoronoiVerticesConnected=[]
        radiiConnected=[]
        for indx in indices: 
            neighborsOld = tri.neighbors[indx]
            neighborsNew=[]
            for i in range(0, 4):
                j = np.where(key[...,0]==neighborsOld[i])
                neighborsNew.append(key[j,1])
            sizeAdd=0
            for a in range(0, len(neighborsNew)):
                sizeAdd = sizeAdd + neighborsNew[a].size
            if sizeAdd != 0: # as long as it has at least one neighbor
                connected_indices.append(indx)
                j = np.where(key[...,0]==indx)
                internalVoronoiVerticesConnected.append(internalVoronoiVertices[key[j[0][0],1]])
                radiiConnected.append(radii[key[j[0][0],1]])
                oldToConnected.append([indx, len(radiiConnected)-1])

        key = np.array(oldToConnected)
        ''' Getting the right list of neighbors. '''
        for indx in connected_indices:
            neighborsNew=[]
            neighborsOld = tri.neighbors[indx]
            for i in range(0, 4):
                j = np.where(key[...,0]==neighborsOld[i])
                if key[j,1].size != 0:
                    neighborsNew.append(key[j,1][0][0])
            allNeighbors.append(neighborsNew)
        
        for i in range(0, len(allNeighbors)):
            if len(allNeighbors[i]) == 0:
                all_connected = False
                indices = connected_indices
                print(len(allNeighbors))
                break
            else:
                all_connected = True

    return internalVoronoiVerticesConnected, radiiConnected, allNeighbors
