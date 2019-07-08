import pandas as pd
import copy
import math
import sys
import datetime, pytz, time

import HOV_Incidents_new.Constants as C
sys.path.append(C.HOME)
                
def getDigit(num):
    """
    Method that gets the number of digit of a number
    
    Parameters
    ----------
    
    num         : float
                  a number for getting the number of digit
                  
    Return
    ------
    count       : int
                  the number of digtis
    """
    count = 0
    while (num > 0):
        num = num//10
        count+=1
    return count


def nestedDictToList(nestedDict):
    """
    Method that converts a double dictionary to a list
    
    Parameters
    ----------
    
    nestedDict     : dictionary
                     in this project,
                     a nested dictionary {Incident Id : {column Name : value}}
                     
    Return
    ------
    outputList     : nested list
                     converted list
    """
    outputList = []
    for key1, val1 in nestedDict.items():
        rowList = [key1]
        for key2, val2 in val1.items():
            if key2 == 20: # For the detail message, it converts set type to string
                rowList.append(str(val2))
            else: # otherwise, it takes its own type
                rowList.append(val2)
        outputList.append(rowList)
    return outputList


def getUnixTime(timeList):
    """
    Method that gets unix time in PST from a form of list
    ex) UTC - 8 hours in the daylight saving period (7 hours otherwise)
    
    Parameters
    ----------
    
    timeList       : list [yyyy, mm, dd, hh, mm, ss]
    
    """
    pacific = pytz.timezone('US/Pacific')
    utc = pytz.timezone('UTC')
    pacific_dt = pacific.localize(datetime.datetime(timeList[0], timeList[1], timeList[2], timeList[3], timeList[4], timeList[5]))
    utc_dt = utc.localize(datetime.datetime(timeList[0], timeList[1], timeList[2], timeList[3], timeList[4], timeList[5]))
    utcUnix = time.mktime(utc_dt.timetuple())
    gap = (pacific_dt - utc_dt).seconds
    return int(utcUnix - gap)
    

class Data():
    """
    Data preparation. Opens CHP incidents files in txt. format provided by PeMS.
    Generates a set of dictionary variables of field names and datasets.
    This class is inherited by Incidents class.
    
    Parameters
    ----------
    
    year:               float
                        year of interest
    
    month:              float
                        month of interest
                        
    Attributes
    ----------
                
    colNameFileRecord:  Pandas.Dataframe
                        meta information of the incident data
                        
    colNameFileDetail:  Pandas.Dataframe
                        meta information of the incident detailed data
                        
    dataFileRecord:     Pandas.Dataframe
                        dataset of incidents (yyyy_mm)
    
    dataFileDetail:     Pandas.Dataframe
                        dataset of detailed incidents (yyyy_mm)
                        
    colRecordDict:      dictionary
                        meta information of the incident data
                        {column index: tuple(column name, type)}
    
    colDetailDict:      dictionary 
                        meta information of the incident detailed data
                        {column index: tuple(column name, type)}
                        
    dataRecordDict:     dictionary
                        dataset of incidents (yyyy_mm)
                        {incident_id(float):{column index : value}}
                        
    dataDetailDict:     dictionary
                        dataset of detailed incidents (yyyy_mm)
                        {incident_id(float):{column index : value}}
    
    keyRecordSet:       set
                        unique set of incident_id's
    
    keyDetailSet:       set
                        unique set of detail_id's
    """
    
    def __init__(self, year, month):
        self.year = year
        self.month = month
        
        self.colNameFileRecord, self.colNameFileDetail = self._openColName()
        self.dataFileRecord, self.dataFileDetail = self._openData()
        

        self.colRecordDict, self.colDetailDict  = self._getColumNames()
        
        
        self.dataRecordDict= self._getDataRecordDict(self.dataFileRecord)
        self.keyRecordSet = set(key for key in self.dataRecordDict) # time complexity - contain, remove O(1)
        
        self.dataDetailDict = self._getDataDetailDict(self.dataFileDetail)
        self.keyDetailSet = set(key for key in self.dataDetailDict)
        
        self._setDetailId()
        self._setHov()
        self._setType()
        self._setTime()
        
    
    def _getColumNames(self):
        colRecord = list(self.colNameFileRecord[0])
        colDetail = list(self.colNameFileDetail[0])
        
        typeRecord = list(self.colNameFileRecord[2])
        typeDetail = list(self.colNameFileDetail[2])
        
        colRecordDict = {ind:(col, ty) for ind, col, ty in zip(self.dataFileRecord,colRecord, typeRecord)}
        colDetailDict = {ind:(col, ty) for ind, col, ty in zip(self.dataFileDetail,colDetail, typeDetail)}
        
        return colRecordDict, colDetailDict


    def _openColName(self):
        colNameRecord = pd.read_excel(C.RAW+C.DIR_COLNAME, \
                                      sheet_name = C.SHEET_RECORD, header=None)
        colNameDetail = pd.read_excel(C.RAW+C.DIR_COLNAME, \
                                      sheet_name = C.SHEET_DETAIL, header=None)
        return colNameRecord, colNameDetail
    
    
    def _openData(self):
        
        dataRecord_txt = pd.read_csv('{}{}\\{}{}_{:02}.txt'.format(\
                                     C.RAW, self.year, C.DIR_RECORD, self.year, self.month), header=None)
        dataDetail_txt = pd.read_csv('{}{}\\{}{}_{:02}.txt'.format(\
                                     C.RAW, self.year, C.DIR_DETAIL, self.year, self.month), header=None)
        return dataRecord_txt, dataDetail_txt


    def _getDataRecordDict(self, dataFileRecord):
            dataRecordDict = {}
            for row in dataFileRecord.values:
                rowDict = {}
                rowList = list(row)
                for ind, val in enumerate(rowList): 
                    if ind != 0: # except record id
                        if type(val) == float and math.isnan(val):
                            val=-1
                        rowDict[ind] = val
                dataRecordDict[rowList[0]] = rowDict
            return dataRecordDict

    def _getDataDetailDict(self, dataFileDetail):
        dataDetailDict = {}
        for row in dataFileDetail.values:
            rowDict = {}
#            if row[0][:8].isdigit(): # check if the first 8 characters are numbers
            if type(row[0]) == str:
                if row[0].isdigit():
                    if getDigit(int(row[0])) == 8: # check if the first value is 8-digit number
                        rowList = list(row)
                        for ind, val in enumerate(rowList):
                            if ind != 1: # except for detail id
                                rowDict[ind] = val
                        dataDetailDict[rowList[1]] = rowDict
            elif type(row[0]) == float:
                if not math.isnan(row[0]):
                    if getDigit(int(row[0])) == 8: # check if the first value is 8-digit number
                            rowList = list(row)
                            for ind, val in enumerate(rowList):
                                if ind != 1: # except for detail id
                                    rowDict[ind] = val
                            dataDetailDict[rowList[1]] = rowDict
        return dataDetailDict

    
    def _matchingDetailMessage(self):
        copyKeyRecordSet = copy.deepcopy(self.keyRecordSet)
        keyRecordDetailDict = {}
        for key, valDict in self.dataDetailDict.items():
            keyRec = valDict[0]
            keyDet = key
            if int(keyRec) in copyKeyRecordSet: # check if the key exists in the dictionary
                keyRecordDetailDict[int(keyRec)] = set([int(keyDet)])
                copyKeyRecordSet.remove(int(keyRec))
            else:
                if int(keyRec) in self.keyRecordSet: # check if the key exists in record data
                    keyRecordDetailDict[int(keyRec)].add(int(keyDet))
        return keyRecordDetailDict

    def _setDetailId(self):
        keyRecordDetailDict = self._matchingDetailMessage()
        detail_id = 20
        self.colRecordDict[detail_id] = ('detail_id', 'set')
        for key in self.keyRecordSet:
            self.dataRecordDict[key][detail_id] = ''
        for key, val in keyRecordDetailDict.items():
            self.dataRecordDict[key][detail_id] = val 

    def _setHov(self):
        hov = 21
        self.colRecordDict[hov] = ('hov', 'boolean')
        hovSet = set([int(rec[0]) for rec in self.dataDetailDict.values() if 'hov' in str(rec[3]).lower()])
        hovSet1 = set([key for key, rec in self.dataRecordDict.items() if 'hov' in str(rec[5]).lower()])
        
        for hov1 in hovSet1:
            hovSet.add(hov1)
        
        for key in self.keyRecordSet:
            if key in hovSet:
                self.dataRecordDict[key][hov] = True
            else:
                self.dataRecordDict[key][hov] = False        
        # A gap exists between # of incident keys in record and detailed datasets.
        # The record dataset cannot fully cover the cases of the detailed dataset.
        
    def _setType(self): 
        accident = 22
        hazard = 23
        self.colRecordDict[accident] = ('accident', 'boolean')
        self.colRecordDict[hazard] = ('hazard', 'boolean')
        
        accidentCodes = set('1179 1180 1181 1182 1183 2000'.split(sep= ' '))
        hazardCodes = set('1125'.split(sep= ' '))
        for key, val in self.dataRecordDict.items():
            if val[4][:4] in accidentCodes:
                self.dataRecordDict[key][accident] = True
                self.dataRecordDict[key][hazard] = False
            elif val[4][:4] in hazardCodes:
                self.dataRecordDict[key][accident] = False
                self.dataRecordDict[key][hazard] = True
            else:
                self.dataRecordDict[key][accident] = False
                self.dataRecordDict[key][hazard] = False
                
    def _setTime(self):
        year = 24
        month = 25
        day = 26
        hour = 27
        unixTime = 28
        
        self.colRecordDict[year] = ('year', 'int')
        self.colRecordDict[month] = ('month', 'int')
        self.colRecordDict[day] = ('day', 'int')
        self.colRecordDict[hour] = ('hour', 'int')
        self.colRecordDict[unixTime] = ('unixTime', 'int') # in PST/ You have to add 28800(or 25200) to get UTC
        
        for key, val in self.dataRecordDict.items():
            timeList = self._splitTime(val[3])
            self.dataRecordDict[key][year] = timeList[0]
            self.dataRecordDict[key][month] = timeList[1]
            self.dataRecordDict[key][day] = timeList[2]
            self.dataRecordDict[key][hour] = timeList[3]
            
            # in case of invalid time
            if timeList == [-1] * 6:
                self.dataRecordDict[key][unixTime] = -1
            else:
                self.dataRecordDict[key][unixTime] = getUnixTime(timeList)
            
        
    def _splitTime(self, time):
        try:
            timeList = time.split(' ')
        except:
            mmddyyyy = [-1, -1, -1]
            hhmmss = [-1, -1, -1]
        else:
            mmddyyyy = timeList[0].split('/')
            hhmmss = timeList[1].split(':')
        
        return [int(mmddyyyy[2]), int(mmddyyyy[0]), int(mmddyyyy[1]), int(hhmmss[0]), int(hhmmss[1]), int(hhmmss[2])]
    
    
class Incidents(Data):
    """
    Filters, massages incidents data imported by the Data class.
    
    Parameters
    ----------
    
    year:               float
                        year of interest
    
    month:              float
                        month of interest
                        
    Attributes
    ----------
    
    Inherited from _Data class
    """    
    
    def __init__(self, year, month):
        Data.__init__(self, year, month)
    
    def getRecords(self, incType='All', facilType='All'):
        
        incTypeList = ['accident', 'hazard', 'others', 'all']
        facilTypeList = ['hov', 'ml', 'all']
        
        assert(incType.lower() in incTypeList and facilType.lower() in facilTypeList)
        
        # 21 - hov / 22 - accident / 23 - hazard => 12 combinations
        if facilType.lower() == 'all' and incType.lower() == 'all':
            return self.dataRecordDict
        elif facilType.lower() == 'all' and incType.lower() == 'accident':
            return {key:val for key, val in self.dataRecordDict.items() if val[22] == True}
        elif facilType.lower() == 'all' and incType.lower() == 'hazard':
            return {key:val for key, val in self.dataRecordDict.items() if val[23] == True}
        elif facilType.lower() == 'all' and incType.lower() == 'others':
            return {key:val for key, val in self.dataRecordDict.items() if val[22] == False and val[23] == False}
        
        elif facilType.lower() == 'hov' and incType.lower() == 'all':
            return {key:val for key, val in self.dataRecordDict.items() if val[21] == True}
        elif facilType.lower() == 'hov' and incType.lower() == 'accident':
            return {key:val for key, val in self.dataRecordDict.items() if val[21] == True and val[22] == True}
        elif facilType.lower() == 'hov' and incType.lower() == 'hazard':
            return {key:val for key, val in self.dataRecordDict.items() if val[21] == True and val[23] == True}
        elif facilType.lower() == 'hov' and incType.lower() == 'others':
            return {key:val for key, val in self.dataRecordDict.items() if val[21] == True and val[22] == False and val[23] == False}
        
        elif facilType.lower() == 'ml' and incType.lower() == 'all':
            return {key:val for key, val in self.dataRecordDict.items() if val[21] == False}
        elif facilType.lower() == 'ml' and incType.lower() == 'accident':
            return {key:val for key, val in self.dataRecordDict.items() if val[21] == False and val[22] == True}
        elif facilType.lower() == 'ml' and incType.lower() == 'hazard':
            return {key:val for key, val in self.dataRecordDict.items() if val[21] == False and val[23] == True}
        elif facilType.lower() == 'ml' and incType.lower() == 'others':
            return {key:val for key, val in self.dataRecordDict.items() if val[21] == False and val[22] == False and val[23] == False}
        
    def getHovAccident(self):
        """
        Method that gets hov accidents in dictionary type
        """
        return {key:val for key, val in self.dataRecordDict.items() if val[21] == True and val[22] == True}
    
    def getHovHazard(self):
        """
        Method that gets hov hazards in dictionary type
        """
        return {key:val for key, val in self.dataRecordDict.items() if val[21] == True and val[23] == True}
    
    def getHovEtc(self):
        """
        Method that gets hov incidents except for accidents and hazards in dictionary type
        """
        return {key:val for key, val in self.dataRecordDict.items() if val[21] == True and val[22] == False and val[23] == False}
    
    
    
if __name__== "__main__":
    pass
    year = 2017
    month = 12
    
    accident_all_dict = {}
    for month in range(1,13):
        test = Incidents(year, month)
        accident_all = test.getRecords('Accident', 'All')
        accident_all_dict.update(accident_all)
        
    acci_all_df = pd.DataFrame(accident_all_dict).transpose()
    acci_all_df_path = '{}Accidents_{}.csv'.format(C.ROOT, year)
    acci_all_df.to_csv(acci_all_df_path)
    
    
