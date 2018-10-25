import obd
import time
import csv
import datetime
from LogFile import LogFile, LogStatus, SupportedLabels

i = 1
connection = None
NotConnected = True

filename = datetime.datetime.now().strftime("%y_%m_%d_%H:%M:%S_") + "test.csv"

# PID's which we want to get
PidsMode1 = [4, 12, 13, 17, 31, 47, 70, 81, 90, 94, 127, 154]

while NotConnected:
    connection = obd.OBD()

    print(connection.status())
    if(connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and (connection.query(obd.commands.RPM).is_null() == False)):
        NotConnected = False
    else:
        time.sleep(2)


print("Erfolg")

PidsMode1 = [i for i in PidsMode1 if obd.commands.has_pid(1, i)]

HeaderCSV = ["Time", "Speed", "RPM", "Engine_Load",
             "MAF", "Temperature", "Pedal", "AFR", "Fuel Level"]
log = LogFile()
log.createLogfile(filename, HeaderCSV)

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
    result.append(connection.query(obd.commands.SPEED))
    result.append(connection.query(obd.commands.RPM))
    result.append(connection.query(obd.commands.ENGINE_LOAD))
    result.append(connection.query(obd.commands.MAF))
    result.append(connection.query(obd.commands.AMBIANT_AIR_TEMP))
    result.append(connection.query(obd.commands.RELATIVE_ACCEL_POS))
    result.append(connection.query(obd.commands.COMMANDED_EQUIV_RATIO))
    result.append(connection.query(obd.commands.FUEL_LEVEL))

    res = []
    for r in result:
        if r.is_null():
            res.append(0)
        else:
            res.append(r.value.magnitude)

    log.addData(timestr, res[0], res[1], res[2],
                res[3], res[4], res[5], res[6], res[7])
    time.sleep(1)

    if(i % 10 == 0):
        log.appendFile()
        print("Append File")

print("Zündung wurde ausgeschaltet!\n")
