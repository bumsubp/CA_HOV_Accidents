import BPSpatial.Constants as C

import sys
sys.path.append(C.HOME)
sys.path.append(C.BPSPATIAL)

import FileIO.Graph as GIO
import FileIO.SHP as SIO
import Analysis.Graph as AG

pointShpPath = '{}\\Test\\testPoint2_UTM11N_near.shp'.format(C.BPSPATIAL)
polylineShpPath = '{}\\Test\\testNetwork2_UTM11N_prj.shp'.format(C.BPSPATIAL)

pointGraph = GIO.Point.fromShapefile(pointShpPath)
polylineGraph = GIO.Polyline.fromShapefile(polylineShpPath)

splitGraph = AG.split.splitLineAtPoint(polylineGraph, pointGraph, [('ID','int')])
splitShpPath = '{}\\Test\\testNetwork2_UTM11N_split.shp'.format(C.BPSPATIAL)
SIO.Polyline.fromGraph(splitGraph, splitShpPath)
crs = SIO.Projection.copyCRS(pointShpPath, splitShpPath)


len(splitGraph.edges(data=True))
len(splitGraph2.edges(data=True))

for i in splitGraph.edges(data=True):
    print(i)