# pylint: disable=no-member

import obd
import time
import csv
import datetime
import gps
import sys
import os
from LogFile import LogFile, LogStatus
from Signals import signals



def main():

    os.system("sudo gpsd /dev/serial0 -F /var/run/gpsd.sock")

    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    i = 1                                   #This line counter for output file is needed to manage different sample rates
    connection = None           
    NotConnected = True
    errorcnt = 0                            #Error count to detect the moment if ignition is off at the end of a Driving Cycle
    HasConnection = True

    filename = datetime.datetime.now().strftime("%y_%m_%d_%H:%M:%S_") + "test.csv"

    while NotConnected:
        connection = obd.OBD()              #Try to connect to OBD dongle
        print(connection.status())          #Print OBD Status for debugging

        #if the return of query RPM signal is not null --> Connecting succeeded 
        if(connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and (connection.query(obd.commands.RPM).is_null() == False)):
            NotConnected = False
        else:
            time.sleep(1)                   #Sleep 1s before trying to connect to OBD dongle again

    print("Successful connected to OBDII!") #Connecting to OBD dongle succeeded

    log = LogFile()
    log.createLogfile(filename)


    while (connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and HasConnection):

        if(connection.query(obd.commands.RPM).is_null() == True): 
            print("Error")
            errorcnt += 1
            print(errorcnt)
        else:
            errorcnt = 0

        if(errorcnt >= 3):
            print("End: Too many Errors - Ignition seems to be off")
            HasConnection = False

        i = i+1
        timestr = str(datetime.datetime.now())
        result = []
        result.append(timestr)
        lon = None
        lat = None
        if(i % 4 == 0):
            report = session.next()
            if report['class'] == 'TPV':
                if hasattr(report, 'lon') and hasattr(report, 'lat'):
                    lon = report.lon
                    lat = report.lat
                    print("Laengengrad:  ", lon)
                    print("Breitengrad: ", lat)

        for signal in signals.getOBDSignalList():

            if(i % signal.sampleRate == 0):  #Handle different Sample Rates
                r = connection.query(obd.commands[signal.name])
                if r.is_null():
                    result.append(0)
                else:
                    result.append(r.value.magnitude)
            else:
                result.append(None)
        
        #Appending GPS-Data
        result.append(lon)
        result.append(lat)
        #Append GPS Data first (if available) 
        log.addData(result)

        time.sleep(0.5)                      #Sleep 500ms to get not that much ammount of data 

        if(i % 20 == 0):                     #Appand file every 20 rows of measurement data
            log.appendFile()
            print("Appending File ...")

    print("Ignition Off")     


if __name__ == "__main__":
    main()
