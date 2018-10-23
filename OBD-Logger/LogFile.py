import csv
import os
import datetime

path = os.getcwd() + "\\OBD-Logger\\Files\\" #Für Raspberry bzw. Linux --> + "/Files/"


class SupportedLabels:
    """All Labels which can be read"""
    SPEED = "SPEED"
    RPM = "RPM"
    ENGINE_LOAD = "ENGINE_LOAD"

class LogStatus:
    """ Values for the Log status flags """

    NO_LOGFILE = "No LogFile"
    LOG_CREATED = "LogFile created"
    LOG_FILE_LOADED = "LogFile loaded from File"

class LogFile:
    """Class to log Data from OBDII adapter"""

    @staticmethod
    def getFilenames():
        """returns a List of filenames"""
        return [f for f in os.listdir(path) if f.endswith('.csv')]

    def __init__(self):
        self._filename = ""
        self._time = []
        self._data = {
            SupportedLabels.SPEED : [],
            SupportedLabels.RPM : [],
        }
        self._status = LogStatus.NO_LOGFILE

    def status(self):
        return self._status

    def createLogfile(self, filename, headerCSV):
        try:
            with open(path+filename, 'w', newline='') as file:
                wr = csv.writer( file, quoting=csv.QUOTE_NONNUMERIC)
                wr.writerow(headerCSV)
        except:
            print("Error! Loading File")

        self._filename = filename
        self._status = LogStatus.LOG_CREATED


    def addData(self, time, speed, rpm):
            self._time.append(time)
            self._data[SupportedLabels.SPEED].append(speed)
            self._data[SupportedLabels.RPM].append(rpm)

    def getLabelData(self, SupportedLabels):
        if (not self._status == LogStatus.LOG_FILE_LOADED):
            raise ValueError("Not allowed! You have to loadFromFile first")
        return list(map(float, self._data[SupportedLabels])) #TODO Fehleingaben abfangen?
    
    def getTime(self):
        if (not self._status == LogStatus.LOG_FILE_LOADED):
            raise ValueError("Not allowed! You have to loadFromFile first")
        return self._time
        

    def getRelTime(self):
        if (not self._status == LogStatus.LOG_FILE_LOADED):
            raise ValueError("Not allowed! You have to loadFromFile first")
        tList = []
        timebuffer = self._time
        for i in timebuffer:
           tList.append(round((datetime.datetime.strptime(i,"%Y-%m-%d %H:%M:%S.%f") - datetime.datetime.strptime(self._time[1],"%Y-%m-%d %H:%M:%S.%f")).total_seconds(), 2))
        return tList

    def getfilename(self):
        return self._filename

    def appendFile(self):
        if(not self._status == LogStatus.LOG_CREATED):
            raise ValueError("Es wurde noch keine Datei geladen!")
       
        try:
            with open(path+self._filename, 'a', newline='') as file:
                wr = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC, quotechar='"')

                for i in range(0, len(self._time)):
                    buffer = []
                    buffer.append(self._time[i])
                    buffer.append(self._data[SupportedLabels.SPEED][i])
                    buffer.append(self._data[SupportedLabels.RPM][i])
                    wr.writerow(buffer)
        except:
            raise FileNotFoundError("Fehler beim erweitern der Datei")
        
        del self._time[:]       #delete time Array
        del self._data[SupportedLabels.SPEED][:]
        del self._data[SupportedLabels.RPM][:]


    def loadFromFile(self, filename):
        try:
            with open(path+filename, 'r') as csvfile:
                next(csvfile)   #Header wird ausgelassen
                fileReader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in fileReader:
                    self._time.append(row[0])
                    self._data[SupportedLabels.SPEED].append(row[1])
                    self._data[SupportedLabels.RPM].append(row[2])
        except:
            raise FileNotFoundError("Fehler beim Laden der Datei")

        self._status = LogStatus.LOG_FILE_LOADED 
        

