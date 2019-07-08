import BPSpatial.Constants as C
import sys
sys.path.append(C.BPSPATIAL)

import FileIO.SHP as SIO
import FileIO.Graph as GIO
import FileIO.Excel as EIO
import Analysis.Graph as AG

from importlib import reload
reload(AG)

import pandas as pd

# =============================================================================
# FileIO.Graph
# =============================================================================
### 1. class Point
## 1) fromCsv
txtPath = '{}all_text_chp_incidents_month_2016_01.txt'.format(C.TEST)
txt = pd.read_csv(txtPath, header=None)

columns = [('Incident ID', 'int64'), \
           ('CC Code', 'object'), \
           ('IncidentNumber', 'int64'), \
           ('Timestamp', 'datetime64[ns]'), \
           ('Description', 'object'), \
           ('Location', 'object'), \
           ('Area', 'object'), \
           ('Zoom Map', 'float64'), \
           ('TB xy', 'float64'), \
           ('Latitude', 'float64'), \
           ('Longitude', 'float64'), \
           ('District', 'int64'), \
           ('County FIPS ID', 'int64'), \
           ('City FIPS ID', 'float64'),\
           ('Freeway Number', 'int64'), \
           ('Freeway Direction', 'object'), \
           ('State Postmile', 'float64'), \
           ('Absolute Postmile', 'float64'), \
           ('Severity', 'float64'), \
           ('Duration', 'int64]')]


txtGraph = GIO.Point.fromCsv(txtPath, geometryKey=(9, 10), columns=columns)


## 2) fromExcel
excPath = '{}test.xlsx'.format(C.TEST)
exc = pd.read_excel(excPath, 'Sheet1', header=None)
#testGra = GIO.Point.fromeExcel(excPath, 'Sheet1', (9,10))
#for pnt in testGra.nodes(data=True):
#    print(pnt)
    
    
## 3) fromShapefile
shpPointPath = '{}testPoint2_UTM11N.shp'.format(C.TEST)
shpPoint = GIO.Point.fromShapefile(shpPointPath, ['Id'])
#for s in shpPoint.nodes(data=True):
#    print(s)
    
### 2. Class Polyine
## 1) fromShapefile
shpPolylinePath = '{}testNetwork2_UTM11N.shp'.format(C.TEST)
shpPolyline = GIO.Polyline.fromShapefile(shpPolylinePath, ['Id'])
#for s in shpPolyline.edges(data=True):
#    print(s)
    
# =============================================================================
# FileIO.SHP
# =============================================================================
### 1. class dbf
shpPointPath1 = '{}testPoint2_UTM11N.shp'.format(C.TEST)
#SIO.dbf.dropFields(shpPointPath1, ['y'])
#SIO.dbf.renameField(shpPointPath1, 'x', 'xCoord')

### 2. class Point
## 1) fromGraph
shpPointPath2 = '{}testNetwork2_UTM11N_output.shp'.format(C.TEST)
shpPointPath2Prj = '{}testNetwork2_UTM11N_output_prj.shp'.format(C.TEST)
SIO.Point.fromGraph(shpPoint, shpPointPath2)
SIO.Projection.defineProjection(shpPointPath2, 26911, 'epsg')

## 3. class Polyline
## 1) fromGraph
shpPolylinePath1 = '{}testNetwork2_UTM11N.shp'.format(C.TEST)
shpPolylinePath1Prj = '{}testNetwork2_UTM11N_prj.shp'.format(C.TEST)
SIO.Polyline.fromGraph(shpPolyline, shpPolylinePath1)
SIO.Projection.defineProjection(shpPolylinePath1, 26911, 'epsg')

crs = SIO.Projection.getPROJ4(26911, 'epsg')
SIO.Projection.project(shpPolylinePath1, crs, shpPolylinePath1Prj)


# =============================================================================
# Analysis.Graph
# =============================================================================
### 1. class near
shpPointPath3 = '{}testPoint2_UTM11N.shp'.format(C.TEST)
shpPoint3 = GIO.Point.fromShapefile(shpPointPath3, ['Id'])
shpPolylinePath3 = '{}testNetwork2_UTM11N.shp'.format(C.TEST)
shpPolyline3 = GIO.Polyline.fromShapefile(shpPolylinePath3, ['Id'])

nearGraph = AG.near.pointOnPolyline(shpPolyline3, shpPoint3, threshold = 200)
nearGraphPath = '{}testPoint2_UTM11N_near.shp'.format(C.TEST)
SIO.Point.fromGraph(nearGraph, nearGraphPath)
SIO.Projection.defineProjection(nearGraphPath, 26911, 'epsg')

### 2. class split
## 1) byDistance
splitByDistGraph = AG.split.byDistance(shpPolyline3, 500)
splitByDistGraphPath = '{}testPoint2_UTM11N_split_byDistance.shp'.format(C.TEST)
SIO.Point.fromGraph(splitByDistGraph, splitByDistGraphPath)
SIO.Projection.defineProjection(splitByDistGraphPath, 26911, 'epsg')

## 2) splitLineAtPoint
splitByPointGraph = AG.split.splitLineAtPoint(shpPolyline3, nearGraph)
splitByPointGraphPath = '{}testPoint2_UTM11N_split_byPoints.shp'.format(C.TEST)
SIO.Polyline.fromGraph(splitByPointGraph, splitByPointGraphPath)
SIO.Projection.defineProjection(splitByPointGraphPath, 26911, 'epsg')

### 3. class intersect
intersectGraph = AG.intersect.byGeometry(shpPolyline3)
intersectGraphPath = '{}testPoint2_UTM11N_intersect.shp'.format(C.TEST)
SIO.Polyline.fromGraph(intersectGraph, intersectGraphPath)
SIO.Projection.defineProjection(intersectGraphPath, 26911, 'epsg')

### 4. class spatialjoin
AG.spatialjoin.nearest(shpPoint3, shpPolyline3, 200)
sjPntGraphPath = '{}testPoint2_UTM11N_sj.shp'.format(C.TEST)
SIO.Point.fromGraph(shpPoint3, sjPntGraphPath)
SIO.Projection.defineProjection(sjPntGraphPath, 26911, 'epsg')

AG.spatialjoin.joincount(shpPoint3, shpPolyline3, 200)
sjPlyGraphPath = '{}testPolyline2_UTM11N_sj.shp'.format(C.TEST)
SIO.Polyline.fromGraph(shpPolyline3, sjPlyGraphPath)
SIO.Projection.defineProjection(sjPlyGraphPath, 26911, 'epsg')

### 5. class interpolate
#centerPoints = []
#for edge in splitGraph.edges(data=True):
#    centerPoints.append(edge[2]['center'])
#centerGraph = GA.split.splitLineAtPoint(intersectGraph, centerPoints)
#
#kd = GA.interpolate.graphKDE(splitGraph, centerGraph, 500, kernel='gaussian', diverge=True)


