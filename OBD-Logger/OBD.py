# pylint: disable=no-member

import obd
import time
import csv
import datetime
from LogFile import LogFile, LogStatus
from Signals import signals

i = 1
connection = None
NotConnected = True
errorcnt = 0
HasConnection = True

filename = datetime.datetime.now().strftime("%y_%m_%d_%H:%M:%S_") + "test.csv"

while NotConnected:
    connection = obd.OBD()

    print(connection.status())
    if(connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and (connection.query(obd.commands.RPM).is_null() == False)):
        NotConnected = False
    else:
        time.sleep(2)

print("Successful connected to OBDII!")

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
        print("End")
        HasConnection = False

    i = i+1
    timestr = str(datetime.datetime.now())
    result = []

    for signal in signals.getSignalList():
        # different samplerates

        # TODO: if i % signal.sampleRate (spart code)
        if(signal.sampleRate == 1):
            r = connection.query(obd.commands[signal.name])
            if r.is_null():
                result.append(0)
            else:
                result.append(round(r.value.magnitude,2))

        elif(signal.sampleRate == 2):
            if(i % 5 == 0):
                r = connection.query(obd.commands[signal.name])
                if r.is_null():
                    result.append(0)
                else:
                    result.append(r.value.magnitude)
            else:
                result.append(None)

    log.addData(timestr, result)
    time.sleep(1)

    if(i % 10 == 0):
        log.appendFile()
        print("Append File")

print("Ignition Off\n")
