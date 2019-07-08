import shapefile
import urllib.request
import geopandas as gpd
import fiona
import shutil
#from mpl_toolkits.basemap import Basemap # https://anaconda.org/conda-forge/basemap
#import matplotlib.pyplot as plt
#import numpy as np

import BPSpatial.Constants as C


class dbf():
    """
    class for handling dbf file, which attributes of spatial dataset
    """
    
    @staticmethod
    def dropFields(shpPath, dropfieldList):
        """
        Method that delete fields of geopandas Dataframe
        
        Parameters
        ----------
        shpPath:        string
                        path of shapefile to handle
                        
        dropfieldList:  list
                        column names to delete
        """
        gpdData = gpd.read_file(shpPath)
        assert(False not in [i in gpdData.keys() for i in dropfieldList])
        
        prjPath = '{}prj'.format(shpPath[:-3])
        prjDesc = open(prjPath, 'r').read()
        
        for field in dropfieldList:
            gpdData.pop(field)
        gpdData.to_file(shpPath)
        
        prj = open(prjPath, 'w+')
        prj.write(prjDesc)
        prj.close()
        print('Remaining fields: {}'.format(gpdData.keys()))
        
    
    @staticmethod
    def renameField(shpPath, fromName, toName):
        """
        Method that change name of column
        
        Parameters
        ----------
        shpPath:        string
                        path of shapefile to handle
                        
        fromName:       string
                        column name to change
        
        toName:         string
                        new name of the column
        """
        gpdData = gpd.read_file(shpPath)
        
        assert(fromName in gpdData.keys())
        
        prjPath = '{}prj'.format(shpPath[:-3])
        prjDesc = open(prjPath, 'r').read()
        
        gpdData[toName] = gpdData.pop(fromName)
        gpdData.to_file(shpPath)
        
        prj = open(prjPath, 'w+')
        prj.write(prjDesc)
        prj.close()
        print('The field name is changed from "{}" to "{}"'.format(fromName, toName))
        
        
class Point():
    """
    Class for creating a shapefile of point data
    """

    @staticmethod
    def _addRecords(point_shp, fields, records, geometryKey):
        """
        Private method to add records when creating a shapefile
        """
        for ind, row in enumerate(records):
            if row[geometryKey[0]] == -1 and row[geometryKey[1]] == -1: # except for nan cases
                pass
            else:
                point_shp.point(float(row[geometryKey[0]]), float(row[geometryKey[1]])) # (lon, lat) or (x, y)
                point_shp.record(*tuple([row[f] for f in range(len(fields))]))
        return point_shp
    
    @staticmethod
    def fromGraph(pntGraph, shpPath):
        """
        Method that creates a point shapefile from a networkx graph
        
        type of shapefile - https://en.wikipedia.org/wiki/Shapefile
        
        Example - https://glenbambrick.com/2016/01/09/csv-to-shapefile-with-pyshp/
        
        Parameters
        ----------
        pntGraph:       neworkx.Graph
                        a graph only has nodes object, not edges
        
        shpPath:        string
                        path of shapefile to handle
        """
        point_shp = shapefile.Writer(shapefile.POINT)
        point_shp.autoBalance = 1
        
        colList = [('X', 'float'), ('Y', 'float')]
        for key, val in pntGraph.nodes(data=True)[0][1].items():
            colList.append((key, str(type(val))))
                
        recordList = []
        for pnt in pntGraph.nodes(data=True):
            rowList = [pnt[0][0], pnt[0][1]]
            for col in colList[2:]:
                rowList.append(pnt[1][col[0]])
            recordList.append(rowList)
            
        Point.new(shpPath, colList, recordList, (0,1))
            
        
    @staticmethod
    def new(shpPath, fields, records, geometryKey):
        """
        Method that creates a point shapefile
        
        type of shapefile - https://en.wikipedia.org/wiki/Shapefile
        
        Example - https://glenbambrick.com/2016/01/09/csv-to-shapefile-with-pyshp/
        
        Parameter
        ---------
        shpPath:    string
                    path of shapefile to handle    
    
        fields:     list of tuple
                    list of data fields
                    ex) [tuple(field name, type)]
        
        records:    list of tuple
                    dataset
                    ex) [(val11, val12, ...),(val21, val22, ...)]
    
        geometryKey:tuple
                    geometry keys, location of latitude and longitude in the records
                    ex) tuple(longitude, latitude) or tuple(x, y)
        """
        point_shp = shapefile.Writer(shapefile.POINT)
        point_shp.autoBalance = 1
        # =============================================================================
        # Because every shape must have a corresponding record it is critical that the
        # number of records equals the number of shapes to create a valid shapefile. To
        # help prevent accidental misalignment pyshp has an "auto balance" feature to
        # make sure when you add either a shape or a record the two sides of the
        # equation line up. This feature is NOT turned on by default. To activate it set
        # the attribute autoBalance to 1 (True)
        # =============================================================================
        
        for col in fields:
            if col[1] in C.TYPES_SHP.keys():
                if col[1] == 'float' or col[1] == "<class 'float'>":
                    point_shp.field(col[0][:10], C.TYPES_SHP[col[1]], decimal=8)
                else:
                    point_shp.field(col[0][:10], C.TYPES_SHP[col[1]])
            else:
                point_shp.field(col[0][:10], 'C')
        
                
        point_shp = Point._addRecords(point_shp, fields, records, geometryKey)
                             
        point_shp.save(shpPath)
        
        print('Shapefile successfully created!')
                
    
class Polyline():
    """
    Class for creating a shapefile of polyline data
    """
    
    @staticmethod
    def _addRecords(polyline_shp, polylineGraph, fields, records, geometryKey):
        """
        Private method to add records when creating a shapefile
        """
        for row, edge in zip(records, polylineGraph.edges(data=True)):
            if (row[geometryKey[0]] == -1 and row[geometryKey[1]] == -1) or (row[geometryKey[2]] == -1 and row[geometryKey[3]] == -1):
                pass
            else:
                polyline_shp.poly(parts=[edge[2]['coordinates']], shapeType=shapefile.POLYLINE)
                polyline_shp.record(*tuple([row[f] for f in range(len(fields))]))
            
        return polyline_shp
    
    
    @staticmethod
    def new(shpPath, polylineGraph, fields, records, geometryKey):
        """
        Method that creates a polyline shapefile
        
        type of shapefile - https://en.wikipedia.org/wiki/Shapefile
        
        Example - https://glenbambrick.com/2016/01/09/csv-to-shapefile-with-pyshp/
        
        Parameter
        ---------
        shpPath:        string
                        path of shapefile to handle
                    
        polylineGraph:  networkx graph
                        polyline type graph which including coordinates of vertices
    
        fields:         list of tuple
                        list of data fields
                        ex) [tuple(field name, type)]
        
        records:        list of tuple
                        dataset
                        ex) [(val11, val12, ...),(val21, val22, ...)]
    
        geometryKey:    tuple
                        geometry keys, location of two end nodes in the records
                        ex) tuple(tuple(longitude, latitude), tuple(longitude, latitude))
        """
        polyline_shp = shapefile.Writer(shapefile.POLYLINE)
        polyline_shp.autoBalance = 1
        # =============================================================================
        # Because every shape must have a corresponding record it is critical that the
        # number of records equals the number of shapes to create a valid shapefile. To
        # help prevent accidental misalignment pyshp has an "auto balance" feature to
        # make sure when you add either a shape or a record the two sides of the
        # equation line up. This feature is NOT turned on by default. To activate it set
        # the attribute autoBalance to 1 (True)
        # =============================================================================
        
        for col in fields:
            if col[1] in C.TYPES_SHP.keys():
                if col[1] == 'float' or col[1] == "<class 'float'>":
                    polyline_shp.field(col[0][:10], C.TYPES_SHP[col[1]], decimal=8)
                else:
                    polyline_shp.field(col[0][:10], C.TYPES_SHP[col[1]])
            else:
                polyline_shp.field(col[0][:10], 'C')
        
                
        polyline_shp = Polyline._addRecords(polyline_shp, polylineGraph, fields, records, geometryKey)
                             
        polyline_shp.save(shpPath)
        
        print('Shapefile successfully created!')
    
    
    @staticmethod
    def fromGraph(polylineGraph, shpPath):
        """
        Method that creates a polyline shapefile
        
        type of shapefile - https://en.wikipedia.org/wiki/Shapefile
                
        Parameters
        ----------
        polylineGraph:  neworkx.Graph
                        polyline type graph that includes edges information
        
        shpPath:        string
                        path of shapefile to handle
        """
    
        colList = [('X1', 'float'), ('Y1', 'float'), ('X2', 'float'), ('Y2', 'float')]
        for key, val in polylineGraph.edges(data=True)[0][2].items():
            colList.append((key, str(type(val))))
        
        recordList = []
        for edge in polylineGraph.edges(data=True):
            rowList = [edge[0][0], edge[0][1], edge[1][0], edge[1][1]]
            for col in colList[4:]:
                rowList.append(edge[2][col[0]])
            recordList.append(rowList)
            
        Polyline.new(shpPath, polylineGraph, colList, recordList, (0, 1, 2, 3))
    
class Projection():
    """
    Handles with projection related functions
    """
    def getWKT_PRJ(crsCode, crsType):
        """
        Method to get 'Human-Readable OGC WKT' type projection information from spatialreference.org
        
        This is utilized when creating .prj file
        
        Ex) https://glenbambrick.com/2015/08/09/prj/
    
        Parameters
        ----------
        crsCode:    int
                    coordinate reference system code
                    
        crsType:    string
                    'epsg' or 'sr-org'. The others can raise an error.
                    
        Return
        ------
        crsStr:     string
                    coordinate reference system in string
        """
        crsTypeDict = {'epsg':1, 'sr-org':2}
        i = crsTypeDict[crsType.lower()]
        if i == 1:
            # access projection information
            wkt = urllib.request.urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(crsCode))
        elif i == 2:
            wkt = urllib.request.urlopen("http://spatialreference.org/ref/sr-org/{0}/prettywkt/".format(crsCode))
        else:
            raise ValueError
            
        content=wkt.read().decode('utf-8')
        assert('Not found' not in content)
        # remove spaces between charachters
        remove_spaces = content.replace(" ","")
        # place all the text on one line
        remove_r = remove_spaces.replace("\r", "")
        crsStr = remove_r.replace("\n", "")
        return crsStr 
     
        
    def getPROJ4(crsCode, crsType):
        """
        Method to get 'Proj4' type projection information from spatialreference.org
        
        This is utilized when implementing project()
        
        The output is a dictionray which is standard crs form
        
        Parameters
        ----------
        crsCode:    int
                    coordinate reference system code
                    
        crsType:    string
                    'epsg' or 'sr-org'. The others can raise an error.
                    
        Return
        ------
        crsDict:    dictionary
                    coordinate reference system in dictionary type
        """
        crsTypeDict = {'epsg':1, 'sr-org':2}
        i = crsTypeDict[crsType.lower()]
        if i == 1:
            proj4 = urllib.request.urlopen("http://spatialreference.org/ref/epsg/{0}/proj4/".format(crsCode))
        elif i == 2:
            proj4 = urllib.request.urlopen("http://spatialreference.org/ref/sr-org/{0}/proj4/".format(crsCode))
        else:
            raise ValueError
            
        content = proj4.read().decode('utf-8')
        assert('Not found' not in content)
        
        crsDict = fiona.crs.from_string(content)
        return crsDict
    
    def copyCRS(shpPathFrom, shpPathTo):
        """
        Method for copying the crs of existing .prj file to another shp file
        
        Parameters
        ----------
        shpPathFrom: string
                     shp file path that you copies the crs from
                     
        shpPathTo:   string
                     shp file path to add the copied crs
        """
        shutil.copyfile('{}prj'.format(shpPathFrom[:-3]), '{}prj'.format(shpPathTo[:-3]))
        print('successfully copied the .prj file!')
    
    def defineProjection(shpPath, crsCode, crsType):
        """
        Method that creates a .proj file for shapefile
        
        Parameters
        ----------
        shpPath:    string
                    path of shapefile to handle    
                    
        crsCode:    int
                    coordinate reference system code
                    
        crsType:    string
                    'epsg' or 'sr-org'. The others can raise an error.
        """
        prjPath = '{}prj'.format(shpPath[:-3])
        prjDesc = Projection.getWKT_PRJ(crsCode, crsType)
        prj = open(prjPath, 'w+')
        prj.write(prjDesc)
        prj.close()
        
        print('.prj file successfully created!')
        
    def project(shpPath, crs, shpPathPrj):
        """
        Method to convert projection of a shapefile
        
        Parameters
        ----------
        shpfile:    string
                    path of input shapefile to convert the coordinate system
                    
        crs:        dictionary
                    a standard form of crs
                    
        path:       string
                    path of the output shapefile
        """
        data = gpd.read_file(shpPath)
        #get coordinate reference system of the current shp file
        currProj = data.crs
        
        data_proj = data.copy()
        # convert x, y values of dataset based on the crs provided from the input
        data_proj['geometry'] = data_proj['geometry'].to_crs(crs=crs)
        # conver crs of the shp file
        data_proj.crs = crs
        # svae the new shp file
        data_proj.to_file(shpPathPrj)
        print('The previous crs:{}\n Current crs:{}'.format(currProj, data_proj.crs))
