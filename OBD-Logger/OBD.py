# pylint: disable=no-member

import obd
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

#Moduls for DS18B20 temperature sensor
import glob
import RPi.GPIO as GPIO
from GpsPoller import *

def main():
        
    gpsp = GpsPoller()
    gpsp.start()
    ### Initialisation of DS18B20 temperature sensor ###
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Wait for initialisation of DS18B20 temperature sensor
    base_dir = '/sys/bus/w1/devices/'
    tempError = 0
    device_folder = None
    
    while (tempError < 10):                 #TO DO: test tempError threshold
        try:
            device_folder = glob.glob(base_dir + '28*')[0]
            break
        except IndexError:
            time.sleep(0.5)
            tempError += 1
            continue
    
    if (device_folder != None):
        device_file = device_folder + '/w1_slave'
        TemperaturMessung(device_file)
    else:
        device_file = None


    
    ###

    i = 0                                   #This line counter for output file is needed to manage different sample rates
    connection = None           
    NotConnected = True
    errorcnt = 0                            #Error count to detect the moment if ignition is off at the end of a Driving Cycle
    HasConnection = True
    
    vinNotRead = True
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

                time.sleep(5)
            else:
                time.sleep(1)                   #Sleep 1s before trying to connect to OBD dongle again
        except:
            print("Error Connecting to OBD-Adapter (" + str(OBDError) + ")")
            
            time.sleep(2)
            OBDError += 1
        
        if(OBDError == 4):
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
            if hasattr(report, 'lon') and hasattr(report, 'lat'):
                print("GPS found-> Only GPS Mode")
                stri = "GPS_"
                stri_end = "x"
                
                OnlyGPSMode = 2
                temp = False
        else:
            time.sleep(1)
      
    log.createLogfile(stri + filename + stri_end)
    
    try:
        #Only GPS Mode
        while(OnlyGPSMode == 2):
            i = i+1
            GPS_Only(log, i, start, device_file, gpsp)

        #Normal Mode: OBD-, GPS-, Temperature-Data
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
            vin = None
            alt = None

            if(vinNotRead):
                c = OBDCommand("VIN", "Get Vehicle Identification Number",  b"0902", 20, raw_string, ECU.ENGINE, False)
                response = connection.query(c, force=True)
                vin = LogFile.parseVIN(response.value)
                vinNotRead = False

            
            #Get GPS data (if possible)
            if(i % signals.getSignal("GPS_Long").sampleRate == 0):
                report = gpsp.get_current_value()
                if report['class'] == 'TPV':
                    if hasattr(report, 'lon') and hasattr(report, 'lat'):
                        lon = report.lon
                        lat = report.lat
                        alt = report.alt                    
                        gpsTime = report.time
                        print("Laengengrad:  ", lon)
                        print("Breitengrad: ", lat)
            
            #Get internal tempterature data
            if (i % signals.getSignal("INTERNAL_AIR_TEMP").sampleRate == 0):
                internalTemp = TemperaturAuswertung(device_file)
            
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
            #Appending OBD data
            log.addData(result)

            time.sleep(0.5)                      #Sleep 500ms to get not that much ammount of data 

            if(i % 20 == 0):                     #Appand file every 10 rows of measurement data
                log.appendFile()
                print("Appending File ...")
        log.appendFile()
        print("Ignition Off")
        print("\nKilling Thread..")
        gpsp.running = False 
        gpsp.join()
        time.sleep(4)
    
    except(KeyboardInterrupt, SystemExit):
        print("Excpetion:")
        print("\nKilling Thread..")
        log.appendFile()
        gpsp.running = False 
        gpsp.join()
        


def GPS_Only(log, i, start, device_file, gpsp):
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
        
        if report['class'] == 'TPV':
            if hasattr(report, 'lon') and hasattr(report, 'lat'):
                lon = report.lon
                lat = report.lat
                alt = report.alt
                gpsTime = report.time
                print(gpsTime)

    #Get internal Temperature-Data
    if(i % signals.getSignal("INTERNAL_AIR_TEMP").sampleRate == 0):
        internalTemp = TemperaturAuswertung(device_file)

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


def TemperaturMessung(device_file):
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def TemperaturAuswertung(device_file):
    if (device_file != None):
        lines = TemperaturMessung(device_file)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.1)
            lines = TemperaturMessung(device_file)
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
        else:
            return None
    else:
        return None

if __name__ == "__main__":
    main()