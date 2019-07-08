"""
@author: bspark
"""
import networkx as nx
import math
import sympy as sp

import BPSpatial.Constants as C
import sys
sys.path.append(C.BPSPATIAL)

import FileIO.RTree as rtree

class geometry():
    """
    Class to get variety of basic information geometry
    """
    @staticmethod
    def lineSpec(node1, node2):
        """
        Method for getting spec (slope, intercept, and distance)of a line between two input nodes
        
        Parameters
        ----------
        node1:  tuple
                (x, y) of node1
        
        node2:  tuple
                (x, y) of node2
                
        Returns
        -------
        m:      float or True/False
                slope of a line of node1 and node2 \n
                True - parallel to y axis \n
                False - paraller to x axis \n
                
        b:      float
                intercept
                
        d:      float or -1
                distance between node1 and node2 \n
                -1 - when node1 and node2 are the same \n
        """
        
        if node1 == node2:
            m = 0
            b = 0
            d = -1
            return m, b, d
            
        elif node1[0] == node2[0]: # parallel to y axis
            m = True
            b = node1[0]
            d = abs(node2[1] - node1[1])
            return m, b, d
            
        elif node1[1] == node2[1]: # parallel to x axis
            m = False
            b = node1[1]
            d = abs(node2[0] - node1[0])
            return m, b, d
            
        else:
            m = (node2[1] - node1[1]) / (node2[0] - node1[0])
            b = (node1[1]) - m*node1[0]
            d = geometry.lineLength(node1, node2)
            return m, b, d 
    
    @staticmethod
    def lineLength(node1, node2):
        """
        Method for getting distance between two input nodes
        
        Parameters
        ----------
        node1:  tuple
                (x, y) of node1
        
        node2:  tuple
                (x, y) of node2
                
        Return
        distance: float
        """
        return ((node2[1] - node1[1])**2 + (node2[0] - node1[0])**2)**(1/2)
    
    
    @staticmethod
    def isPointOnLine(node1, node2, point):
        """
        Method for check if a point is on a line of two input nodes
        
        Parameters
        ----------
        node1:  tuple
                (x, y) of node1
        
        node2:  tuple
                (x, y) of node2
                
        point:  tuple
                (x, y) of a point to check
                
        Return
        ------
        output: boolean
                True, if a point is on the line of two nodes \n
                False,otherwise  
        """
        m, b, d = geometry.lineSpec(node1, node2)
        if d == -1: # if two nodes are the same
            if node1 == point:
                return True
            else:
                return False
        else:
            if m == True: # parallel to y axis
                if point[0] == b and \
                (((node1[1] <= point[1]) and (point[1] <= node2[1])) or\
                 ((node2[1] <= point[1]) and (point[1] <= node1[1]))):
                    return True
                else:
                    return False
            
            elif m == False:
                if point[1] == b and \
                (((node1[0] <= point[0]) and (point[0] <= node2[0])) or\
                 ((node2[0] <= point[0]) and (point[0] <= node1[0]))):
                    return True
                else:
                    return False
                
            else:
                if(abs(point[1] - (m*point[0] + b)) < 0.05) and \
                (((node1[0] <= point[0]) and (point[0] <= node2[0])) or\
                 ((node2[0] <= point[0]) and (point[0] <= node1[0]))) and\
                (((node1[1] <= point[1]) and (point[1] <= node2[1])) or\
                 ((node2[1] <= point[1]) and (point[1] <= node1[1]))):
                    return True
                else:
                    return False
                
    @staticmethod
    def findNearPointOnLine(node1, node2, point):
        """
        Method for finding the nearest point on a straight infinite line form by
        two nodes from a point. This cannot guarantee the output point is on
        the line created by the two nodes.
        
        Parameters
        ----------
        node1:  tuple
                (x, y) of node1
        
        node2:  tuple
                (x, y) of node2
                
        point:  tuple
                (x, y) of a point to check
                
        Return
        ------
        x:      float
                x coordinate of the nearest point
                
        y:      float
                x coordinate of the nearest point
        """
        p=point[0]
        q=point[1]
        a=node1[0]
        b=node1[1]
        c=node2[0]
        d=node2[1]
        
        x = ((a-p)*(d-b) + (q-b)*(c-a)) / ((d-b)**2+(c-a)**2) * (d-b) + p
        y = ((a-p)*(d-b) + (q-b)*(c-a)) / ((d-b)**2+(c-a)**2) * (a-c) + q
        
        return x, y
    
    
    @staticmethod
    def findPointOnLine(node1, node2, distance):
        """
        Method for finding a point aparting distance from node1  
        on the line of node1 and node2
        
        Parameters
        ----------
        node1:      tuple
                    (x, y) of node1
        
        node2:      tuple
                    (x, y) of node2
                
        distance:   float
        
        Return
        ------
        xy:         list
                    coordinate set of the ouput point on the line of the input nodes
        """
        m, b, _ = geometry.lineSpec(node1, node2)
        
        xy = []
        if m == True: # parallel to y axis
            xy.append(node1[0])
            if node1[1] <= node2[1]:
                xy.append(node1[1] + distance)
            else:
                xy.append(node1[1] - distance)
        
        elif m == False: # parallel to x axis
            if node1[0] <= node2[0]:
                xy.append(node1[0] + distance)
            else:
                xy.append(node1[0] - distance)
            xy.append(node1[1])
        
        else:
            x = sp.Symbol('x')
            z = (x-node1[0])**2 + (m*x+b-node1[1])**2 - distance**2
            xSolution = sp.solve(z, x)
            
            for xSol in xSolution:
                if (xSol >= node1[0] and xSol <= node2[0]) or (xSol <= node1[0] and xSol >= node2[0]):
                    xy.append(xSol)
                    xy.append(xSol*m + b)
        return xy
                

class graphCalculate():
    """
    Class to implementing a variety of calculation of networkx graph object
    """
    @staticmethod
    def addDistance(graph):
        """
        Method for adding distance of edges in the input polyline graph
        
        Parameters
        ----------
        graph:  networkx graph
                polyine graph to add the distance of each edge
        """
        distanceList = graphCalculate._calculateDistance(graph)
        for dist, edge in zip(distanceList, graph.edges(data=True)):
            edge[2]['distance'] = dist
        
    @staticmethod
    def addCenter(graph, decimals=6):
        """
        Method for adding center point coordinate of edges in the input polyline graph
        
        Parameters
        ----------
        graph:  networkx graph
                polyine graph to add the center coordinates of each edge
        """
        for edge in graph.edges(data=True):
            prevVertex = None
            distnaceToGo = (edge[2]['distance']) / 2
            for ind, vertex in enumerate(edge[2]['coordinates']):
                if ind == 0:
                    prevVertex = vertex
                else:
                    currVertex = vertex
                    
                    distance = geometry.lineLength(prevVertex, currVertex)
                    if distnaceToGo > distance:
                        distnaceToGo -= distance
                    else:
                        centerPoint = geometry.findPointOnLine(prevVertex, currVertex, distnaceToGo)
                        edge[2]['center'] = [round(centerPoint[0], decimals), round(centerPoint[1], decimals)]
                        break
                    
                    prevVertex = currVertex
        
    @staticmethod
    def _calculateDistance(graph):
        distanceList = []
        for edge in graph.edges(data=True):
            dist = 0
            prevVertex = None
            for ind, vertex in enumerate(edge[2]['coordinates']):
                if ind == 0:
                    prevVertex = vertex
                else:
                    currVertex = vertex
                    segLen = geometry.lineLength(prevVertex, currVertex) 
                    dist+= segLen
                    
                    prevVertex = currVertex
            distanceList.append(dist)
        return distanceList
        
class near():
    """
    Class to find the nearest point from a point on a line
    """
    
    @staticmethod
    def pointOnPolyline(polylineGraph, pointGraph, criterion='', threshold=0):
        """
        Method for finding the nearest point of individual point feature of 
        a point graph among a set of line features of polyline graph
        
        Parameters
        ----------
        polylineGraph:  networkx graph
                        polyline graph in which a set of output points will be located
                        
        pointGraph:     networkx graph
                        point graph including points to check
                        
        criterion:      string
                        a common column name of point and line features
                        when finding the nearest point
                        
        threshold:      float
                        searching distance threshold when finding the nearest point
                        
        Return
        ------
        pntGraph:       networkx graph
                        point graph of the nearest points                        
        """
        pntGraph = pointGraph.copy()
        
        idxLine, edgeIdCoordDict = rtree.rtree_polyline(polylineGraph)
        
        for pnt in pntGraph.nodes(data=True):
            nearPolylineId = list(idxLine.nearest(rtree.pointRect(pnt[0]), 3))
            
            pointCandidateDict = {}
            for edgeId in nearPolylineId:
                edge = edgeIdCoordDict[edgeId] # key of polyline Graph
                
                if criterion == '':
                    
                    distToStartNode = geometry.lineLength(pnt[0], list(edge[0]))
                    distToEndNode = geometry.lineLength(pnt[0], list(edge[1]))
                    if threshold == 0:
                        pointCandidateDict[distToStartNode] = edge[0]
                        pointCandidateDict[distToEndNode] = edge[1]
                    else:
                        if distToStartNode <= threshold:
                            pointCandidateDict[distToStartNode] = edge[0]
                        if distToEndNode <= threshold:
                            pointCandidateDict[distToEndNode] = edge[1]
                        
                    prevVertex = None
                    for ind, vertex in enumerate(polylineGraph.edge[edge[0]][edge[1]]['coordinates']):
                        if ind == 0:
                            prevVertex = vertex
                        else:
                            currVertex = vertex
                            
                            nearX, nearY = geometry.findNearPointOnLine(prevVertex, currVertex, pnt[0])
                            nearXY = (nearX, nearY)
                            
                            onLine = geometry.isPointOnLine(prevVertex, currVertex, nearXY)
                            if onLine == True:
                                distPointLine = geometry.lineLength(nearXY, pnt[0])
                                if threshold == 0:
                                    pointCandidateDict[distPointLine] = nearXY
                                else:
                                    if distPointLine <= threshold:
                                        pointCandidateDict[distPointLine] = nearXY
                            prevVertex = currVertex
                            
                else: # if there is a criterion
                    if polylineGraph.edge[edge[0]][edge[1]][criterion] == pnt[1][criterion]:
                        
                        distToStartNode = geometry.lineLength(pnt[0], list(edge[0]))
                        distToEndNode = geometry.lineLength(pnt[0], list(edge[1]))
                        if threshold == 0:
                            pointCandidateDict[distToStartNode] = edge[0]
                            pointCandidateDict[distToEndNode] = edge[1]
                        else:
                            if distToStartNode <= threshold:
                                pointCandidateDict[distToStartNode] = edge[0]
                            if distToEndNode <= threshold:
                                pointCandidateDict[distToEndNode] = edge[1]
                            
                        prevVertex = None
                        for ind, vertex in enumerate(polylineGraph.edge[edge[0]][edge[1]]['coordinates']):
                            if ind == 0:
                                prevVertex = vertex
                            else:
                                currVertex = vertex
                                
                                nearX, nearY = geometry.findNearPointOnLine(prevVertex, currVertex, pnt[0])
                                nearXY = (nearX, nearY)
                                
                                onLine = geometry.isPointOnLine(prevVertex, currVertex, nearXY)
                                if onLine == True:
                                    distPointLine = geometry.lineLength(nearXY, pnt[0])
                                    if threshold == 0:
                                        pointCandidateDict[distPointLine] = nearXY
                                    else:
                                        if distPointLine <= threshold:
                                            pointCandidateDict[distPointLine] = nearXY
                                prevVertex = currVertex
            
                
            # after looking through the entire edges, select the edge id with the minimum distance
            if len(pointCandidateDict) != 0:
                finalPnt = pointCandidateDict[min(sorted(pointCandidateDict))]
                pntGraph.node[finalPnt] = pntGraph.node.pop(pnt[0])
                
            else:
                pntGraph.node.pop(pnt[0])
                
        return pntGraph


class split():
    """
    Class to implementing split process for polyline graph objects
    """
    @staticmethod
    def _findPointIter(startNode, endNode, distance):
        d = geometry.lineLength(startNode, endNode)
        if d < distance:
            tempNode = endNode
            remainD = d
            iteration = False
        else:
            solution = geometry.findPointOnLine(startNode, endNode, distance)
            
            tempNode = tuple(solution)
            remainD = 0
            iteration = True
        return tempNode, remainD, iteration
    
    @staticmethod
    def _splitNodes(graph, distance, decimals=6):
        splitNodesList = []
        for edge in graph.edges(data=True):
            
            # for one edge, find the new edges (sub-edges) and nodes based on the distance 
            nodeList = [] # node list on a edge list[tuple()]
            
            prevVertex = None 
            currVertex = None
            remainD = 0      # remaining distance to go
            distance = distance
            distanceToGo = distance
            
            nodeList.append(edge[0]) # starts with the first node
            
            # if the length of the edge is smaller than the distance, add the end node
            # without any sub-node
            edgeLen = geometry.lineLength(edge[0], edge[1])
            
            # if the length of the edge is greater than the distance
            if edgeLen >= distance:
                # find the nodes every after the distance
                for ind, vertex in enumerate(edge[2]['coordinates']):
                    iteration = True
                    
                    if ind == 0:
                        prevVertex = vertex
                    else:
                        currVertex = vertex
                        
                        iterationNum = 0
                        while iteration:
                            if iterationNum != 0:
                                distanceToGo = distance
                            distanceToGo -= remainD
                            tempPoint, remainD, iteration = split._findPointIter(prevVertex, currVertex, distanceToGo)
                            if tempPoint != currVertex:
                                nodeList.append((round(tempPoint[0], decimals), round(tempPoint[1], decimals)))
                            
                            iterationNum+=1 
                            prevVertex = tempPoint
            
            nodeList.append(edge[1]) #endNode
            splitNodesList.extend(nodeList)
        
        return list(set(splitNodesList))
    
    @staticmethod
    def byDistance(graph, distance, edgeAttrs=[]):
        """
        Method for spliting polyline object every length of the distance
        
        Parameters
        ----------
        graph:      networkx graph
                    polyline type graph to split
                    
        distance:   float
        
        
        Return
        ------
        splitGraph: network garph
                    split polyline type graph
        """
    
        #==============================================================================
        # fromNode, toNode, {Ind, coordinates, distance, center}
        # fromNode (tuple): coordinate of start node
        # toNode (tuple): coordinate of end node
        # Ind (int): identifier
        # coordinates (doubl list): a list of coordinates of vertices of the segment
        # distnace (float): distance of the segment
        # center (list): coordinate of center of the segment
        #==============================================================================
        
        splitGraph = nx.DiGraph()
    
        nodeList = split._splitNodes(graph, distance)
        
        splitGraph.add_nodes_from(nodeList)
        
        attrsDict = {}
        
        splitEdgeInd = 0
        for edgeInd, edge in enumerate(graph.edges(data=True)):
            vertexDict = {}
            prevVertex = None
            cumulDistance = 0
            
            # for each eage, locate the nodes between the corrseponding vertices
            for ind, vertex in enumerate(edge[2]['coordinates']):
                if ind == 0:
                    prevVertex = vertex
                    
                    # add the first vertex in the vertex list
                    vertexDict[cumulDistance] = prevVertex
                else:
                    currVertex = vertex
                    
                    
                    # find the nodes which are between the prevVertex and currVertex
                    m, b, d = geometry.lineSpec(prevVertex, currVertex)
                    
                    for node in nodeList:
                        if m == True: # parallel to y axis
                            if node[0] == b and \
                            (((prevVertex[1] <= node[1]) and (node[1] <= currVertex[1])) or\
                             ((currVertex[1] <= node[1]) and (node[1] <= prevVertex[1]))):
                                 # if the node is between the vertices, 
                                 # calculate the length between the prevVertex and the node
                                 seglen = geometry.lineLength(prevVertex, node)
                                 # add the node into the dictionary
                                 vertexDict[seglen+cumulDistance] = node
                                
                        elif m == False:
                            if node[1] == b and \
                            (((prevVertex[0] <= node[0]) and (node[0] <= currVertex[0])) or\
                             ((currVertex[0] <= node[0]) and (node[0] <= prevVertex[0]))):
                                 # if the node is between the vertices, 
                                 # calculate the length between the prevVertex and the node
                                 seglen = geometry.lineLength(prevVertex, node)
                                 # add the node into the dictionary
                                 vertexDict[seglen+cumulDistance] = node
                                 
                        else:
                            if(abs(node[1] - (m*node[0] + b)) < 0.05) and \
                            (((prevVertex[0] <= node[0]) and (node[0] <= currVertex[0])) or\
                             ((currVertex[0] <= node[0]) and (node[0] <= prevVertex[0]))) and\
                             (((prevVertex[1] <= node[1]) and (node[1] <= currVertex[1])) or\
                             ((currVertex[1] <= node[1]) and (node[1] <= prevVertex[1]))):
                                 # if the node is between the vertices, 
                                 # calculate the length between the prevVertex and the node
                                 seglen = geometry.lineLength(prevVertex, node)
                                 # add the node into the dictionary
                                 vertexDict[seglen+cumulDistance] = node
                            
                    cumulDistance += geometry.lineLength(prevVertex, currVertex)
                    vertexDict[cumulDistance] = currVertex
                    
                    prevVertex = currVertex
            
            
            orderedVertexList = []
            for key in sorted(vertexDict.keys()):
                orderedVertexList.append(list(vertexDict[key]))
            
            startInd1 = 0
            for ind1, vertex1 in enumerate(orderedVertexList):
                # check whether vertex1 is in nodelist
                endInd1 = 0
                for splitNode in nodeList:
                    if tuple(vertex1) == splitNode:
                        endInd1 = ind1
                        
                        coordList = orderedVertexList[startInd1:endInd1 + 1]
                        startVertex = tuple(orderedVertexList[startInd1])
                        endVertex = tuple(orderedVertexList[endInd1])
                        
                        if startVertex != endVertex:
                            splitGraph.add_edge(startVertex, endVertex, Ind=splitEdgeInd, coordinates = coordList)
                            
                            attrsDict[(startVertex, endVertex)] = {}
                            for edgeAttr in edgeAttrs:
                                attrsDict[(startVertex, endVertex)][edgeAttr] = edge[2][edgeAttr]
                            
                            startInd1 = endInd1
                            splitEdgeInd+=1
#        print(edgeAttrs)
#        if edgeAttrs != []:
#            for attr in edgeAttrs:
#                print(attr)
#                attrDict = {key1:val1[attr] for key1, val1 in attrsDict.items()}
#                print(attrDict)
#                nx.set_edge_attributes(splitGraph, attr, attrDict)
                
        for edge in splitGraph.edges(data=True):
            for attr in edgeAttrs:
                edge[2][attr] = attrsDict[(edge[0], edge[1])][attr]
            
            
        graphCalculate.addDistance(splitGraph)
        graphCalculate.addCenter(splitGraph)
        return splitGraph
    
    
    @staticmethod
    def splitLineAtPoint(lineGraph, pointGraph, nodeAttrs=[], decimals=6):
        """
        Method for split a polyline type graph at individual points of input point list
        
        Parameters
        ----------
        lineGraph:      networkx graph
                        polyline type graph to split
                        
        pointGraph:     networkx graph
                        point type graph by which a line graph is split
                        
        nodeAttrs:      nested list
                        list of attribute tuple of attribute name and its type in the pointGraph \n
                        [('ID', 'int'), ('Latitude', 'float')]
        
        Return
        ------
        lineGraphCopy:  networkx graph
                        split polyline type graph based on a set of points
        """
        lineGraphCopy = lineGraph.copy()
        initConvert = {'str': '', 'int': -1, 'float': -1, 'bool':False}
        for node in nodeAttrs:
            nx.set_edge_attributes(lineGraphCopy, 'node1_{}'.format(node[0]), initConvert[node[1]])
            nx.set_edge_attributes(lineGraphCopy, 'node2_{}'.format(node[0]), initConvert[node[1]])
        attrs = set(list(lineGraphCopy.edges(data=True)[0][2].keys()))
        attrs = attrs.difference(set(['Ind', 'coordinates']))
#        remains = set(['Ind', 'coordinates'] + list(attrs))
#        delAttrs = attrs.difference(remains)
#        
#        for edge in lineGraphCopy.edges(data=True):
#            for delAttr in delAttrs:
#                del edge[2][delAttr]
        
        pointList = []
        for point in pointGraph.nodes(data=True):
            pointList.append([point[0][0], point[0][1]])
        
        tempId = len(pointGraph.nodes(data=True))
        
        # for every center point (splitFeatures)
        for pointInd, point in enumerate(pointList):
#            print('{}/{}'.format(pointInd, len(pointList)))
            # find the edge that the center point located
            done = False
            for edge in lineGraphCopy.edges(data=True):
                # among the segments in the edge
                prevVertex = None
                for ind, vertex in enumerate(edge[2]['coordinates']):
                    if ind == 0:
                        prevVertex = vertex
                    else:
                        currVertex = vertex
                        onLine = geometry.isPointOnLine(prevVertex, currVertex, point)
                        
                        near_x,near_y = geometry.findNearPointOnLine(prevVertex, currVertex, point)
                        near_dist = geometry.lineLength((near_x, near_y), point)
                        # if the center point is on the segment
                        if onLine == True and near_dist < 0.0001:
                            coord1 = edge[2]['coordinates'][:ind]
                            coord1.append((near_x, near_y)) # add 'point' in the end of the list
                            coord2 = edge[2]['coordinates'][ind:]
                            coord2.insert(0, (near_x, near_y)) # add 'point' at the front of the list
                            
#                            startNode1 = tuple(coord1[0])
                            startNode1 = tuple([round(coord, decimals) for coord in coord1[0]])
#                            endNode1 = tuple(coord1[-1])
                            endNode1 = tuple([round(coord, decimals) for coord in coord1[-1]])
#                            startNode2 = tuple(coord2[0])
                            startNode2 = tuple([round(coord, decimals) for coord in coord2[0]])
#                            endNode2 = tuple(coord2[-1])
                            endNode2 = tuple([round(coord, decimals) for coord in coord2[-1]])
                            
                            attrsDict = {}
                            attrsDict['Ind'] = tempId
                            attrsDict['coordinates'] = coord1
                            
                            for attr in attrs:
                                attrsDict[attr] = edge[2][attr]
                            
                            for nodeAttr in nodeAttrs:
                                key1 = tuple(coord1[0])
#                                key1 = (round(coord1[0][0], decimals), round(coord1[0][1], decimals))
                                if key1 in pointGraph.nodes():
                                    attrsDict['node1_{}'.format(nodeAttr[0])] = pointGraph.node[key1][nodeAttr[0]]
                                  
                                key2 = tuple(coord1[-1])
#                                key2 = (round(coord1[-1][0], decimals), round(coord1[-1][1], decimals))
                                if key2 in pointGraph.nodes():
                                    attrsDict['node2_{}'.format(nodeAttr[0])] = pointGraph.node[key2][nodeAttr[0]]
                                
                            if startNode1 != endNode1:
                                lineGraphCopy.add_edge(startNode1, endNode1, attrsDict)
                                tempId+=1
                            
                            attrsDict['Ind'] = tempId
                            attrsDict['coordinates'] = coord2
                            
                            for nodeAttr in nodeAttrs:
                                key1 = tuple(coord2[0])
#                                key1 = (round(coord2[0][0], decimals), round(coord2[0][1], decimals))
                                if key1 in pointGraph.nodes():
                                    attrsDict['node1_{}'.format(nodeAttr[0])] = pointGraph.node[key1][nodeAttr[0]]
                                
                                key2 = tuple(coord2[-1])
#                                key2 = (round(coord2[-1][0], decimals), round(coord2[-1][1], decimals))
                                if key2 in pointGraph.nodes():
                                    attrsDict['node2_{}'.format(nodeAttr[0])] = pointGraph.node[key2][nodeAttr[0]]
                            
                            if startNode2 != endNode2:
                                lineGraphCopy.add_edge(startNode2, endNode2, attrsDict)
                                tempId+=1
                            
                            # remove the original edge
                            e = (edge[0], edge[1], {'Ind':edge[2]['Ind']})
                            lineGraphCopy.remove_edge(*e[:2])
                            
                            prevVertex = currVertex
                            
                            done = True
                            break
                        
                        prevVertex = currVertex
                if done == True:
                    break
        
        graphCalculate.addDistance(lineGraphCopy)
        return lineGraphCopy
    
    @staticmethod
    def splitLineAtPoint_backup(lineGraph, pointGraph, decimals=6):
        """
        Method for split a polyline type graph at individual points of input point list
        
        Parameters
        ----------
        lineGraph:      networkx graph
                        polyline type graph to split
                        
        pointGraph:     networkx graph
                        point type graph by which a line graph is split
        
        Return
        ------
        lineGraphCopy:  networkx graph
                        split polyline type graph based on a set of points
        """
        lineGraphCopy = lineGraph.copy()
        attrs = set(list(lineGraphCopy.edges(data=True)[0][2].keys()))
        remains = set(['Ind', 'coordinates'] + list(attrs))
        delAttrs = attrs.difference(remains)
        
        for edge in lineGraphCopy.edges(data=True):
            for delAttr in delAttrs:
                del edge[2][delAttr]
        
        pointList = []
        for point in pointGraph.nodes(data=True):
            pointList.append([point[0][0], point[0][1]])
        
        tempId = len(pointGraph.nodes(data=True))
        
        # for every center point (splitFeatures)
        for pointInd, point in enumerate(pointList):
            print('{}/{}'.format(pointInd, len(pointList)))
            # find the edge that the center point located
            done = False
            for edge in lineGraphCopy.edges(data=True):
                # among the segments in the edge
                prevVertex = None
                for ind, vertex in enumerate(edge[2]['coordinates']):
                    if ind == 0:
                        prevVertex = vertex
                    else:
                        currVertex = vertex
                        onLine = geometry.isPointOnLine(prevVertex, currVertex, point)
                        
                        # if the center point is on the segment
                        if onLine == True:
                            coord1 = edge[2]['coordinates'][:ind]
                            coord1.append(point) # add 'point' in the end of the list
                            coord2 = edge[2]['coordinates'][ind:]
                            coord2.insert(0, point) # add 'point' at the front of the list
                            
                            
#                            startNode1 = tuple(coord1[0])
                            startNode1 = tuple([round(coord, decimals) for coord in coord1[0]])
#                            endNode1 = tuple(coord1[-1])
                            endNode1 = tuple([round(coord, decimals) for coord in coord1[-1]])
#                            startNode2 = tuple(coord2[0])
                            startNode2 = tuple([round(coord, decimals) for coord in coord2[0]])
#                            endNode2 = tuple(coord2[-1])
                            endNode2 = tuple([round(coord, decimals) for coord in coord2[-1]])
                            
                            attrsDict = {}
                            attrsDict['Ind'] = tempId
                            attrsDict['coordinates'] = coord1
                            attrs = attrs.difference(set(['Ind', 'coordinates']))
                            for attr in attrs:
                                attrsDict[attr] = edge[2][attr]
                                
                            lineGraphCopy.add_edge(startNode1, endNode1, attrsDict)
                            tempId+=1
                            
                            attrsDict['Ind'] = tempId
                            attrsDict['coordinates'] = coord2
                            lineGraphCopy.add_edge(startNode2, endNode2, attrsDict)
                            tempId+=1
                            
                            # remove the original edge
                            e = (edge[0], edge[1], {'Ind':edge[2]['Ind']})
                            lineGraphCopy.remove_edge(*e[:2])
                            
                            prevVertex = currVertex
                            
                            done = True
                            break
                        
                        prevVertex = currVertex
                if done == True:
                    break
        
        graphCalculate.addDistance(lineGraphCopy)
        return lineGraphCopy
    
    
class intersect():
    """
    Class to implement intersect analysis
    """
    @staticmethod
    def _intersections(graph):
        intersectSet = set()
        uniqueSet = set()
        
        edges = graph.edges(data=True)
        for edge in edges:
            for vertex in edge[2]['coordinates']:
                vertex = tuple(vertex)
                if vertex not in uniqueSet:
                    uniqueSet.add(vertex)
                else:
                    intersectSet.add(vertex)
        return intersectSet

    @staticmethod
    def byGeometry(graph):
        """
        Method for implementing intersect with polyline type graph.
        The features are recreated based on the geometry (vertices)
        
        Parameters
        ----------
        graph:      networkx graph
                    polyline type input graph
                
        Return
        ------
        outputGraph: networkx graph
                     polyline type graph which split by intersected vertices
        
        """
        edgeId = 0 # for edge's id
        outputGraph = nx.DiGraph() # output : networkx graph
        
        intersectedNodes = intersect._intersections(graph)
        
        # for each edge, check if any of intersected points are on the edge
        for edge in graph.edges(data=True):
            intersectedNodeDict = {}
            for iNode in intersectedNodes:
                # excludes the two end points
                for ind, vertex in enumerate(edge[2]['coordinates'][:-1]):
                    if ind == 0:
                        pass
                    else:
                        if tuple(vertex) == iNode:
                            intersectedNodeDict[ind] = vertex
            
            coordinatesList = []
            coordinatesList.append(list(edge[0]))
            for key in sorted(intersectedNodeDict.keys()):
                coordinatesList.append(intersectedNodeDict[key])
            coordinatesList.append(list(edge[1]))
            
            startVertex = None
            for ind, coord in enumerate(coordinatesList):
                outputGraph.add_node(tuple(coord))
                if ind == 0:
                    startVertex = coord
                else:
                    endVertex = coord
                    startInd = edge[2]['coordinates'].index(startVertex)
                    endInd = edge[2]['coordinates'].index(endVertex)
                    
                    vertexList = None
                    if edge[2]['coordinates'][startInd:endInd+1] == []:
                        vertexList = edge[2]['coordinates'][endInd:startInd+1]
                    else:
                        vertexList = edge[2]['coordinates'][startInd:endInd+1]
                    
                    outputGraph.add_edge(tuple(startVertex), tuple(endVertex),\
                                         Ind= edgeId, coordinates= vertexList)
                    startVertex = endVertex
                    edgeId +=1
        graphCalculate.addDistance(outputGraph)
        return outputGraph
    

class spatialjoin():
    """
    Class to implement spatialjoin analysis between point and line features
    """
    @staticmethod
    def _spatialjoin(pntGraph, lineGraph, criterion, threshold):
        
        # init spatialJoinDict showing the edge id matched to each point
        # ind - point id, value - edge id 
        spatialJoinDict = {}
    
        pointGraph = pntGraph.copy()
#        pointGraph = nx.DiGraph()
        
#        # create a point graph
#        for ind, node in enumerate(pntGraph.nodes(data=True)):
#            pointGraph.add_node(node[0], Ind=node[1]['Ind'])
            
        # init 'matNumDict' showing the number of points matched to each edge
        # ind - edge id, value - 0 (initial)
        matNumDict = {}
        for edge in lineGraph.edges(data=True):
            matNumDict[edge[2]['Ind']] = 0
            
        idxLine, edgeIdCoordDict = rtree.rtree_polyline(lineGraph)
        
        # match each point to an edge
        # first iteration - points     
        for point in pointGraph.nodes(data=True):
            
            p = point[0][0]
            q = point[0][1]
            
            nearPolylineId = list(idxLine.nearest(rtree.pointRect(point[0]), 3))
            
            # second iteration - edge
            edgeCandidateDict={}
            for edgeId in nearPolylineId:
                edge = edgeIdCoordDict[edgeId]
                
                if criterion == '':
                
                    # for one point, add the distance to start node and end node to the candidateDict
                    distToStartNode = geometry.lineLength(point[0], list(edge[0]))
                    distToEndNode = geometry.lineLength(point[0], list(edge[1]))
                    
                    if threshold == 0:
                        edgeCandidateDict[distToStartNode] = edgeId
                        edgeCandidateDict[distToEndNode] = edgeId
                    else:
                        if distToStartNode <= threshold:
                            edgeCandidateDict[distToStartNode] = edgeId
                        
                        if distToEndNode <= threshold:
                            edgeCandidateDict[distToEndNode] = edgeId
                    
                    prevVertex = None
                    for ind, vertex in enumerate(lineGraph.edge[edge[0]][edge[1]]['coordinates']):
                        if ind == 0:
                            prevVertex = vertex
                        else:
                            currVertex = vertex
                            
                            a = prevVertex[0]
                            b = prevVertex[1]
                            c = currVertex[0]
                            d = currVertex[1]
                    
                            # find the point on the edge which closest from the point p and q
                            x, y = geometry.findNearPointOnLine((a,b), (c,d), (p,q))
                    
                            # chech if the x and y are on the edge
                            # if true, add it into the dictionary key = distance, value = edge id
                            onLine = geometry.isPointOnLine(prevVertex, currVertex, [x,y])
                            if onLine == True:
                                distPointLine = geometry.lineLength(point[0], [x,y])
                                if threshold == 0:
                                    edgeCandidateDict[distPointLine] = edgeId
                                else:
                                    if distPointLine <= threshold:
                                        edgeCandidateDict[distPointLine] = edgeId
                            
                            prevVertex = currVertex
                else: # if there is a criterion
                    if lineGraph.edge[edge[0]][edge[1]][criterion] == point[1][criterion]:
                        
                        # for one point, add the distance to start node and end node to the candidateDict
                        distToStartNode = geometry.lineLength(point[0], list(edge[0]))
                        distToEndNode = geometry.lineLength(point[0], list(edge[1]))
                        
                        if threshold == 0:
                            edgeCandidateDict[distToStartNode] = edgeId
                            edgeCandidateDict[distToEndNode] = edgeId
                        else:
                            if distToStartNode <= threshold:
                                edgeCandidateDict[distToStartNode] = edgeId
                            
                            if distToEndNode <= threshold:
                                edgeCandidateDict[distToEndNode] = edgeId
                        
                        prevVertex = None
                        for ind, vertex in enumerate(lineGraph.edge[edge[0]][edge[1]]['coordinates']):
                            if ind == 0:
                                prevVertex = vertex
                            else:
                                currVertex = vertex
                                
                                a = prevVertex[0]
                                b = prevVertex[1]
                                c = currVertex[0]
                                d = currVertex[1]
                        
                                # find the point on the edge which closest from the point p and q
                                x, y = geometry.findNearPointOnLine((a,b), (c,d), (p,q))
                        
                                # chech if the x and y are on the edge
                                # if true, add it into the dictionary key = distance, value = edge id
                                onLine = geometry.isPointOnLine(prevVertex, currVertex, [x,y])
                                if onLine == True:
                                    distPointLine = geometry.lineLength(point[0], [x,y])
                                    if threshold == 0:
                                        edgeCandidateDict[distPointLine] = edgeId
                                    else:
                                        if distPointLine <= threshold:
                                            edgeCandidateDict[distPointLine] = edgeId
                                
                                prevVertex = currVertex
                        
                
            # after looking through the entire edges, select the edge id with the minimum distance
            if len(edgeCandidateDict) != 0:
                finalEdgeId = edgeCandidateDict[min(sorted(edgeCandidateDict))]
                spatialJoinDict[point[1]['Ind']] = finalEdgeId
                matNumDict[finalEdgeId] += 1
            else:
                finalEdgeId = -1
                spatialJoinDict[point[1]['Ind']] = finalEdgeId
            
            # assign the point to the corresponding edge (edge count+=1)
        return matNumDict, spatialJoinDict
        
    @staticmethod
    def nearest(pntGraph, lineGraph, criterion='', threshold=0):
        """
        Method for finding the nearest polyline feature and assign its id to the point feature
        
        Parameters
        ----------
        pntGraph:   networkx graph
                    point type graph where the id of the nearest edge to be added
            
        lineGraph:  networkx garph
                    polyline type graph whose id's are searched
        
        criterion:  string
                    a common column name of point and line features
                    when finding the nearest point
            
        threshold:  float
                    searching radius
                    
        """
        _, spatialJoinDict = spatialjoin._spatialjoin(pntGraph, lineGraph, criterion, threshold)
        for point in pntGraph.nodes(data=True):
            point[1]['nearEdge'] = spatialJoinDict[point[1]['Ind']]
        print('The Ind of the nearest polyline is added to the POINT type graph.')
        
    @staticmethod
    def joincount(pntGraph, lineGraph, criterion='', threshold=0):
        """
        Method for calculating the number of points which assigned to each polyline object in the spatial join process        
        Parameters
        ----------
        pntGraph:   networkx graph
                    point type graph where the id of the nearest edge to be added
            
        lineGraph:  networkx garph
                    polyline type graph whose id's are searched
        
        criterion:  string
                    a common column name of point and line features
                    when finding the nearest point
            
        threshold:  float
                    searching radius
                    
        """
        matNumDict, _ = spatialjoin._spatialjoin(pntGraph, lineGraph, criterion, threshold)
        for edge in lineGraph.edges(data=True):
            edge[2]['joinCount'] = matNumDict[edge[2]['Ind']]
        print('The join count is added to the POLYLINE type graph.')
        
class interpolate():
    """
    Class to implement interpolate analysis.
    
    Calculate a density value based on \n
    1) a kernel function, \n
     http://desktop.arcgis.com/en/arcmap/10.3/tools/spatial-analyst-toolbox/an-overview-of-the-interpolation-tools.htm \n
     http://connor-johnson.com/2014/03/20/simple-kriging-in-python/ \n
    2) network distance - centerGraph > distance, \n
    3) the number of events on the source lixel - splitGraph > pointCount
    """
    @staticmethod
    def _gaussian(bandwidth, d):
        return 1/math.sqrt(2*math.pi)*math.exp((-1/2)*(d/bandwidth)**2)
    
    @staticmethod
    def _initiaize(lixelGraph, lxcenterGraph):
        # create lookup dictionary key:value = center :(startNode, endNode, joincount)
        lookupDict={}
        for edge in lixelGraph.edges(data=True):
            lookupDict[tuple(edge[2]['center'])] = (edge[0], edge[1], edge[2]['joinCount'])
            
        # neighborsDict key:center point, value: number of neighbors
        neighborsDict = {}
        for node in lxcenterGraph.nodes():
            neighbor = len(lxcenterGraph.neighbors(node))
            if neighbor == 1:
                neighborsDict[node] = neighbor + 1
            else:
                neighborsDict[node] = neighbor
        return lookupDict, neighborsDict  
    
    @staticmethod
    def graphKDE(lixelGraph, lxcenterGraph, bandwidth, kernel = 'gaussian', diverge=True):
        """
        Method for calculating Kernel Density Estimate using lixel graph and lixel center graph
        
        Parameters
        ----------
        lixelGraph:     networkx DiGraph
                        Polyline graph of split edges with join count of events
        
        lxcenterGraph:  networkx DiGraph(Polyline)
                        Polyline graph split by center points
        Return
        ------
        kernelDensity:  list(tuple(), double)
                        list of kernel density estimate [tuple(center), kde]
                        
                        
        """
        
        lookupDict, neighborsDict = interpolate._initiaize(lixelGraph, lxcenterGraph)
        
        kernelDensity = []
        for edge in lixelGraph.edges(data=True):
            # extract center
            center = edge[2]['center']
            
            # find the shortest path for all nodes
            pred, dist = nx.shortest_paths.weighted.dijkstra_predecessor_and_distance(lxcenterGraph, tuple(center), weight = 'distance')
        
            # find neighbors within the bandwidth
            neighbor = None
            sortedDist = sorted(dist.items(), key=lambda x: x[1])
            for ind, (key, val) in enumerate(sortedDist):
                if val > bandwidth:
                    neighbor = sortedDist[:ind+1]
                    break
                
                if ind == len(sortedDist) - 1 and val <= bandwidth:
                    neighbor = sortedDist
            kd = 0
            for nb in neighbor:
                divergeWeight = 1
                if diverge == True:
                    endNode = nb[0]
                    currNode = endNode
                    predNode = None
                    
                    while True:
                        predNode = pred[tuple(currNode)]
                        if predNode != []:
                            divergeWeight *= neighborsDict[predNode[0]] - 1
                            currNode = predNode[0]
                        else:
                            break
                
                # calculate kernel density for the sample
                # neighbor - tuple(center, distance)
                try:
                    # joincount (number of events) based on the center
                    jc = lookupDict[nb[0]][2]
                except KeyError:
                    pass
                else:
                    d = nb[1]
                    if kernel == 'gaussian':
                        kd += jc*interpolate._gaussian(bandwidth,d)/divergeWeight
                
            kernelDensity.append((tuple(center), kd))
        
        return kernelDensity