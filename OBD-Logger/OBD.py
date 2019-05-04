# pylint: disable=no-member

import obd                                      #For connection with OBD-adapter
from obd import OBDCommand, Unit
from obd.protocols import ECU
from obd.decoders import raw_string
import time
import csv
import datetime
import gps
import sys
import os
from LogFile import LogFile, LogStatus         
from Signals import signals
from uptime import uptime
from subprocess import call
#Moduls for DS18B20 temperature sensor
import glob
from TempPoller import TempPoller
#Moduls for GPS sensor
from GpsPoller import GpsPoller
import RPi.GPIO as GPIO



def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17,GPIO.OUT)
    GPIO.setup(27,GPIO.OUT)
    GPIO.setup(22,GPIO.OUT)
    GPIO.setwarnings(False)

    RGBblue =  17
    RGBred = 27
    RGBgreen = 22
    GPIO.output(RGBblue, GPIO.LOW)
    GPIO.output(RGBred,GPIO.LOW)
    GPIO.output(RGBgreen,GPIO.LOW)
    GPIO.output(RGBblue,GPIO.HIGH)
    GPIO.output(RGBred,GPIO.HIGH)
    GPIO.output(RGBgreen,GPIO.HIGH)
    
    gpsp = GpsPoller()                      #Start GPS thread
    gpsp.start()
    temperature = TempPoller()              #Start temperature thread
    temperature.start()
    
    i = 0                                   #This line counter for output file is needed to manage different sample rates
    connection = None           
    NotConnected = True
    errorcnt = 0                            #Error count to detect the moment if ignition is off at the end of a Driving Cycle
    HasConnection = True

    OnlyGPSMode = 0
    OBDError = 0
    filename = datetime.datetime.now().strftime("%y_%m_%d_%H:%M:%S_") + "test.csv"
    start = uptime()

    #Try to establish a connection with the OBD dongle
    while NotConnected:
        try:
                           
            connection = obd.OBD()              #Try to connect to OBD dongle
            print(connection.status())          #Print OBD Status for debugging
            
            #if the return of query RPM signal is not null --> Connecting succeeded 
            if(connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and (connection.query(obd.commands.RPM).is_null() == False)):
                NotConnected = False
                print("Successful connected to OBDII!") #Connecting to OBD dongle succeeded

                time.sleep(1)
            else:
                time.sleep(1)                   #Sleep 1s before trying to connect to OBD dongle again
        except:
            print("Error Connecting to OBD-Adapter (" + str(OBDError) + ")")
            
            time.sleep(1)
            OBDError += 1
        
        if(OBDError == 10):
                NotConnected = False
                OnlyGPSMode = 1
             
    
    log = LogFile()
    
    OBDError = 0
    temp = True
    stri = ""
    stri_end = ""
    
    #Handle only GPS Mode: check if GPS data is available 
    while(temp and OnlyGPSMode == 1):
        report = gpsp.get_current_value()
        if report['class'] == 'TPV':
            if hasattr(report, 'lon') and hasattr(report, 'lat') and hasattr(report, 'alt'):
                print("GPS found-> Only GPS Mode")
                #Set Colour to Cyan
                GPIO.output(RGBblue, GPIO.LOW)
                GPIO.output(RGBred,GPIO.LOW)
                GPIO.output(RGBgreen,GPIO.LOW)
                GPIO.output(RGBblue, GPIO.HIGH)
                stri = "GPS_"
                stri_end = "x"
                
                OnlyGPSMode = 2
                temp = False
        else:
            time.sleep(1)
    
    #Create logfile
    log.createLogfile(stri + filename + stri_end)
    
    vin = None

    start = uptime()
    try:
        #Only GPS Mode
        while(OnlyGPSMode == 2):
            i = i+1
            if(i == 2048): 
                i = 0
            GPS_Only(log, i, start, temperature, gpsp)

        if(connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and HasConnection):
            c = OBDCommand("VIN", "Get Vehicle Identification Number",  b"0902", 20, raw_string, ECU.ENGINE, False)
            response = connection.query(c, force=True)
            vin = LogFile.parseVIN(response.value)
            print(vin)
            #connection.close()
            #change to asynchronous connection
            connection = obd.Async()
            connection.watch(obd.commands.RPM) # keep track of the RPM
            for signal in signals.getOBDSignalList():
                connection.watch(obd.commands[signal.name]) # keep track of the RPM
            connection.start()
            time.sleep(0.5)
            #Set Colour to pink
            GPIO.output(RGBblue, GPIO.LOW)
            GPIO.output(RGBred,GPIO.LOW)
            GPIO.output(RGBgreen,GPIO.LOW)
            GPIO.output(RGBblue, GPIO.HIGH)
            GPIO.output(RGBred, GPIO.HIGH)
                
        #Normal Mode: OBD-, GPS-, Temperature-Data
        while (connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and HasConnection):
            
            #Error handling to detect IGNITION OFF Signal
            if(connection.query(obd.commands.RPM).is_null() == True): 
                print("Error")
                errorcnt += 1
                print(errorcnt)
            else:
                errorcnt = 0

            if(errorcnt >= 5):
                print("End: Too many Errors - Ignition seems to be off")
                HasConnection = False
                GPIO.output(RGBblue, GPIO.LOW)
                GPIO.output(RGBred,GPIO.LOW)
                GPIO.output(RGBgreen,GPIO.LOW)

            i = i+1
            if(i == 2048): 
                i = 0

            #Get actual time data
            #timestr = str(datetime.datetime.now())
            timestr = uptime()
            timestr = timestr - start
            result = []
            result.append(timestr)

            #Set the GPS and Temperature variables to initial value
            lon = None
            lat = None
            gpsTime = None
            internalTemp = None
            alt = None
            
            #Get GPS data (if possible)
            if(i % signals.getSignal("GPS_Long").sampleRate == 0):
                report = gpsp.get_current_value()
                (lon, lat, alt, gpsTime) = getGpsData(report)

            #Get internal tempterature data
            if (i % signals.getSignal("INTERNAL_AIR_TEMP").sampleRate == 0):
                internalTemp = temperature.get_current_value()
            
            #Get OBD data
            for signal in signals.getOBDSignalList():

                if(i % signal.sampleRate == 0):  #Handle different Sample Rates
                    r = connection.query(obd.commands[signal.name])
                    if r.is_null():
                        result.append(0)
                    else:
                        result.append(r.value.magnitude)
                else:
                    result.append(None)
            
            #Appending GPS-Data (if available)
            result.append(lon)
            result.append(lat)
            result.append(alt)
            result.append(gpsTime)
            #Append Temperature-Data (if available)
            result.append(internalTemp)
            result.append(vin)

            #write all data to file
            log.addData(result)
            
            if(vin != None):                     #write vin to file only once to readuce ammount of data
                vin = None

            time.sleep(0.5)                      #Sleep 500ms to get not that much ammount of data 
            
            if(i % 20 == 0):                     #Appand file every 20 rows of measurement data
                log.appendFile()
                print("Appending File ...")


        log.appendFile()
        print("Ignition Off")
        print("\nKilling Threads..")
        gpsp.running = False 
        gpsp.join()
        temperature.running = False
        temperature.join()
        connection.stop()
        GPIO.output(RGBblue, GPIO.LOW)
        GPIO.output(RGBred,GPIO.LOW)
        GPIO.output(RGBgreen,GPIO.LOW)
        GPIO.cleanup()

    
    except(KeyboardInterrupt, SystemExit):
        GPIO.output(RGBblue, GPIO.LOW)
        GPIO.output(RGBred,GPIO.LOW)
        GPIO.output(RGBgreen,GPIO.LOW)
        GPIO.cleanup()
        print("Excpetion:")
        print("\nKilling Threads..")
        log.appendFile()
        gpsp.running = False 
        gpsp.join()
        temperature.running = False
        temperature.join()
        connection.stop()
           
def getGpsData(report):
    """ return gps data from report """
    lon = None
    lat = None
    alt = None
    gpsTime = None
    if report['class'] == 'TPV':
        if(hasattr(report, 'time')):                    
            gpsTime = report.time
        if hasattr(report, 'lon') and hasattr(report, 'lat') and hasattr(report, 'alt') and hasattr(report, 'time'):
            lon = report.lon
            lat = report.lat
            alt = report.alt                    
            gpsTime = report.time
            print("Lon:  ", lon)
            print("Lat: ", lat)
    return (lon, lat, alt, gpsTime)

def GPS_Only(log, i, start, temperature, gpsp):
    """ This method is not logging OBD-data """

    #Get actual time data
    #timestr = str(datetime.datetime.now())
    timestr = uptime()
    timestr = timestr - start
    result = []
    result.append(timestr)
    
    #Set the GPS and Temperature variables to initial value
    lon = None
    lat = None
    alt = None
    gpsTime = None
    internalTemp = None
    vin = None
        
    #Get GPS data
    if(i % signals.getSignal("GPS_Long").sampleRate == 0):
        report = gpsp.get_current_value()
        (lon, lat, alt, gpsTime) = getGpsData(report)

    #Get internal Temperature-Data
    if(i % signals.getSignal("INTERNAL_AIR_TEMP").sampleRate == 0):
        internalTemp = temperature.get_current_value()

    #Append None for OBD signals
    for signal in signals.getOBDSignalList():
        result.append(None)
    
    #Appending GPS data
    result.append(lon)
    result.append(lat)
    result.append(alt)
    result.append(gpsTime)
    #Append internal temperature data
    result.append(internalTemp)
    result.append(vin)
    #Appending all other OBD Siganls
    log.addData(result)

    time.sleep(0.5)                      #Sleep 500ms to get not that much ammount of data 

    if(i % 10 == 0):                     #Append file every 10 rows of measurement data
        log.appendFile()
        print("Appending File ...")


if __name__ == "__main__":
    main()