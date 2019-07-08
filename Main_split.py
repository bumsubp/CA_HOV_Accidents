import BPSpatial.Constants as C
import CA_HOV_Accidents as IC
import sys
sys.path.append(C.BPSPATIAL)

import FileIO.SHP as SIO
import FileIO.Graph as GIO
import Analysis.Graph as AG

import copy

# =============================================================================
# Directories
# =============================================================================
# polyline
shpHOVPath = '{}CA_HOV_Access_prj.shp'.format(IC.HIGHWAYS)
intersectGraphPath = '{}CA_HOV_intersect.shp'.format(IC.HIGHWAYS)
splitByDistGraphPath = '{}CA_HOV_split_500m.shp'.format(IC.HIGHWAYS)
splitSjGraphPath = '{}CA_HOV_split_500m_line.shp'.format(IC.HIGHWAYS)


# projection
projFromPath = shpHOVPath

# Open shp file
hovGraph = GIO.Polyline.fromShapefile(shpHOVPath, ['Route', 'Direction', 'HwyId'])

# =============================================================================
# Intersect the graph
# =============================================================================
intersectGraph = AG.intersect.byGeometry(hovGraph)
# Save shp file
SIO.Polyline.fromGraph(intersectGraph, intersectGraphPath)
SIO.Projection.copyCRS(projFromPath, intersectGraphPath)

# =============================================================================
# Split the graph
# =============================================================================
splitByDistGraph = AG.split.byDistance(intersectGraph, 500)
SIO.Point.fromGraph(splitByDistGraph, splitByDistGraphPath)
SIO.Projection.copyCRS(projFromPath, splitByDistGraphPath)

# =============================================================================
# Spatial Join
# =============================================================================
## Data preprocessing for Direction and Ind of polyline shp file
# rename Ind field
#SIO.dbf.renameField(splitSjGraphPath, 'OBJECTID', 'edgeInd')
# Change values of Direction field
splitSjGraph = GIO.Polyline.fromShapefile(splitSjGraphPath, 'edgeInd Route Direction HwyId'.split(sep=' '))
dirConvertDict = {'NB':'N', 'SB':'S', 'EB':'E', 'WB':'W'}
for line in splitSjGraph.edges(data=True):
    direction = line[2]['Direction']
    if direction != None:
        line[2]['Direction'] = dirConvertDict[direction]
        
# open excel file and convert to shp file for changing projection
for year in range(2014, 2018+1):
    hovAccPath = '{}HOV_Accidents_{}.xlsx'.format(IC.INCIDENTS, year)
    hovAccGraph = GIO.Point.fromExcel(hovAccPath, 'Sheet1', [10, 9], header= 0, columns = [])
    
    # to avoid attribute error in severity column
    hovAccGraphCopy = copy.deepcopy(hovAccGraph)
    for ind, node in enumerate(hovAccGraph.nodes(data=True)):
        hovAccGraphCopy.node[node[0]]['Severity'] = str(node[1]['Severity'])
        hovAccGraphCopy.node[node[0]]['StatePM'] = str(node[1]['StatePM'])
    
    # Save shp file
    shpHOVAccPath = '{}HOV_Accidents_{}.shp'.format(IC.INCIDENTS, year)
    shpHOVAccPrjPath = '{}HOV_Accidents_{}_prj.shp'.format(IC.INCIDENTS, year)
    SIO.Point.fromGraph(hovAccGraphCopy, shpHOVAccPath)
    SIO.Projection.defineProjection(shpHOVAccPath, IC.CRS_WGS84[0], IC.CRS_WGS84[1])
    crs = SIO.Projection.getPROJ4(IC.CRS_PRJ[0], IC.CRS_PRJ[1])
    SIO.Projection.project(shpHOVAccPath, crs, shpHOVAccPrjPath)
    
    # Read the projection converted shp file
    hovAccPrjGraph = GIO.Point.fromShapefile(shpHOVAccPrjPath, 'Route Direction'.split(sep=' '))
    # Spatial join
    splitSjGraphCopy = copy.deepcopy(splitSjGraph)
    AG.spatialjoin.joincount(hovAccPrjGraph, splitSjGraphCopy, criterion='Direction', threshold=20)
    splitJoincountPath = '{}CA_HOV_split_500m_line_sj_{}.shp'.format(IC.HIGHWAYS, year)
    SIO.Polyline.fromGraph(splitSjGraphCopy, splitJoincountPath)
    SIO.Projection.copyCRS(projFromPath, splitJoincountPath)
    