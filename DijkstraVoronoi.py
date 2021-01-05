from dijkstra import DijkstraSPF
import numpy as np
''' This code creates a graph object containing the list of Voronoi vertices, radii of largest inscribed spheres, and connected points. '''

class DijkstraVoronoi(DijkstraSPF):

    @staticmethod
    def get_adjacent_nodes(G, u):
        neighbors = G[2][int(u)]
        neighborsStr = []
        for i in range(0, len(neighbors)):
            neighborsStr.append(str(neighbors[i]))
        return neighborsStr

    @staticmethod
    def get_edge_weight(G, u, v):
        alpha = 1; beta = 50 # weighting to control how import it is to stay in the center of the vessel vs. shortest path (alpha - centering, beta - shortest path)
        dis = np.sqrt((G[0][int(u)][0]-G[0][int(v)][0])**2 + (G[0][int(u)][1]-G[0][int(v)][1])**2 + (G[0][int(u)][2]-G[0][int(v)][2])**2)
        weight = alpha * (1/G[1][int(u)] + 1/G[1][int(v)])/2 + beta * dis # graph edge weighting penalises both moving away from the center of the vessel (small maximum inscribed sphere radius) and distance between nodes 
        return weight
