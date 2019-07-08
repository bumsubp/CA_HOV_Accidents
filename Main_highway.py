import BPSpatial.Constants as BPS
import HOV_Incidents_new.Constants as C
import sys
sys.path.append(BPS.HOME)
sys.path.append(BPS.BPSPATIAL)

import FileIO.Graph as GIO
import FileIO.SHP as SIO

import copy
import pickle

crs = SIO.Projection.getPROJ4(C.CRS_PRJ[0], C.CRS_PRJ[1])

shpHOVPath = '{}CA_HOV_Access_dissolve.shp'.format(C.HIGHWAYS_R)
HOVGraph = GIO.Polyline.fromShapefile(shpHOVPath, 'HwyId Route Direction'.split(sep=' '))

shpSplitPath = '{}CA_HOV_dissolve_split_500m_line.shp'.format(C.HIGHWAYS_R)
splitGraph = GIO.Polyline.fromShapefile(shpSplitPath, 'HwyId Route Direction'.split(sep=' '))

shpStationPath = '{}HOV_Stations_selected_near.shp'.format(C.STATIONS_R)
stationGraph = GIO.Point.fromShapefile(shpStationPath, 'ID Route Direction'.split(sep=' '))


## Get information of hwy route ends coordinates
hwyEndNodesDict ={}
# =============================================================================
# hwyEndNodesDict    dictionary of coordinates of end nodes of route 
#                    {(route, direction, HwyId): ((x,y), (x,y))}
# =============================================================================

for line in HOVGraph.edges(data=True):
    route = line[2]['Route']
    direction = line[2]['Direction']
    hwyId = line[2]['HwyId']
    
    node1_x = line[0][0]
    node1_y = line[0][1]
    node2_x = line[1][0]
    node2_y = line[1][1]
    
    xyDict = {node1_x : node1_y, node2_x : node2_y}
    yxDict = {node1_y : node1_x, node2_y : node2_x}
    
    if direction != None:
        if direction == 'NB':
            y1 = min(node1_y, node2_y)
            x1 = yxDict[y1]
            y2 = max(node1_y, node2_y)
            x2 = yxDict[y2]
        elif direction == 'SB':
            y1 = max(node1_y, node2_y)
            x1 = yxDict[y1]
            y2 = min(node1_y, node2_y)
            x2 = yxDict[y2]
        elif direction == 'EB':
            x1 = min(node1_x, node2_x)
            y1 = xyDict[x1]
            x2 = max(node1_x, node2_x)
            y2 = xyDict[x2]
        elif direction == 'WB':
            x1 = max(node1_x, node2_x)
            y1 = xyDict[x1]
            x2 = min(node1_x, node2_x)
            y2 = xyDict[x2]
        
        hwyEndNodesDict[(route, direction, hwyId)] = ((x1, y1), (x2, y2))


### Matching end nodes of split segments and station Id
        
splitGraphCopy = splitGraph.copy()
roundNum = 3
stationCoords = {(round(station[0][0],roundNum), round(station[0][1],roundNum)):station[1]['ID'] for station in stationGraph.nodes(data=True)}
for splitLine in splitGraphCopy.edges(data=True):
    node1_coord = (round(splitLine[0][0], roundNum), round(splitLine[0][1],roundNum))
    if node1_coord in stationCoords.keys():
        splitLine[2]['station1_ID'] = stationCoords[node1_coord]
    else:
        splitLine[2]['station1_ID'] = -1
    node2_coord = (round(splitLine[1][0], roundNum), round(splitLine[1][1],roundNum))
    if node2_coord in stationCoords.keys():
        splitLine[2]['station2_ID'] = stationCoords[node2_coord]
    else:
        splitLine[2]['station2_ID'] = -1

#count = 0
#for splitLine in splitGraphCopy.edges(data=True):
#    if splitLine[2]['station1_ID'] != -1:
#        count+=1
#    if splitLine[2]['station2_ID'] != -1:
#        count+=1
        
# =============================================================================
# splitGraphCopy    networkx polyline graph without HOV connectors
# =============================================================================
for splitLine in splitGraphCopy.edges(data=True):
    direction = splitLine[2]['Direction']
    if direction == None:
        splitGraphCopy.remove_edge(splitLine[0], splitLine[1])
    
attrNames = 'Ind Direction Route distance station1_ID station2_ID'.split(sep=' ')
hwySplitDict = {key:[] for key in hwyEndNodesDict.keys()}
# =============================================================================
# hwySplitDict    nestedDictionary 
#                {(Route, Direction, HwyId): [(edge[0], edge[1], edge[2])]}
# =============================================================================
for splitLine in splitGraphCopy.edges(data=True):
    attrsDict = {key:splitLine[2][key] for key in attrNames}
    attrsTuple = tuple([splitLine[0], splitLine[1], attrsDict])
    hwySplitDict[(splitLine[2]['Route'], splitLine[2]['Direction'], splitLine[2]['HwyId'])].append(attrsTuple)
    
    
# =============================================================================
# hwySplitOrderedDict nestedDictionary with orders
#                    {(Route, Direction, HwyId): [(edge[0], edge[1], edge[2])]}
# =============================================================================
    
hwySplitOrderedDict = {key:[] for key in hwyEndNodesDict.keys()}
printInd = 0
for key, valList in hwySplitDict.items(): # (Route, Direction, hwyId): [(edge[0], edge[1], edge[2])]
    printInd+=1
    print(key)
    print('{} / {}'.format(printInd, len(hwySplitDict.keys())))
    (startNode, endNode) = hwyEndNodesDict[key]  #(route, direction, hwyId) = ((x1, y1), (x2, y2))
    tempStartNode = startNode # (x1, y1)
    tempEndNode = startNode
    
    valListCopy = copy.deepcopy(valList) # [(edge[0], edge[1], edge[2])]
    
    # find out the index of the first node of hwy
    firstIndex = []
    for val in valListCopy:
        if tempStartNode in val:
            firstIndex.append(val.index(tempStartNode))
    
    # it requires only one element (0 or 1)
    assert(len(firstIndex) == 1)
    # if first node of split graph is x coordinate
    if firstIndex[0] == 0:
        while tempEndNode != endNode:
            for ind, val in enumerate(valListCopy):
                if tempStartNode == val[0]:
                    tempStartNode = val[1]
                    tempEndNode = val[1]
                    
                    hwySplitOrderedDict[key].append(val)
                    valListCopy.pop(ind)
                    break
                
    # if first node of split graph is y coordinate
    elif firstIndex[0] == 1:
        while tempEndNode != endNode: 
            for ind, val in enumerate(valListCopy):
                if tempStartNode == val[1]:
                    tempStartNode = val[0]
                    tempEndNode = val[0]
                    
                    newNode1Id = val[2]['station2_ID']
                    newNode2Id = val[2]['station1_ID']
                    val2Dict =copy.deepcopy(val[2])
                    val2Dict['station1_ID'] = newNode1Id
                    val2Dict['station2_ID'] = newNode2Id
                    
                    valNew = (val[1], val[0], val2Dict)
                    hwySplitOrderedDict[key].append(valNew)
                    valListCopy.pop(ind)
                    break

savePath = '{}hwySplitOrderedDict_diss.p'.format(C.HIGHWAYS_R)
pickle.dump( hwySplitOrderedDict, open( savePath, 'wb' ) )
