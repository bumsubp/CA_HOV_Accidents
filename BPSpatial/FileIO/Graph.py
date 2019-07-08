"""
@author: bspark
"""

import networkx as nx
import geopandas as gpd
import math
import pandas as pd
import json

import BPSpatial.Constants as C
import sys
sys.path.append(C.BPSPATIAL)

import Analysis.Graph as AG

class Point():
    """
    class to handle point-type graph that only has nodes without edges
    """
    @staticmethod
    def fromShapefile_nx(shpPath, attrs=[], decimals = 6):
        """
        Method for importing a shapefile and converting it to a newtorkx graph
        using networkx. This may have a problem when the data has duplicate points
        
        Parameters
        ----------
        shpPath:        string
                        path of shapefile to handle
                        
        attrs:          list of string
                        attributes to add to a graph from the input shp file
                        
        Return
        ------
        graph:          networkx Graph
                        a graph only with nodes, not edges
                        graph.nodes - key:(x, y, ind), value:{column:value}
        """
        shp = nx.read_shp(shpPath)
        graph = nx.DiGraph()
        
        attrDict = {}
        for attr in attrs:
            attrDict[attr] = {}
            
        for ind, node in enumerate(shp.nodes(data=True)):
            graph.add_node((round(node[0][0], decimals), round(node[0][1], decimals), ind), Ind = ind)
            
            for attr in attrs:
                attrDict[attr][(round(node[0][0], decimals), round(node[0][1], decimals), ind)]=node[1][attr]
            
        # add attributes
        for attr in attrs:
            nx.set_node_attributes(graph, attr, attrDict[attr])
        
        return graph
    
    @staticmethod
    def fromShapefile(shpPath, attrs=[], decimals = 6):
        """
        Method for importing a shapefile and converting it to a newtorkx graph
        using geopandas to avoid of removal of points with the same coordinates
        
        Parameters
        ----------
        shpPath:        string
                        path of shapefile to handle
                        
        attrs:          list of string
                        attributes to add to a graph from the input shp file
                        
        Return
        ------
        graph:          networkx Graph
                        a graph only with nodes, not edges
                        graph.nodes - key:(x, y, ind), value:{column:value}
        """
        graph = nx.DiGraph()
        shp = gpd.read_file(shpPath)
        
        for attr in attrs:
            assert(attr in shp.keys())
        
        #construct attribute dataset in dictionary- key:(x, y, ind), value:{column:value}
        attrDict = {}
        for attr in attrs:
            attrDict[attr] = {}
            for ind, (geo, i) in enumerate(zip(shp.geometry, shp[attr])):
                attrDict[attr][(round(geo.x, decimals), round(geo.y, decimals), ind)]= i
                
        #add nodes
        for ind, geo in enumerate(shp.geometry):
            graph.add_node((round(geo.x, decimals), round(geo.y, decimals), ind), Ind = ind)

        #set attributes
        for attr in attrs:
            nx.set_node_attributes(graph, attr, attrDict[attr])
        
        return graph
    
    @staticmethod
    def fromExcel(excelPath, sheetName, geometryKey, header, columns, decimals=6):
        """
        Method for creating a networkx graph from excel file
        
        Parameters
        ----------
        excelPath:      string
                        path of excel file to access
        
        sheetName:      string
                        name of sheet name to access
                        
        geometryKey:    tuple
                        key of geometry(x,y) or (lng, lat) in columns or header list
                        
        header:         0 or None
                        0, if data contains column names, 
                        None, otherwise
        
        columns:        list of tuple
                        column name and type [(col1,dtype), (col2, dtype), ...]
        
        Return
        ------
        graph:          networkx graph
                        a point-type graph, only having nodes
        """
        assert(header == 0 or header == None)
        exc = pd.read_excel(excelPath, sheetName, header=header)
        
        if header == None:
            assert(columns != [] and len(columns) == len(exc.values[0]))
        else:
            columns = []
            for i, j in exc.dtypes.items():
                if str(j) in C.TYPES_EXCEL:
                    columns.append((i, C.TYPES_EXCEL[str(j)]))
                else:
                    columns.append((i, 'str'))
        
        exc = Point._nan(exc)
        geometryCol = (columns[geometryKey[0]][0], columns[geometryKey[1]][0])
        
        graph = nx.DiGraph()
        
        for ind, (x,y) in enumerate(zip(exc[geometryCol[0]], exc[geometryCol[1]])):
            graph.add_node((round(x, decimals), round(y, decimals), ind), Ind = ind)
        
        #construct attribute dataset in dictionary- key:(x, y, ind), value:{column:value}
        attrDict = {}
        for attr in columns:
            attrDict[attr[0]] = {}
            for ind, (x, y, a) in enumerate(zip(exc[geometryCol[0]], exc[geometryCol[1]], exc[attr[0]])):
                attrDict[attr[0]][(round(x, decimals), round(y, decimals), ind)] = a
            
        for attr in columns:
            nx.set_node_attributes(graph, attr[0], attrDict[attr[0]])
            
        return graph
    

    @staticmethod
    def fromCsv(csvPath, geometryKey, header=0, columns=[], decimals=6):
        """
        Method for creating a networkx graph from excel file
        
        Parameters
        ----------
        csvPath:        string
                        path of csv file to access
        
        geometryKey:    tuple
                        key of geometry(x,y) or (lng, lat) in columns or header list
                        
        header:         0 or None
                        0, if data contains column names, 
                        None, otherwise
        
        columns:        list of tuple
                        column name and type [(col1,dtype), (col2, dtype), ...]
        
        Return
        ------
        graph:          networkx graph
                        a point-type graph, only having nodes
        """
        assert(header == 0 or header == None)
        csv = pd.read_csv(csvPath, header=header)
        
        if header == None:
            assert(columns != [] and len(columns) == len(csv.values[0]))
        else:
            columns = []
            for i, j in csv.dtypes.items():
                if str(j) in C.TYPES_EXCEL:
                    columns.append((i, C.TYPES_EXCEL[str(j)]))
                else:
                    columns.append((i, 'str'))
                    
        csv = pd.read_csv(csvPath, header=header)
        assert(len(columns) == len(csv.keys()))
        
        csv = Point._nan(csv)
        
        graph = nx.DiGraph()
        
        for ind, row in enumerate(csv.values):
            x = row[geometryKey[0]]
            y = row[geometryKey[1]]
            graph.add_node((round(x, decimals), round(y, decimals), ind), Ind = ind)
        
        #construct attribute dataset in dictionary- key:(x, y, ind), value:{column:value}
        attrDict = {}
        for n, attr in enumerate(columns):
            attrDict[attr[0]] = {}
            for ind, row in enumerate(csv.values):
                x = row[geometryKey[0]]
                y = row[geometryKey[1]]
                a = row[n]
                attrDict[attr[0]][(round(x, decimals), round(y, decimals), ind)] = a
            
        for ind, attr in enumerate(columns):
            nx.set_node_attributes(graph, attr[0], attrDict[attr[0]])
            
        return graph
        
    @staticmethod    
    def _nan(pandasDF):
        for ind, row in enumerate(pandasDF.values): 
            for key, val in zip(pandasDF.keys(), row[:len(pandasDF.keys())]):
                if type(val) == float and math.isnan(val):
                    replace = -1
                    pandasDF.at[ind, key] = replace
        return pandasDF
    

        
class Polyline():
    """
    Class to handle polyline-type graph that has both nodes and edges.
    But nodes has no attributes.
    """
    
    @staticmethod
    def fromShapefile(shpPath, attrs=[], decimals=6):
        """
        Method for importing a shapefile and converting it to a newtorkx graph
        using networkx. This may have a problem when the data has duplicate points
        
        Parameters
        ----------
        shpPath:        string
                        path of shapefile to handle
                        
        attrs:          list of string
                        attributes to add to a graph from the input shp file
                        
        decimals:       int
                        number of decimals to round
                        
        Return
        ------
        graph:          networkx Graph
                        a graph only with nodes, not edges
                        graph.nodes - key:((x1, y2), (x2,y2)) value:{column:value}
        """
        shp = nx.read_shp(shpPath)
        graph = nx.DiGraph()
        
        for ind, node in enumerate(shp.nodes(data=True)):
            graph.add_node((round(node[0][0],decimals), round(node[0][1], decimals)), Ind = ind)
        
        attrDict = {}
        for attr in attrs:
            attrDict[attr] = {}
            
        for ind, edge in enumerate(shp.edges(data=True)):
            coordRound = []
            for coord in json.loads(edge[2]['Json'])['coordinates']:
                xyRound = []
                for ele in coord:
                    xyRound.append(round(ele,decimals))
                coordRound.append(xyRound)
            
            graph.add_edge((round(edge[0][0], decimals), round(edge[0][1], decimals)), \
                           (round(edge[1][0], decimals), round(edge[1][1], decimals)), \
                                Ind= ind, coordinates= coordRound)
            for attr in attrs:
                attrDict[attr][((round(edge[0][0], decimals), round(edge[0][1], decimals)), \
                               (round(edge[1][0], decimals), round(edge[1][1], decimals)))] \
                                =edge[2][attr]
            
        for attr in attrs:
            nx.set_edge_attributes(graph, attr, attrDict[attr])
                
        AG.graphCalculate.addDistance(graph)
        
        return graph