import BPSpatial.Constants as C
import HOV_Incidents_new.Constants as IC
import sys
sys.path.append(C.BPSPATIAL)

import FileIO.SHP as SIO
import FileIO.Graph as GIO
#import FileIO.Excel as EIO
import Analysis.Graph as AG

import networkx as nx
import copy
import numpy as np
import os

# =============================================================================
# Parameters
# =============================================================================
splitJoincountPath = '{}CA_HOV_split_500m_line_sj_all.shp'.format(IC.HIGHWAYS_R)
lxcenterGraphPath = '{}CA_HOV_split_500m_lxcenter.shp'.format(IC.HIGHWAYS_R) # output of ArcMap
# copy projection from
projFromPath = splitJoincountPath
# set bandwidth
bandwidth = 1000


lxcenterGraph_exists = os.path.isfile(lxcenterGraphPath)
if lxcenterGraph_exists == False:
    print('lxcenter graph does not exist')
    
    # =============================================================================
    # ArcMap works
    #
    # 1. Add Center Coordinates to CA_HOV_split_500m_line_sj_all.shp
    #   - using attribute table, add two columns for x, y and calcuate geometry
    #   - Export attribute table in csv file
    # 2. Add X,Y Data
    #   - X - center_x / Y - center_Y
    #   - Export to CA_HOV_split_500m_lxcenter_point.shp
    # 3. Split Line at Point
    #   - Input Feature - CA_HOV_Intersect.shp
    #   - Point Feature - CA_HOV_split_500m_lxcenter_point.shp
    #   - Search Radius - 0.01 m
    #   - Output Feature Class - CA_HOV_split_500m_lxcenter.shp
    # =============================================================================
else:
    print('lxcenter graph exists')
    # read a shapefile
    lxcenterGraph = GIO.Polyline.fromShapefile(lxcenterGraphPath)
    splitJoincount = GIO.Polyline.fromShapefile(splitJoincountPath, attrs=['joinCount', 'edgeInd'])
    # add center point
    AG.graphCalculate.addCenter(splitJoincount)
    

    # Get X, Y coordinates of lxcenterGraph's nodes    
    lxcenterList = []
    for lxc in lxcenterGraph.nodes(data=True):
        lxcenterList.append(list(lxc[0]))
    lxcenterArray = np.array(lxcenterList).transpose()
    
    # Find the spl's nearest node from lxcenterGraph
    # SplitJoincount -> lixelGraph
    lixelGraph = copy.deepcopy(splitJoincount)
    for spl in splitJoincount.edges(data=True):
        center_x = [spl[2]['center'][0]] * len(lxcenterGraph.nodes())
        center_y = [spl[2]['center'][1]] * len(lxcenterGraph.nodes())
        distanceArray = np.sqrt(np.sum((np.array([center_x, center_y])-lxcenterArray), axis=0)**2)
        minInd = np.argmin(distanceArray)
        if distanceArray[minInd] > 1:
            print(spl[2]['center'], lxcenterList[minInd], distanceArray[minInd])
        nx.set_edge_attributes(lixelGraph, 'center', {(spl[0], spl[1]):lxcenterList[minInd]})

    ## find the shortest path for all nodes
    failList = []
    centerList = [lix[2]['center'] for lix in lixelGraph.edges(data=True)]
    centerList[0]
    lxcenterList = [list(lxc) for lxc in lxcenterGraph.nodes()]
    centerList[0] in lxcenterList
    for center in centerList:
        if center in lxcenterList:
            pass
        else:
            failList.append(center)
    print(len(failList))
    
    pred, dist = nx.shortest_paths.weighted.dijkstra_predecessor_and_distance(lxcenterGraph, tuple(center), weight = 'distance')
    
    # KDE
    lixelKDE = AG.interpolate.graphKDE(lixelGraph, lxcenterGraph, bandwidth=bandwidth, kernel = 'gaussian', diverge=True)
    # {key:value} = {tuple(center):KDE}
    lixelKDE_dict = {val[0]:val[1] for val in lixelKDE}
    # {key:value} = {tuple(tuple(center), ind):KDE}
    attr_dict = {}
    for edge in lixelGraph.edges(data=True):
        center = tuple(edge[2]['center'])
        kde = lixelKDE_dict[center]
        attr_dict[(edge[0], edge[1])] = kde
    nx.set_edge_attributes(lixelGraph, 'KDE', attr_dict)
    
    outLixelGraphPath = '{}CA_HOV_split_500m_line_sj_KDE_{}.shp'.format(IC.HIGHWAYS_R, bandwidth)
    SIO.Polyline.fromGraph(lixelGraph, outLixelGraphPath)
    SIO.Projection.copyCRS(projFromPath, outLixelGraphPath)