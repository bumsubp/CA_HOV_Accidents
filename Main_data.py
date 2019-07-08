import sys
import CA_HOV_Accidents.Constants as C
sys.path.append(C.HOME)
sys.path.append(C.ROOT)
sys.path.append(C.BPSPATIAL)

import pickle

import FileIO.SHP as SIO
import FileIO.Graph as GIO
import FileIO.Excel as EIO
import Analysis.Graph as AG

import Incidents as Incidents

import copy

from importlib import reload
reload(EIO)

# =============================================================================
# 1. Data Preparation
#   Input: 
#       1) Incidents .txt file - the PeMS Incidents .txt file 
#       2) Hwy HOV split shpfile - hwy segements split by stations
#   Output: 
#       1-1) hovAccPrjPath - HOV accident .shp file
#       1-2) hovAccGraph - networkx point type graph
#       2) hwyHOVSplitGraph - Hwy HOV split networkx graph
# =============================================================================

year = set([yr for yr in range(2014,2018+1)])
month = set([mon for mon in range(1,13)])

yyyymm = set([(yr, mon) for yr in year
                        for mon in month])

for yr in sorted(year):
    hovAccDict={}    
    for mon in sorted(month):
        print(yr, mon)
        ## Paths
        hovAccPath = '{}HOV_Accidents_{}_{:02}.shp'.format(C.INCIDENTS, yr, mon)
        hovAccPrjPath = '{}HOV_Accidents_{}_{:02}_prj.shp'.format(C.INCIDENTS, yr, mon)
        hwyHOVSplitPath = '{}_03_2_CA_HOV_All_split_by_station_arcmap.shp'.format(C.HIGHWAYS)
        
        ## Projection
        crsPrj = SIO.Projection.getPROJ4(C.CRS_PRJ[0], C.CRS_PRJ[1])
        
        # Load an incident file
        inc = Incidents.Incidents(yr, mon)
        
        # Extract HOV Accidents
        hovAcc = inc.getHovAccident()
        
        # Construct column name list (nested list)
        # Due to the length limit of column name in ArcMap, take only first 10 characters
        colNames = [[val[0][:10], val[1]] for val in inc.colRecordDict.values()]
         
        # Construct dataset list (nested list)
        hovAccList = Incidents.nestedDictToList(hovAcc)
        
        # Create shp file
        SIO.Point.new(hovAccPath, colNames, hovAccList, (10, 9))
        SIO.Projection.defineProjection(hovAccPath, C.CRS_WGS84[0], C.CRS_WGS84[1])
        SIO.Projection.project(hovAccPath, crsPrj, hovAccPrjPath)
        
        # HOV accident graph
        hovAccAttrs = 'IncId Route Direction'.split(sep= ' ')
        hovAccGraph = GIO.Point.fromShapefile(hovAccPrjPath, attrs=hovAccAttrs)
        
        # hwy split graph
        hwyHOVSplitAttrs = 'Route Direction'.split(sep= ' ')
        hwyHOVSplitGraph = GIO.Polyline.fromShapefile(hwyHOVSplitPath, attrs=hwyHOVSplitAttrs)
        
        # modify the column, Direction, of hwyHOVSplitGraph to ensure the two graphs have the identical values
        # NB-> N / SB->S / EB - E / WB - W
        dirConvertDict = {'NB':'N', 'SB':'S', 'EB':'E', 'WB':'W'}
        for line in hwyHOVSplitGraph.edges(data=True):
            direction = line[2]['Direction']
            if direction != None:
                line[2]['Direction'] = dirConvertDict[direction]
            
        # =============================================================================
        # 2. Matching HOV accidents to split HOV semgents
        #   Input: 
        #       1) hovAccGraph - HOV accidents in point type networkx graph
        #       2) hwyHOVSplitGraph - split HOV segments in polyline type networkx graph
        #   Output: 
        #       1) hovAccGraph
        # =============================================================================
        
        # spatial joint
        AG.spatialjoin.nearest(hovAccGraph, hwyHOVSplitGraph, criterion='Direction', threshold = 30)
        
        # =============================================================================
        # 3. Join attributes of Accidents and hwy segments defined in Highway.py
        #   Input: 
        #       1) hovAccGraph - HOV accidents in point type networkx graph
        #       2) hwySplitOrderedDict.p - nested dictionary of ordered segment of HOV facilites
        #           {(Route, Direction, HwyId): [(edge[0], edge[1], edge[2])]}
        #   Output: 
        #       1) hovAccGraphCopy
        # =============================================================================
        
        # Open ordered hwy split segments dictionary in pickle
        hwySplitOrderedDictPickle = pickle.load(open('{}hwySplitOrderedDict.p'.format(C.HIGHWAYS), 'rb'))
        
        # define a new dictionary for efficient join
        hwySplitOrderedDict = {} # {edgeInd: [(edge[0], edge[1], edge[2])]}
        for routeDirValList in hwySplitOrderedDictPickle.values():
            for edge in routeDirValList:
                hwySplitOrderedDict[edge[2]['Ind']] = edge
                
        # join attributes
        hovAccGraphCopy = hovAccGraph.copy()
        for acc in hovAccGraphCopy.nodes(data=True):
            sta1 = 'station1_ID'
            sta2 = 'station2_ID'
            nearEdge = acc[1]['nearEdge']
            acc[1][sta1] = -1
            acc[1][sta2] = -1
            
            if nearEdge in hwySplitOrderedDict.keys():
                acc[1][sta1] = hwySplitOrderedDict[nearEdge][2][sta1]
                acc[1][sta2] = hwySplitOrderedDict[nearEdge][2][sta2]
                
        # =============================================================================
        # 4. Construct an excel file using graph variables
        #   Input: 
        #       1) hovAccGraphCopy - HOV accidents in point type networkx graph
        #   Output: 
        #       1) HOV_Accidents_Station_yyyy_mm.xlsx
        # =============================================================================
        #hovAccStationsExcelPath = '{}HOV_Accidents_Station_{}_{:02}.xlsx'.format(C.INCIDENTS, yr, mon)
        #EIO.pointGraph_to_xlsx(hovAccGraphCopy, hovAccStationsExcelPath, 'Sheet1')
        
        # =============================================================================
        # 4.(alternative) Construct an excel file which includes accident info and near stations
        #   Input: 
        #       1) hovAcc - nested dictionary of HOV accident 
        #       2) colNames - column names of the hovAcc dictionary except for its key (incId)
        #       3) hovAccGraphCopy - HOV accidents in point type networkx graph
        #   Output: 
        #       1) HOV_Accidents_Station_yyyy_mm.xlsx
        # =============================================================================
        
    #    hovAccStationsExcelPath = '{}HOV_Accidents_Station_{}_{:02}.xlsx'.format(C.INCIDENTS, yr, mon)
        
        hovAccCopy = copy.deepcopy(hovAcc)
        hovAccColNames = copy.deepcopy(colNames)
        hovAccColNames = [col[0] for col in hovAccColNames]
        
        hovAccColNames.append('Inc_X') # add column to add which is same to the key in the point graph data
        hovAccColNames.append('Inc_Y')
        hovAccColNames.append('station1_ID') 
        hovAccColNames.append('station2_ID')
        
        hovAccKeys=[29, 30, 31, 32] # key of the nested dictionary
        
        for point in hovAccGraphCopy.nodes(data=True):
            try:
                hovAccCopy[point[1]['IncId']][hovAccKeys[0]] = point[0][0]
                hovAccCopy[point[1]['IncId']][hovAccKeys[1]] = point[0][1]
                hovAccCopy[point[1]['IncId']][hovAccKeys[2]] = point[1]['station1_ID']
                hovAccCopy[point[1]['IncId']][hovAccKeys[3]] = point[1]['station2_ID']
            except:
                pass
            
        hovAccDict.update(hovAccCopy)
    
    hovAccStationsExcelPath = '{}HOV_Accidents_{}.xlsx'.format(C.INCIDENTS, yr)
    EIO.nestedDict_to_xlsx(hovAccDict, hovAccStationsExcelPath, 'Sheet1', hovAccColNames)
