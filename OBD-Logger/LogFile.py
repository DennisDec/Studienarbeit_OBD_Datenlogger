# pylint: disable=no-member

"""
This class is controlling the datalogging

"""
import csv
import os
import datetime    
import mysql.connector
import env
import os
import subprocess
import socket
import json
import bcrypt
from subprocess import Popen, PIPE

from datetime import datetime, timedelta

from Util import Util

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
    def SqlAddEntry(filename, date, starttime, totalKM, endtime, VIN, fuelConsumption, energyConsumption, endLat, endLong, endDate):
        """
        Create query string to load new file to db
        SqlAddEntry(filename, date, starttime, totalKM, endtime, VIN, fuelConsumption, energyConsumption, endLat, endLong, endDate)
        date: MM-DD-YYYY
        time: HH:MM:SS
        """
        
        sql = "INSERT INTO  data ( filename, date, starttime, totalKM, endtime," \
            + " VIN, fuelConsumption, energyConsumption, endLat, endLong, endDate ) VALUES ('" + str(filename) \
            + "', '" + str(date) + "', '" + str(starttime) + "', '" + str(totalKM) + "', '" + str(endtime) \
            +"', '" + str(VIN) + "', '" + str(fuelConsumption) +"', '" + str(energyConsumption) + "', '" + str(endLat) \
            +"', '" + str(endLong) + "', '" + str(endDate) +  "')"

        return sql


class LogFile:
    """Class to log data from OBDII adapter"""

    @staticmethod
    def getFilenames():
        """returns a sorted List of filenames which are located in path"""
        return sorted([f for f in os.listdir(path) if f.endswith('.csv')])

    @staticmethod
    def parseVIN(res):
        """parse VIN from OBD response to VIN string"""
        str1 = res.split('\n')
        VIN = ""
        str10 = str1[0].split("490201")[-1]
        VIN = VIN + str(str10)
        VIN = VIN + str(str1[1][5:]) + str(str1[2][5:])
        VIN = bytes.fromhex(VIN).decode("utf-8")
        return VIN

    def __init__(self):
        self._filename = ""
        self._data = {

        }
        self._VIN = ""

        for s in signals.getSignalList():    #Get OBD Signals
            # Fill Dictionary with Signals from Class Signals
            self._data[s.name] = []

        self._status = LogStatus.NO_LOGFILE
        self._isBrokenFile = False

    def status(self):
        return self._status

    def isBrokenFile(self):
        return self._isBrokenFile

    def getDataDict(self):
        return self._data

    def transferToJson(self):
        """ You have to call loadFromFile first"""
        data = self._data   #get dictionary
        if("VIN" in data):
            data.pop("VIN")     #remove VIN from data

        jsonPath = path + "JSON/"
        filename = self._filename
        with open( jsonPath + filename.split(".csv")[0] + ".json", 'w') as fp:
            json.dump(data, fp)
        return filename.split(".csv")[0] + ".json"    

    def copyFileToServer(self, filename):
        errcnt = 0
        ip = []
        f = open(env.PATH_REPO + "ipAddress.ip", "r")
        ipAddress = f.read()
        if(not ipAddress == ""):
            stri = str(subprocess.check_output(('nmap -p22 ' + str(ipAddress)), shell=True))
            if(stri.find("open") != -1):
                ip.append(str(ipAddress))
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 1))
            own_ip = str(s.getsockname()[0])

            ip_mask = ".".join(own_ip.split('.')[0:-1]) + ".*"

            stri = str(subprocess.check_output(('nmap -p22 ' + str(ip_mask)), shell=True))
            output = stri.split("\\n")

            for i, line in enumerate(output):
                if(line.find("open") != -1 and output[i-3].split(' ')[-1] != own_ip):
                    ip.append(output[i-3].split(' ')[-1].replace("(", "").replace(")",""))
                    print(ip)
        
        if(len(ip) >= 1):              
            for i, tmp in enumerate(ip):
                cmd = "sshpass -p '" + str(env.DB_PASSWORD) + "' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/home/pi/known_host -r " + str(path) + "JSON/" + str(filename) + " pi@" + str(ip[i]) +":datafiles/"
                
                proc =  Popen([cmd], stdin=PIPE, stdout=PIPE,  stderr=PIPE, shell=True)
                stdout, stderr = proc.communicate()
                print(stderr)
                
                if stderr == b'' or stderr.endswith(b'to the list of known hosts.\r\n'):
                    try:
                        self.transmitToSQL(filename, str(ip[i]))
                        f = open(env.PATH_REPO + "ipAddress.ip", "w")
                        f.write(str(ip[i]))
                    except mysql.connector.errors.IntegrityError as err:
                        return False, err
                    return True, ""
                else:
                    if(len(ip)-1  == i):
                        return False, ""
        else:
            return False, "No Server connection found!"
                    
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
                if(s.name == "GPS_Time" or s.name == "VIN" or signalList[i] == None):
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
            tList.append(round((datetime.strptime(i, "%Y-%m-%d %H:%M:%S.%f") -
                                datetime.strptime(self._data[signals.TIME.name][0], "%Y-%m-%d %H:%M:%S.%f")).total_seconds(), 2))
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
            columns = []
            with open(env.PATH + filename, 'r') as f:
                reader = csv.reader( (line.replace('\0','') for line in f) )
                for row in reader:
                    if columns:
                        for i, value in enumerate(row):
                            if(value == ""):
                                columns[i].append(None)
                            else:
                                if(Util.isfloat(value)):
                                    columns[i].append(float(value))
                                else:
                                    columns[i].append(value)
                    else:
                        # first row
                        columns = [[value] for value in row]
            as_dict = {c[0]: c[1:] for c in columns}
            if("VIN" in as_dict):
                #TODO:
                vinList = [x for x in as_dict["VIN"] if x is not None]
                if(len(vinList) > 0):
                    self._VIN = vinList[0]
            if("GPS_Long" in as_dict):
                gpsL = [x for x in as_dict["GPS_Long"] if x is not None]
                if(len(gpsL) < 1):
                    self._isBrokenFile = True
            
            if("RPM" in as_dict):
                rpm = [x for x in as_dict["RPM"] if int(x) is not 0]
                if(len(rpm) < 1):
                    self._isBrokenFile = True

            self._data = as_dict
            
        except Exception as e:
            raise FileNotFoundError("Error: Loading File failed!" + str(e))
        self._filename = filename
        self._status = LogStatus.LOG_FILE_LOADED

    def transmitToSQL(self, filename, ip):                      #Connecting to SQL Server
        """
            Connecting to SQL server and transmit all data stored in this Class
            
        """
        db = mysql.connector.connect(
            user=env.DB_USER,
            password=env.DB_PASSWORD,
            host=ip,
            database=env.DB_NAME
        )
        #calculate the data

        dateTimeStart = self.getStartTime().split(";")
        dateTimeEnd = self.getEndTime().split(";")

        date = dateTimeStart[0]
        starttime = dateTimeStart[1]

        endDate = dateTimeEnd[0]
        endtime = dateTimeEnd[1]
        totalKM = self.getDistance()
        VIN = self.getHashedVIN()
        fuelConsumption = self.getFuelConsumption()
        energyConsumption = self.getEnergyCons()
        endLat = [x for x in self._data["GPS_Lat"] if x is not None][-1]
        endLong = [x for x in self._data["GPS_Long"] if x is not None][-1]

        
        cursor = db.cursor()                   
        cursor.execute(Stringbuilder.SqlAddEntry(filename, date, starttime, totalKM, endtime, VIN, fuelConsumption, energyConsumption, endLat, endLong, endDate))
        
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

    def getFuelConsumption(self):
        speed = self._data["SPEED"]
        maf = self._data["MAF"]
        cer = self._data["COMMANDED_EQUIV_RATIO"]

        #density fuel : 748
        #Air Fuel ratio : 14.7
        fuelCon_normal = []
        for i in range(len(speed)):
            if((cer[i]) == 0):
                pass
            else:
                fuelCon_normal.append(((maf[i]* 3600)/(748*14.7*cer[i])))

        avfuelCon = Util.mean(fuelCon_normal)
        avSpeed = Util.mean(speed)

        avfuelCon = 100*(avfuelCon/avSpeed)

        print("Normal: " + str(avfuelCon))

        return avfuelCon

    def getHashedVIN(self):
        """encryption of the vehicle identification number to store it in db on server"""
        hashed = ""
        if(not self._VIN == ""):
            hashed = bcrypt.hashpw(self._VIN.encode(), bcrypt.gensalt(10))
        return hashed.decode("utf-8")

    def getEnergyCons(self):
        """ Time has to be relative Signal! """
        time = self.getTime()
        diff = []
        maf = self._data[signals.MAF.name] #Mass Air Flow
        cer = self._data[signals.COMMANDED_EQUIV_RATIO.name] 

        eff = 0.35 #efficiency engine
        cal = 0.01125  #calorific value gasoline
        airFuel = 14.7 #Air Fuel ratio  

        for i in range(1, len(time)):
            diff.append(time[i]- time[i-1])
        dT = Util.mean(diff)
        
        energy = []
        for i in range(len(maf)):
            if(cer[i] == 0):
                pass
            else:
                energy.append(eff *cal *dT * maf[i] / (airFuel * cer[i]))
        
        return (sum(energy)/0.85) #Division: efficiency of electric engine

    def getStartTime(self):

        """ returns a datetime of the real start of datalogging """
        str = "2000-01-01T00:00:00.000Z000.00" #default Time
        strlist = [x for x in self._data["GPS_Time"] if x is not None]
        if(len(strlist) >= 1):
            str = strlist[-1]
        #2000-01-01T00:00:00.000Z000.00

        dateArray  = str.split("T")[0].split("-")
        year = dateArray[0]
        month = dateArray[1]
        day = dateArray[2]

        time = str.split("T")[1].split("Z")[0].split(":")

        hours = time[0]
        min = time[1]
        sec = time[2]
        if(str in self._data["GPS_Time"]):
            ind = self._data["GPS_Time"].index(str)
            timeInd = self._data["TIME"][ind]
        else:#deault Time
            ind = 0
            timeInd = 0
        d = datetime(year=int(year), month=int(month), day=int(day), hour=int(hours), minute=int(min), second=int(float(sec))) - timedelta(seconds=int(float(timeInd)))
        
        return d.strftime("%m-%d-%Y;%H:%M:%S")

    def getEndTime(self):
        #2019-02-23T10:58:31.000Z417.75
        str = "2000-01-01T00:00:00.000Z000.00" #default Time
        strlist = [x for x in self._data["GPS_Time"] if x is not None]
        if(len(strlist) >= 1):
            str = strlist[-1]

        dateArray  = str.split("T")[0].split("-")
        print(dateArray)
        year = dateArray[0]
        month = dateArray[1]
        day = dateArray[2]

        time = str.split("T")[1].split("Z")[0].split(":")

        hours = time[0]
        min = time[1]
        sec = time[2]

        if(str in self._data["GPS_Time"]):
            ind = self._data["GPS_Time"].index(str)
            timeInd = self._data["TIME"][ind]
            timeend = self._data["TIME"][-1]
        else:
            timeInd = 0
            timeend = 0
        timedel = timeend - timeInd


        d = datetime(year=int(year), month=int(month), day=int(day), hour=int(hours), minute=int(min), second=int(float(sec))) + timedelta(seconds=int(float(timedel)))
        return d.strftime("%m-%d-%Y;%H:%M:%S")

    def getDistance(self):
        #time = self._data[signals.TIME.name][-1]
        time = self.getTime()
        avSpeed = Util.mean(self._data[signals.SPEED.name])
        km = avSpeed*(time[-1]/3600)
        return round(km,2)




                

