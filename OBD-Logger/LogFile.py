import csv
import os
import datetime    
import mysql.connector

# Für Raspberry bzw. Linux --> + "/Files/" Bei Windows: "\\OBD-Logger\\Files\\"
# "/Files/" #"\\OBD-Logger\\Files\\"
path = os.getcwd() + "/Files/"


class SupportedLabels:
    """All Labels which support logging funktion"""
    SPEED = "SPEED"
    RPM = "RPM"
    ENGINE_LOAD = "ENGINE_LOAD"
    MAF = "MAF"
    AMBIANT_AIR_TEMP = "AMBIANT_AIR_TEMP"
    RELATIVE_ACCEL_POS = "RELATIVE_ACCEL_POS"
    COMMANDED_EQUIV_RATIO = "COMMANDED_EQUIV_RATIO"
    FUEL_LEVEL = "FUEL_LEVEL"


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
        self._time = []
        self._data = {
            SupportedLabels.SPEED: [],
            SupportedLabels.RPM: [],
            SupportedLabels.ENGINE_LOAD: [],
            SupportedLabels.MAF: [],
            SupportedLabels.AMBIANT_AIR_TEMP: [],
            SupportedLabels.RELATIVE_ACCEL_POS: [],
            SupportedLabels.COMMANDED_EQUIV_RATIO: [],
            SupportedLabels.FUEL_LEVEL: [],

        }
        self._status = LogStatus.NO_LOGFILE

    def status(self):
        return self._status

    # TODO: header can be set inside this Class
    def createLogfile(self, filename, headerCSV):
        """Create logfile to track OBDII data"""
        try:
            with open(path+filename, 'w', newline='') as file:
                wr = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
                wr.writerow(headerCSV)
        except:
            print("Error! Loading File")

        self._filename = filename
        self._status = LogStatus.LOG_CREATED

    # TODO User List instead of single parameter
    def addData(self, time, speed, rpm, load, maf, temp, pedal, afr, fuel_lvl):
        """add data to buffer"""
        self._time.append(time)

        # TODO Use for-Loop
        self._data[SupportedLabels.SPEED].append(speed)
        self._data[SupportedLabels.RPM].append(rpm)
        self._data[SupportedLabels.ENGINE_LOAD].append(load)
        self._data[SupportedLabels.MAF].append(maf)
        self._data[SupportedLabels.AMBIANT_AIR_TEMP].append(temp)
        self._data[SupportedLabels.RELATIVE_ACCEL_POS].append(pedal)
        self._data[SupportedLabels.COMMANDED_EQUIV_RATIO].append(afr)
        self._data[SupportedLabels.FUEL_LEVEL].append(fuel_lvl)

    def getLabelData(self, SupportedLabels):
        if (not self._status == LogStatus.LOG_FILE_LOADED):
            raise ValueError("Not allowed! You have to loadFromFile first")
        return self._data[SupportedLabels]

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
            tList.append(round((datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S.%f") -
                                datetime.datetime.strptime(self._time[1], "%Y-%m-%d %H:%M:%S.%f")).total_seconds(), 2))
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
                    file, quoting=csv.QUOTE_NONNUMERIC, quotechar='"')

                for i in range(0, len(self._time)):
                    buffer = []
                    buffer.append(self._time[i])

                    # TODO: Use for-Loop instead
                    buffer.append(self._data[SupportedLabels.SPEED][i])
                    buffer.append(self._data[SupportedLabels.RPM][i])
                    buffer.append(self._data[SupportedLabels.ENGINE_LOAD][i])
                    buffer.append(self._data[SupportedLabels.MAF][i])
                    buffer.append(
                        self._data[SupportedLabels.AMBIANT_AIR_TEMP][i])
                    buffer.append(
                        self._data[SupportedLabels.RELATIVE_ACCEL_POS][i])
                    buffer.append(
                        self._data[SupportedLabels.COMMANDED_EQUIV_RATIO][i])
                    buffer.append(self._data[SupportedLabels.FUEL_LEVEL][i])
                    wr.writerow(buffer)
        except:
            raise FileNotFoundError("Error!: Appending file failed")

        # TODO Define LabelList and use for-Loop
        del self._time[:]
        del self._data[SupportedLabels.SPEED][:]
        del self._data[SupportedLabels.RPM][:]
        del self._data[SupportedLabels.ENGINE_LOAD][:]
        del self._data[SupportedLabels.MAF][:]
        del self._data[SupportedLabels.AMBIANT_AIR_TEMP][:]
        del self._data[SupportedLabels.RELATIVE_ACCEL_POS][:]
        del self._data[SupportedLabels.COMMANDED_EQUIV_RATIO][:]
        del self._data[SupportedLabels.FUEL_LEVEL][:]

    def loadFromFile(self, filename):
        """load data from csv file"""
        try:
            with open(path+filename, 'r') as csvfile:
                next(csvfile)  #ignore header (first row)
                fileReader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in fileReader:
                    self._time.append(row[0])
                    self._data[SupportedLabels.SPEED].append(float(row[1]))
                    self._data[SupportedLabels.RPM].append(float(row[2]))
                    self._data[SupportedLabels.ENGINE_LOAD].append(
                        float(row[3]))
                    self._data[SupportedLabels.MAF].append(float(row[4]))
                    self._data[SupportedLabels.AMBIANT_AIR_TEMP].append(
                        float(row[5]))
                    self._data[SupportedLabels.RELATIVE_ACCEL_POS].append(
                        float(row[6]))
                    self._data[SupportedLabels.COMMANDED_EQUIV_RATIO].append(
                        float(row[7]))
                    self._data[SupportedLabels.FUEL_LEVEL].append(
                        float(row[8]))
        except:
            raise FileNotFoundError("Error: Loading File failed!")

        self._status = LogStatus.LOG_FILE_LOADED

    def transmitToSQL(self, filename):
        db = mysql.connector.connect(
            user='root',
            password='OBD2',
            host='192.168.2.113',
            database='obd/gps-datenlogger'
        )
        #cursor.execute("SELECT * FROM importobd")
        cursor = db.cursor()
        """load data from csv file"""
        try:
            with open(path+filename, 'r') as csvfile:
                next(csvfile)  #ignore header (first row)
                fileReader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in fileReader:
                    print(row)
                    sql = "INSERT INTO importobd (time, speed, rpm, engine_load, maf, temperature, pedal, afr, fuel_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, row)
        except:
            raise FileNotFoundError("Error: Loading File failed!")

        self._status = LogStatus.LOG_FILE_LOADED   
        db.commit()
        db.close()

    def getAverageData(self):
        if (not self._status == LogStatus.LOG_FILE_LOADED):
            raise ValueError("Not allowed! You have to loadFromFile first")
        # TODO return average value of data-Array

    # TODO Add method: getAverageFuelConsumption() and return Value
