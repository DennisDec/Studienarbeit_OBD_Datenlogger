# pylint: disable=no-member

import csv
import os
import datetime    
import mysql.connector
import env
import os
import subprocess
import socket
import json

from statistics import mean

from Signals import signals

# Fuer Raspberry bzw. Linux --> + "/Files/" Bei Windows: "\\OBD-Logger\\Files\\"
# "/Files/" #"\\OBD-Logger\\Files\\"
path = env.PATH #"\\OBD-Logger\\Files\\" # 
#path = "/home/pi/Studienarbeit_OBD_Datenlogger/OBD-Logger/Files/"

class LogStatus:
    """ Values for the Log status flags """
    NO_LOGFILE = "No LogFile"
    LOG_CREATED = "LogFile created"
    LOG_FILE_LOADED = "LogFile loaded from File"

class Stringbuilder:

    @staticmethod
    def SqlBuidler(tableName):
        """ 
        Creates a string with SQL INSTERT command to load all measurements to a sql table 

        """

        #TODO: Call different getSignalList()-method, depending on tableName!
        sql = "INSERT INTO " + str(tableName) + "("
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
        return sql

    @staticmethod
    def SqlAddEntry(filename):
        """
        Create query string to load new file to db
        """
        sql = "INSERT INTO  data ( filename ) VALUES ('" + str(filename) + "\')"
        
        return sql


class LogFile:
    """Class to log data from OBDII adapter"""

    @staticmethod
    def getFilenames():
        """returns a List of filenames which are located in path """
        return [f for f in os.listdir(path) if f.endswith('.csv')]

    @staticmethod
    def transferToJson(filename):
        jsonPath = path + "JSON/"
        with open(path +filename, 'r') as csvfile:
            next(csvfile)
            fileReader = csv.DictReader(csvfile, fieldnames=("TIME", "SPEED", "RPM", "ENGINE_LOAD", "MAF" ,"AMBIANT_AIR_TEMP", "RELATIVE_ACCEL_POS", "COMMANDED_EQUIV_RATIO","FUEL_LEVEL" ,"GPS_Long", "GPS_Lat"))
            out = json.dumps( [ row for row in fileReader ] ) 
            f = open( jsonPath + filename.split(".csv")[0] + ".json", 'w')  
            f.write(out)
            return filename.split(".csv")[0] + ".json"    

    @staticmethod
    def copyFileToServer(filename):
        errcnt = 0
        ip = []
        f = open("ipAddress.ip", "r")
        ipAddress = f.read()
        if(not ipAddress == ""):
            stri = str(subprocess.check_output(('nmap -p22 ' + str(ipAddress.IP)), shell=True))
            if(stri.find("open") != -1):
                ip.append(str(ip))
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 1))
            own_ip = str(s.getsockname()[0])

            ip_mask = ".".join(own_ip.split('.')[0:-1]) + ".*"

            stri = str(subprocess.check_output(('nmap -p22 ' + str(ip_mask)), shell=True))
            output = stri.split("\\n")

            for i, line in enumerate(output):
                if(line.find("open") != -1 and output[i-3].split(' ')[-1] != own_ip):
                    ip.append(output[i-3].split(' ')[-1])
                    print(ip)


        for i, tmp in enumerate(ip):
            #os.system("sshpass -p '" + str(env.DB_PASSWORD) + "' scp " + str(path) + "JSON/" + str(filename) + " pi@" + str(ip[i]) + ":datafiles/")
            try:
                subprocess.check_output(("sshpass -p '" + str(env.DB_PASSWORD) + "' scp " + str(path) + "JSON/" + str(filename) + " pi@" + str(ip[i]) + ":datafiles/"), shell=True)
                LogFile.transmitToSQL(filename, str(ip[i]))
                f = open("ipAddress.ip", "w")
                f.write("IP = '" + str(ip[i]) + "'")


                return True
            except subprocess.CalledProcessError:
                errcnt = errcnt + 1
                if(len(ip)-1  == i):
                    return False
                pass


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

    def getDataDict(self):
        return self._data

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

    def addData(self, signalList):
        """add data to buffer"""
        if(len(signals.getSignalList()) == len(signalList)):
            for i, s in enumerate(signals.getSignalList()):
                if(s.name == "TIME" or signalList[i] == None):
                    self._data[s.name].append(signalList[i])
                else:
                    self._data[s.name].append(round(float(signalList[i]),s.roundDigit))
        else:
            raise ValueError("Error: signalList has to have the same shape as signals.getSignalList()")

    def getLabelData(self, labelName):
        """
            returns measurement data by labelName. Call loadFrimFile() first
        """
        if (not self._status == LogStatus.LOG_FILE_LOADED):
            raise ValueError("Not allowed! You have to loadFromFile first")
        return self._data[labelName]

    def getTime(self):
        """ 
            returns time array  
        """
        return self.getLabelData(signals.getTimeSignal().name)

    def getRelTime(self):
        """
            returns relative time array in second based on the start time
        """

        tList = []
        timebuffer = self.getTime()

        for i in timebuffer:
            tList.append(round((datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S.%f") -
                                datetime.datetime.strptime(self._data[signals.TIME.name][0], "%Y-%m-%d %H:%M:%S.%f")).total_seconds(), 2))
        return tList

    def getfilename(self):
        """
            returns the current fileName
        """

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
                                self._data[s.name].append(round(float(row[i]),s.roundDigit))

        except:
            raise FileNotFoundError("Error: Loading File failed!")
        self._filename = filename
        self._status = LogStatus.LOG_FILE_LOADED

    @staticmethod
    def transmitToSQL(filename, ip):                      #Connecting to SQL Server
        """
            Connecting to SQL server and transmit all data stored in this Class
            
        """
        db = mysql.connector.connect(
            user=env.DB_USER,
            password=env.DB_PASSWORD,
            host=ip,
            database=env.DB_NAME
        )

        cursor = db.cursor()                   
        cursor.execute(Stringbuilder.SqlAddEntry(filename))
        # for i in range(len(self._data["TIME"])):
        #     row = []
        #     for s in signals.getSignalList():
        #         row.append(self._data[s.name][i])                
        #     cursor.execute(Stringbuilder.SqlBuidler("importobd"), row)
                    
        ##            row1 =[]
        ##            row1.append("test")
        ##            row1.append(self._data["GPS_Long"][i])
        ##            row1.append(self._data["GPS_Lat"][i])
        ##            cursor.execute(Stringbuilder.SqlBuidler("gpsdata"), row1)

        db.commit()
        db.close()

    def getAverageData(self, signalStr):
        """
            returns averange array from
        """

        if (not self._status == LogStatus.LOG_FILE_LOADED):
            raise ValueError("Not allowed! You have to loadFromFile first")
        if not signals.containsSignalByString(signalStr):
            raise ValueError("Signal is not available!")
        
        L = self._data[signalStr]
        L = [x for x in L if x is not None]
        return mean(L)

