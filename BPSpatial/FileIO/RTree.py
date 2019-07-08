"""
@author: bspark
"""
import numpy as np
from rtree import index

def pointRect(coord):
        return (coord[0]-1, coord[1]-1, coord[0]+1, coord[1]+1)

def lineRect(lineGraph, node1, node2):
    left = min(np.array(lineGraph.edge[node1][node2]['coordinates'])[:,0])
    bottom = min(np.array(lineGraph.edge[node1][node2]['coordinates'])[:,1])
    right = max(np.array(lineGraph.edge[node1][node2]['coordinates'])[:,0])
    up = max(np.array(lineGraph.edge[node1][node2]['coordinates'])[:,1])
    return (left, bottom, right, up)
    

def rtree_polyline(polylineGraph):
    idxLine = index.Index()
    edgeIdCoordDict = {}
    for edge in polylineGraph.edges(data=True):
#            left = min(np.array(edge[2]['coordinates'])[:,0])
#            bottom = min(np.array(edge[2]['coordinates'])[:,1])
#            right = max(np.array(edge[2]['coordinates'])[:,0])
#            up = max(np.array(edge[2]['coordinates'])[:,1])
#            idxLine.insert(int(edge[2]['Ind']), (left, bottom, right, up))
        
        lineRectVal = lineRect(polylineGraph, edge[0], edge[1])
        idxLine.insert(int(edge[2]['Ind']), lineRectVal)
        
        edgeIdCoordDict[edge[2]['Ind']] = (edge[0], edge[1])
        
    return idxLine, edgeIdCoordDict
