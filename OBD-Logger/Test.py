# pylint: disable=no-member
from statistics import mean
from LogFile import LogFile
import os
import matplotlib.pyplot as plt
import numpy as np
import datetime
import time
from Signals import signals

#Average Test
L = [1,2,4,3,6,None,8,0 ,0]
liste = [x for x in L if x is not None]
mean(liste)


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
average_speed = log2.getAverageData(signals.SPEED.name)
time = log2.getRelTime()
speed = log2.getLabelData(signals.SPEED.name)
afr = log2.getLabelData(signals.COMMANDED_EQUIV_RATIO.name)
temp = log2.getLabelData(signals.AMBIANT_AIR_TEMP.name)
rpm = log2.getLabelData(signals.RPM.name)
load = log2.getLabelData(signals.ENGINE_LOAD.name)
maf = log2.getLabelData(signals.MAF.name)
pedal = log2.getLabelData(signals.RELATIVE_ACCEL_POS.name)
fuel_lvl = log2.getLabelData(signals.FUEL_LEVEL.name)



fuelCons = log2.getFuelConsumption()

# Numpy Array
#time = np.asarray(time)
#speed = np.asarray(speed)
#rpm = np.asarray(rpm)


# Plot Signals
fig, (ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8) = plt.subplots(8, 1)
ax1.plot(time, speed)
ax4.plot(time, temp)
ax4.set(ylabel='Temperatur [°C]')
ax5.plot(time, pedal)
ax5.set(ylabel='Accelerator pedal [%]')
ax6.plot(time, maf)
ax6.set(ylabel='Mass Air Flow')
ax7.plot(time, afr)
ax7.set(ylabel='Air Fuel Ratio')

ax8.plot(time, fuelCons)
ax8.set(ylabel='FuelCons L/100km')


if(len(load) == len(time)):
    ax3.plot(time, load)
ax1.set(ylabel='Speed [km/h]')
ax3.set(ylabel='Load [%]')

ax2.set(ylabel='RPM[U/min]', xlabel="time [s]")

ax2.plot(time, rpm)
plt.show()
