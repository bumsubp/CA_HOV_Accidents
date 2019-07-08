HOME = 'D:\\Cloud\\Dropbox (CSU Fullerton)\\_BPARK\\Spyder\\'

ROOT = HOME + 'HOV_Incidents_new\\'

BPSPATIAL = ROOT + 'BPSPATIAL\\'

RAW = ROOT + 'Incidents\\'
DIR_RECORD = 'all_text_chp_incidents_month_'
DIR_DETAIL = 'all_text_chp_incident_det_month_'
DIR_COLNAME = 'chp_incidents_month_column_names.xlsx'
SHEET_RECORD = 'CHP Incidents Month'
SHEET_DETAIL = 'CHP Incidents Month Detail'

ADMIN = ROOT+'data\\Admin_boundary\\'
STATE = 'tl_2017_us_state_CA\\tl_2017_us_state_CA.shp'
COUNTY = 'tl_2017_us_county_CA\\tl_2017_us_county_CA.shp'
DISTRICT = 'District_2016\\District_2016.shp'

INCIDENTS = ROOT+'data\\Incidents\\'

HIGHWAYS = ROOT+'data\\Highways\\'

STATIONS = ROOT+'data\\Stations\\'

 # =============================================================================
# field type
# N-numeric (decimal=)
# C-text (size=)
# L-boolean
# D-date
# =============================================================================
TYPES_SHP = {'str': 'C', 'float': 'N', 'int': 'N', 'boolean':'L', 'set': 'C', \
             "<class 'str'>":'C', "<class 'float'>" : 'N', "<class 'int'>":'N', \
             "<class 'bool'>": 'L'}

TYPES_EXCEL = {'int64': 'int', 'float64':'float', 'object':'str', 'bool':'bool'}


CRS_PRJ = [3311, 'epsg']
# NAD83(HARN) / California Albers
# http://spatialreference.org/ref/epsg/3311/

CRS_WGS84 = [4326, 'epsg']
#WGS 84 -- WGS84 - World Geodetic System 1984, used in GPS

CLR_WATER = 'lightskyblue'

CLR_EATRH = 'cornsilk'