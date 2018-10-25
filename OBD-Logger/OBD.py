import obd
import time
import csv
import datetime
from LogFile import LogFile, LogStatus, SupportedLabels

i = 1
connection = None
NotConnected = True

filename = datetime.datetime.now().strftime("%y_%m_%d_%H:%M:%S_") + "test.csv"

#PID's which we want to get
PidsMode1 = [4, 12, 13, 17, 31, 47, 70, 81, 90, 94, 127, 154]

while NotConnected:
    connection = obd.OBD()

    print(connection.status())
    if(connection.status() == obd.utils.OBDStatus.CAR_CONNECTED):
        NotConnected = False
    else:
        time.sleep(3)


PidsMode1 = [i for i in PidsMode1 if obd.commands.has_pid(1, i)]


HeaderCSV = ["Time", "Speed", "RPM"]
log = LogFile()
log.createLogfile(filename, HeaderCSV)

IgnitionStep2 = False
while (IgnitionStep2 == False):
    
    if(connection.query(obd.commands.RPM).is_null() == False):
        IgnitionStep2 = True
    time.sleep(3)
    
while (connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and (connection.query(obd.commands.RPM).is_null() == False)):
    
    i = i+1
    timestr = str(datetime.datetime.now()) #Parse String to datetime :  t = datetime.datetime.strptime(t,"%Y-%m-%d %H:%M:%S.%f") --> Calculate Difference: t = t2-t1 --> t = round(t.total_seconds()/60, 2) [Time in Minute]
    speed = connection.query(obd.commands.SPEED)
    rpm = connection.query(obd.commands.RPM)

    if speed.is_null():
        speed = 0
    else:
        speed = speed.value.magnitude
    
    if rpm.is_null():
        rpm = 0
    else:
        rpm = rpm.value.magnitude

    log.addData(timestr, speed, rpm)
    time.sleep(1)

    if(i%10 == 0):
        log.appendFile()

print("Zündung wurde ausgeschaltet!\n")
   



    





