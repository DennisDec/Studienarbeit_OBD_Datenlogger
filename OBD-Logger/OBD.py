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

filename = datetime.datetime.now().strftime("%y_%m_%d_%H:%M:%S_") + "test.csv"


while NotConnected:
    connection = obd.OBD()

    print(connection.status())
    if(connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and (connection.query(obd.commands.RPM).is_null() == False)):
        NotConnected = False
    else:
        time.sleep(2)


print("Erfolg")


log = LogFile()
log.createLogfile(filename)
IgnitionStep2 = True
while (IgnitionStep2 == False):

    #connection = obd.OBD()
    if(connection.query(obd.commands.RPM).is_null() == False):
        IgnitionStep2 = True
    print("Ignition not on Step 2")
    time.sleep(2)

while (connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and (connection.query(obd.commands.RPM).is_null() == False)):

    i = i+1
    # Parse String to datetime :  t = datetime.datetime.strptime(t,"%Y-%m-%d %H:%M:%S.%f") --> Calculate Difference: t = t2-t1 --> t = round(t.total_seconds()/60, 2) [Time in Minute]
    timestr = str(datetime.datetime.now())

    result = []

    for signal in signals.getSignalList():
        # different samplerates

        #TODO: if i % signal.sampleRate (spart code)
        if(signal.sampleRate == 1):
            r = connection.query(obd.commands[signal.name])
            if r.is_null():
                result.append(0)
            else:
                result.append(r.value.magnitude)

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

print("Zündung wurde ausgeschaltet!\n")
