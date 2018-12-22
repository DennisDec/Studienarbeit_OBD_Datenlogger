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
import pygame



def main():
    
    pygame.mixer.init()
    pygame.mixer.music.load("/home/pi/Musik/success_sound") #Load Success Sound
    
    
    #Run GPS Deamon
    os.system("sudo gpsd /dev/serial0 -F /var/run/gpsd.sock")

    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    i = 1                                   #This line counter for output file is needed to manage different sample rates
    connection = None           
    NotConnected = True
    errorcnt = 0                            #Error count to detect the moment if ignition is off at the end of a Driving Cycle
    HasConnection = True
    OnlyGPSMode = 0
    OBDError = 0
    filename = datetime.datetime.now().strftime("%y_%m_%d_%H:%M:%S_") + "test.csv"

    while NotConnected:
        try:
                           
            connection = obd.OBD()              #Try to connect to OBD dongle
            print(connection.status())          #Print OBD Status for debugging
            
            #if the return of query RPM signal is not null --> Connecting succeeded 
            if(connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and (connection.query(obd.commands.RPM).is_null() == False)):
                NotConnected = False
                print("Successful connected to OBDII!") #Connecting to OBD dongle succeeded
                pygame.mixer.music.play()
                time.sleep(5)
            else:
                time.sleep(1)                   #Sleep 1s before trying to connect to OBD dongle again
        except:
            print("Error Connecting to OBD-Adapter (" + str(OBDError) + ")")
            
            time.sleep(2)
            OBDError +=1
        
        if(OBDError == 4):
                NotConnected = False
                OnlyGPSMode = 1
             

    
    pygame.mixer.music.load("/home/pi/Musik/success_1")
    
    log = LogFile()
    
    OBDError = 0
    temp = True
    stri = ""
    
    while(temp and OnlyGPSMode == 1):
        report = session.next()
        if report['class'] == 'TPV':
            if hasattr(report, 'lon') and hasattr(report, 'lat'):
                print("GPS found-> Only GPS Mode")
                stri = "GPS_"
                pygame.mixer.music.play()
                OnlyGPSMode = 2
                temp = False
        else:
            time.sleep(1)
      
    log.createLogfile(stri + filename)
    
    while(OnlyGPSMode == 2):
        i = i+1
        GPS_Only(session, log, i)
 
    while (connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and HasConnection):
        
        #Error handling to detect IGNITION OFF Signal
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

        #Get GPS Information if possible
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
    log.appendFile()
    print("Ignition Off") 
    pygame.mixer.music.load("/home/pi/Musik/end")
    pygame.mixer.music.play()
    time.sleep(4)



def GPS_Only(session, log, count):

    timestr = str(datetime.datetime.now())
    result = []
    result.append(timestr)
    lon = None
    lat = None
        
    report = session.next()
    
    if report['class'] == 'TPV':
        if hasattr(report, 'lon') and hasattr(report, 'lat'):
            lon = report.lon
            lat = report.lat
            OBDError = 0 

    for signal in signals.getOBDSignalList():
        result.append(None)
    
    #Appending GPS-Data
    result.append(lon)
    result.append(lat)
    #Appending all other OBD Siganls
    log.addData(result)

    time.sleep(1.0)                      #Sleep 500ms to get not that much ammount of data 

    if(count % 10 == 0):                     #Appand file every 20 rows of measurement data
        log.appendFile()
        print("Appending File ...")



if __name__ == "__main__":
    main()
  