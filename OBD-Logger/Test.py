from LogFile import LogFile, SupportedLabels
import os
import matplotlib.pyplot as plt
import numpy as np
import datetime
import time
from Signals import signals

filename = 'TestFile.csv'
log = LogFile()
log.createLogfile(filename)


speed = [34, 35, 36, 24, 23, 56]
rpm = [2000, 2001, 2100, 3100, 50000, 60000]
load = [60, 40, 50, 30, 70, 80]
maf = [3, 4, 3, 4, 3, 2]
temp = [13, 13, 13, 14, 14, 14]
pedal = [30, 33, 24, 36, 21, 18]
afr = [1, 1.2, 1.1, 1, 1, 1]
fuel_lvl = [80, 80, 80, 79, 79, 79]

for i in range(0, len(speed)):
    t1 = str(datetime.datetime.now())
    log.addData(t1, [speed[i], rpm[i], load[i], maf[i],
                temp[i], pedal[i], afr[i], fuel_lvl[i]])

log.appendFile()

log2 = LogFile()
log2.loadFromFile(filename)

for label in signals.getSignalList():
    print(str(label.name) + str(log2.getLabelData(label.name)))


files = LogFile.getFilenames()  # static Method
print(files)


log2 = LogFile()
log2.loadFromFile(files[0])
time = log2.getRelTime()
speed = log2.getLabelData(SupportedLabels.SPEED)
rpm = log2.getLabelData(SupportedLabels.RPM)
load = log2.getLabelData(SupportedLabels.ENGINE_LOAD)
temp = log2.getLabelData(SupportedLabels.AMBIANT_AIR_TEMP)
pedal = log2.getLabelData(SupportedLabels.RELATIVE_ACCEL_POS)
maf = log2.getLabelData(SupportedLabels.MAF)
afr = log2.getLabelData(SupportedLabels.COMMANDED_EQUIV_RATIO)


# Numpy Array
#time = np.asarray(time)
#speed = np.asarray(speed)
#rpm = np.asarray(rpm)


# Plot Signals
fig, (ax1, ax2, ax3, ax4, ax5, ax6, ax7) = plt.subplots(7, 1)
ax1.plot(time, speed)
ax4.plot(time, temp)
ax4.set(ylabel='Temperatur [°C]')
ax5.plot(time, pedal)
ax5.set(ylabel='Accelerator pedal [%]')
ax6.plot(time, maf)
ax6.set(ylabel='Mass Air Flow')
ax7.plot(time, afr)
ax7.set(ylabel='Air Fuel Ratio')


if(len(load) == len(time)):
    ax3.plot(time, load)
ax1.set(ylabel='Speed [km/h]')
ax3.set(ylabel='Load [%]')

ax2.set(ylabel='RPM[U/min]', xlabel="time [s]")

ax2.plot(time, rpm)
plt.show()
