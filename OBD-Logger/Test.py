from LogFile import LogFile, SupportedLabels
import os
import matplotlib.pyplot as plt
import numpy as np
import datetime
import time


print(os.getcwd())

filename = 'TestFile.csv'
log = LogFile()
log.createLogfile(filename, ["Time", "Speed", "RPM"])

t1 = str(datetime.datetime.now())

t2 = str(datetime.datetime.now())

log.addData(t1, 30, 2400)
log.addData(t2, 40, 2600)
log.addData(t2, 50, 2700)

log.appendFile()

log2 = LogFile()
log2.loadFromFile(filename)

speed = log2.getLabelData(SupportedLabels.RPM)

print(speed)


files = LogFile.getFilenames() #static Method
print(files)


log2 = LogFile()
log2.loadFromFile(files[0])
time = log2.getRelTime()
speed = log2.getLabelData(SupportedLabels.SPEED)

rpm = log2.getLabelData(SupportedLabels.RPM)


#Numpy Array
#time = np.asarray(time)
#speed = np.asarray(speed)
#rpm = np.asarray(rpm)



#Plot Signals
fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(time, speed)

ax1.set(ylabel='Speed [km/h]')

ax2.set(ylabel='RPM[U/min]', xlabel="time [s]")

ax2.plot(time, rpm)
plt.show()
