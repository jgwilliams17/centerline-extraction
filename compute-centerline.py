''' This code computes the centerline of a vascular input provided in .obj format. '''

import argparse
import re
import csv
from readObj import readObj
from scipy.spatial import Voronoi, Delaunay
from calculateVoronoi import calculateVoronoi
import numpy as np 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d
from DijkstraVoronoi import DijkstraVoronoi
from numpy.random import rand

''' Parser arguments (choose data): '''
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--vasc", choices=['Bifurcation','Aneurysm','Bleeding'],default='Bifurcation')
args, _ = parser.parse_known_args()

''' Import object and get vertices and normals: '''
datapath = f"vasculature/{args.vasc}/Mesh.obj"
vertices, normals = readObj(datapath)
verticesPoints = np.reshape(vertices,(int(len(vertices)/3),3))
normalsPoints = np.reshape(normals,(int(len(normals)/3),3))

''' Get Delaunay triangulation and embedded Voronoi diagram: '''
tri = Delaunay(verticesPoints)
internalVoronoi, radii, allNeighbors = calculateVoronoi(verticesPoints, normalsPoints)
internalVoronoiPoints = np.reshape(np.array(internalVoronoi), (int(len(np.array(internalVoronoi))), 3))
radii = np.array(radii).flatten()
allNeighbors = np.array(allNeighbors, dtype=object)

''' Create graph object out of Voronoi points, radii (to use in the edge weighting function, and neighboring points: '''
G = [internalVoronoiPoints,radii,allNeighbors]

''' Display the embedded Voronoi points as a scatter plot, coloured by radii of maximum inscribed sphere: '''
fig = plt.figure()
ax = Axes3D(fig)
cm = plt.cm.get_cmap('RdYlBu')
annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)
sc = ax.scatter(internalVoronoiPoints[...,0], internalVoronoiPoints[...,1], internalVoronoiPoints[...,2], c= radii, s=20, vmin = min(radii), vmax = max(radii), cmap=cm, picker=1)

''' Pick points to use as starting and ending points to get centerline: '''
numOutPts = input("Number of outlet points: ")
points=[]
def onpick3(event):
    indx = event.ind[0]
    x, y, z = event.artist._offsets3d
    proj = ax.get_proj()
    proj = ax.get_proj()
    data = np.array(sc._offsets3d).T
    x_p, y_p, _ = proj3d.proj_transform(x[indx], y[indx], z[indx], proj)
    plt.annotate(str(indx), xy=(x_p, y_p))
    fig.canvas.draw_idle()
    points.append(indx)
    if len(points) == 1 + int(numOutPts):
        plt.close()

def update_annot(ind):
    pos = sc.get_offsets()[ind["ind"][0]]
    annot.xy = pos
    text = str(ind["ind"][0])
    annot.set_text(text)

def hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

ax.set_xlim3d(verticesPoints[...,0].min(), verticesPoints[...,0].max())
ax.set_ylim3d(verticesPoints[...,1].min(), verticesPoints[...,1].max())
ax.set_zlim3d(verticesPoints[...,2].min(), verticesPoints[...,2].max())
fig.canvas.mpl_connect('pick_event', onpick3)
fig.canvas.mpl_connect("motion_notify_event", hover)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ax.set_title('Select inlet point then each outlet point in turn')
plt.show()

outPts=[]
inPt = points[0]
for i in range(1,len(points)):
    outPts.append(points[i])

'''Run Dijkstra's shortest path algorithm to get path between inlet point and each of the outlet points. Save points where there is a bifurcation - detected as where the path splits - so that we don't get repeat indices in the path and can plot each branch separately: '''
dijkstra = DijkstraVoronoi(G,str(inPt))

fig = plt.figure()
ax = Axes3D(fig)

colors=['k','green','red','blue']
csv_file = open(f"vasculature/{args.vasc}/path_{args.vasc}.csv","w+")
writer = csv.writer(csv_file, delimiter=',')
path_initial = dijkstra.get_path(str(outPts[0]))
total_path = path_initial
indxSplit = []
for i in range(1, int(numOutPts)):
    path = dijkstra.get_path(str(outPts[i]))
    lgth = min(len(path), len(path_initial))
    indxFirstDiff = [x for x in range(lgth) if path_initial[x] != path[x]][0]
    indxSplit.append(len(total_path))
    total_path = total_path + path[indxFirstDiff:len(path)]

indxSplit.append(len(total_path))

''' Plot each branch of the path: '''
for j in range(0, indxSplit[0]-1):
    ax.plot([internalVoronoiPoints[int(total_path[j]),0], internalVoronoiPoints[int(total_path[j+1]),0]], [internalVoronoiPoints[int(total_path[j]),1], internalVoronoiPoints[int(total_path[j+1]),1]], [internalVoronoiPoints[int(total_path[j]),2], internalVoronoiPoints[int(total_path[j+1]),2]], color=colors[0])
    
for i in range(0, len(indxSplit)-1):
    for j in range(indxSplit[i], indxSplit[i+1]-1):
        ax.plot([internalVoronoiPoints[int(total_path[j]),0], internalVoronoiPoints[int(total_path[j+1]),0]], [internalVoronoiPoints[int(total_path[j]),1], internalVoronoiPoints[int(total_path[j+1]),1]], [internalVoronoiPoints[int(total_path[j]),2], internalVoronoiPoints[int(total_path[j+1]),2]], color=colors[i+1])

''' Save path to .csv file (in vasculature/Bifurcation/path.csv) for example: '''
for j in range(0, len(total_path)):
    line = "%s, %s, %s\n" % (internalVoronoiPoints[int(total_path[j]),0], internalVoronoiPoints[int(total_path[j]),1], internalVoronoiPoints[int(total_path[j]),2])
    csv_file.write(line)

csv_file.close()
ax.set_xlim3d(verticesPoints[...,1].min(), verticesPoints[...,1].max())
ax.set_ylim3d(verticesPoints[...,1].min(), verticesPoints[...,1].max())
ax.set_zlim3d(verticesPoints[...,1].min(), verticesPoints[...,1].max())
plt.show()
