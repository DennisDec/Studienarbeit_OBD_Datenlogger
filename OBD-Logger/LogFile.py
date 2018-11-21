# pylint: disable=no-member

import csv
import os
import datetime    
import mysql.connector
import env

from statistics import mean

from Signals import signals

# Für Raspberry bzw. Linux --> + "/Files/" Bei Windows: "\\OBD-Logger\\Files\\"
# "/Files/" #"\\OBD-Logger\\Files\\"
path = os.getcwd() + "\\OBD-Logger\\Files\\"
#path = "/home/pi/Schreibtisch/Studienarbeit_OBD_Datenlogger/OBD-Logger/Files/"

class LogStatus:
    """ Values for the Log status flags """
    NO_LOGFILE = "No LogFile"
    LOG_CREATED = "LogFile created"
    LOG_FILE_LOADED = "LogFile loaded from File"


class LogFile:
    """Class to log data from OBDII adapter"""

    @staticmethod
    def getFilenames():
        """returns a List of filenames"""
        return [f for f in os.listdir(path) if f.endswith('.csv')]

    def __init__(self):
        self._filename = ""
        self._data = {

        }

        for s in signals.getSignalList():    #Get OBD Signals
            # Fill Dictionary with Signals from Class Signals
            self._data[s.name] = []

        self._status = LogStatus.NO_LOGFILE

    def status(self):
        return self._status

    # TODO: header can be set inside this Class
    def createLogfile(self, filename):
        """Create logfile to track OBDII data"""
        try:
            with open(path+filename, 'w', newline='') as file:
                wr = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
                # Auto generate Header from signals in Signals.py
                header = [s.name for s in signals.getSignalList()]
                wr.writerow(header)
        except:
            print("Error! Creating File failed")

        self._filename = filename
        self._status = LogStatus.LOG_CREATED

    # TODO User List instead of single parameter
    def addData(self, signalList):
        """add data to buffer"""
        if(len(signals.getSignalList()) == len(signalList)):
            for i, s in enumerate(signals.getSignalList()):
                self._data[s.name].append(signalList[i])
        else:
            raise ValueError("Error: signalList has to have the same shape as signals.getSignalList()")

    def getLabelData(self, SupportedLabels):
        if (not self._status == LogStatus.LOG_FILE_LOADED):
            raise ValueError("Not allowed! You have to loadFromFile first")
        return self._data[SupportedLabels]

    def getTime(self):
        return self.getLabelData(signals.getTimeSignal().name)

    def getRelTime(self):
        tList = []
        timebuffer = self.getTime()

        for i in timebuffer:
            tList.append(round((datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S.%f") -
                                datetime.datetime.strptime(self._time[0], "%Y-%m-%d %H:%M:%S.%f")).total_seconds(), 2))
        return tList

    def getfilename(self):
        return self._filename

    def appendFile(self):
        """save buffered date in csv file"""
        if(not self._status == LogStatus.LOG_CREATED):
            raise ValueError("You have to create LogFile first!")

        try:
            with open(path+self._filename, 'a', newline='') as file:
                wr = csv.writer(
                    file, quoting=csv.QUOTE_MINIMAL, quotechar='"')

                for i in range(0, len(self._data["TIME"])):
                    buffer = []

                    for s in signals.getSignalList():
                        buffer.append(self._data[s.name][i])

                    wr.writerow(buffer)
        except:
            raise FileNotFoundError("Error!: Appending file failed")

        self._data.clear()
        for s in signals.getSignalList():
            # Fill Dictionary with Signals from Class Signals
            self._data[s.name] = []
        

    def loadFromFile(self, filename):
        """load data from csv file"""
        try:
            with open(path+filename, 'r') as csvfile:
                next(csvfile)  # ignore header (first row)
                fileReader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in fileReader:

                    for i, s in enumerate(signals.getSignalList()):
                        
                        if(row[i] == ""):
                            self._data[s.name].append(None)
                        else:
                            if(s.name == "TIME"):
                                self._data[s.name].append(row[i])
                            else:
                                self._data[s.name].append(float(row[i]))

        except:
            raise FileNotFoundError("Error: Loading File failed!")

        self._status = LogStatus.LOG_FILE_LOADED

    def transmitToSQL(self, filename):                      #Connecting to SQL Server
        db = mysql.connector.connect(
            user=env.DB_USER,
            password=env.DB_PASSWORD,
            host=env.DB_HOST,
            database=env.DB_NAME
        )



        #cursor.execute("SELECT * FROM importobd")
        cursor = db.cursor()
        
        # """load data from csv file"""
        # try:
        #     with open(path+filename, 'r') as csvfile:
        #         next(csvfile)  #ignore header (first row)
        #         fileReader = csv.reader(csvfile, delimiter=',', quotechar='"')
        #         for row in fileReader:
        #             print(row)
        #             sql = "INSERT INTO importobd (time, speed, rpm, engine_load, maf, temperature, pedal, afr, fuel_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        #             cursor.execute(sql, row)
        # except:
        #     raise FileNotFoundError("Error: Loading File failed!")

        # self._status = LogStatus.LOG_FILE_LOADED
        sql = "INSERT INTO importobd ("
        s = []
        for signal in signals.getSignalList():
            s.append(signal.db_name)
        sql += ", ".join(s)
        sql += ") VALUES ("
        tmp = []
        for i in range(len(s)):
            tmp.append("%s")
        sql += ", ".join(tmp)
        sql += ")"                    
        for i in enumerate(len(self._data["TIME"])):
            row = []
            for s in signals.getSignalList()):
                row.append(self._data[s.name][i])                
            cursor.execute(sql, row)
        db.commit()
        db.close()

    def getAverageData(self, signalStr):
        if (not self._status == LogStatus.LOG_FILE_LOADED):
            raise ValueError("Not allowed! You have to loadFromFile first")
        if not signals.containsSignalByString(signalStr):
            raise ValueError("Signal is not available!")
        
        L = self._data[signalStr]
        L = [x for x in L if x is not None]
        return mean(L)
     

    def getFuelConsumption(self):
        #Not working yet
        if (not self._status == LogStatus.LOG_FILE_LOADED):
            raise ValueError("Not allowed! You have to loadFromFile first")
        if not (signals.containsSignalByString("MAF")
                and signals.containsSignalByString("COMMANDED_EQUIV_RATIO")
                and signals.containsSignalByString("SPEED")):
            raise ValueError(
                "There are signals missing to calculate FuelConsumption")
        if not len(self._data[signals.MAF.name]) == len(self._data[signals.COMMANDED_EQUIV_RATIO.name]):
            raise ValueError("MAF list and AFR list don't have same shapes")
        FuelDensity = 0.775
        fuelcons = []
        maf = self._data[signals.MAF.name]
        afr = self._data[signals.COMMANDED_EQUIV_RATIO.name]
        speed = self._data[signals.SPEED.name]
        for i, v in enumerate(speed):
            if(afr[i] != 0 and v != 0): 
                fuelcons.append((maf[i]*3600)/(1000* 14.5*afr[i]* FuelDensity)* 100/(v))
            else:
                fuelcons.append(0)
            
        return fuelcons
