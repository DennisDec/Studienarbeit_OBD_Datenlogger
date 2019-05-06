from LogFile import LogFile, LogStatus, Stringbuilder
# pylint: disable=no-member
import unittest
import time
import datetime
from OBDSignal import OBDSignal 
import hashlib
from Signals import signals
import bcrypt
import numpy as np


from Signals import signals


class TestLogFile(unittest.TestCase):

    def test_init(self):
        log = LogFile()
        self.assertEqual(log.status(), LogStatus.NO_LOGFILE)
        #Check wheather alls Signals are in the datadict after initialization
        for sig in signals.getSignalList():
            self.assertEqual(sig.name in log.getDataDict(), True)
    
    def test_DecodeVIN(self):
        raw = "4D463044585847414B4448503939393939" #Hex Values from OBD
        VINreal = b"MF0DXXGAKDHP99999"          #real VIN
        VIN = bytes.fromhex(raw).decode('utf-8')
        print(VIN)
        #BCRYPT
        hashed = bcrypt.hashpw(VIN.encode(), bcrypt.gensalt(10))
        print(hashed)
        self.assertEqual(bcrypt.checkpw(VINreal, hashed), True)

    def test_SQLString(self):
        sql = "INSERT INTO importobd ("
        s = []
        for signal in signals.getSignalList():
            s.append(signal.db_name)
        sql += ", ".join(s)
        sql += ") VALUES ("
        tmp = []
        for i in range(len(s)):
            tmp.append("%s")
        sql += ", ".join(tmp)
        sql += ")" 

        print(sql)
        #INSERT INTO importobd (time, speed, rpm, engine_load, maf, temperature, pedal, afr, fuel_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)


    def test_EqualOBDSignals(self):
        o1 = OBDSignal("Signal1", "Test", True, 1 , 3)
        o2 = OBDSignal("Signal1", "Test", True, 1 , 3)
        o3 = OBDSignal("Signal1", "Test", True, 2 , 3)

        self.assertEqual(o1, o2)
        self.assertNotEqual(o2, o3)

    def test_containsMethod(self):
        o1 = OBDSignal("SPEED", "Test", True, 1 , 3)
        o2 = OBDSignal("Signal1", "Test", True, 1 , 3)
        
        self.assertTrue(signals.containsSignal(o1))
        self.assertFalse(signals.containsSignal(o2))

    def test_StatusNoLogFile(self):
        log = LogFile()
        self.assertEqual(log.status(), LogStatus.NO_LOGFILE)

    def test_StatusLogCreated(self):
        log = LogFile()
        log.createLogfile("testFile.test")
        self.assertEqual(log.status(), LogStatus.LOG_CREATED)


    def test_getFilenames(self):
        LogFile.getFilenames()
        self.assertTrue(isinstance(LogFile.getFilenames(), list))
    
    def test_loadEmptyFile(self):
        log = LogFile()
        log.createLogfile("empty.test")

        log2 = LogFile()
        log2.loadFromFile("empty.test")
        self.assertTrue(log2.isBrokenFile())


        

    def test_createRandomDataFileNoGPS(self):
        log = LogFile()
        log.createLogfile("Random_NoGPS.test")
        time = range(100)
        speed = np.random.randint(100, size=100).tolist()
        rpm = np.random.randint(5000, size=100).tolist()
        load = np.random.randint(100, size=100).tolist()
        maf = np.random.randint(100, size=100).tolist()
        temp = np.random.randint(30, size=100).tolist()
        pedal = np.random.randint(100, size=100).tolist()
        afr = [1]*100
        fuel_lvl = np.random.randint(100, size=100).tolist()
        gps_long = [None] * 100
        gps_lat = [None] * 100
        gps_alt = [None] * 100
        gps_time = [None] * 100
        internal_temp = np.random.randint(30, size=100).tolist()
        vin = ["MF0DXXGAKDJP09111"] * 100
        for i in  range(0, len(speed)):
                log.addData([time[i], speed[i], rpm[i], load[i], maf[i], temp[i], pedal[i], afr[i], fuel_lvl[i], gps_long[i], gps_lat[i], gps_alt[i], gps_time[i], internal_temp[i], vin[i] ])

        log.appendFile()
        log2 = LogFile()
        log2.loadFromFile(log.getfilename())
        speed_csv = log2.getLabelData(signals.SPEED.name)
        afr_csv = log2.getLabelData(signals.COMMANDED_EQUIV_RATIO.name)
        temp_csv = log2.getLabelData(signals.AMBIANT_AIR_TEMP.name)
        rpm_csv = log2.getLabelData(signals.RPM.name)
        load_csv = log2.getLabelData(signals.ENGINE_LOAD.name)
        maf_csv = log2.getLabelData(signals.MAF.name)
        pedal_csv = log2.getLabelData(signals.RELATIVE_ACCEL_POS.name)
        fuel_lvl_csv = log2.getLabelData(signals.FUEL_LEVEL.name)
        gps_long_csv = log2.getLabelData(signals.GPS_Long.name)
        gps_lat_csv = log2.getLabelData(signals.GPS_Lat.name)
        gps_alt_csv = log2.getLabelData(signals.GPS_Alt.name)
        gps_time_csv = log2.getLabelData(signals.GPS_Time.name)
        internal_temp_csv = log2.getLabelData(signals.INTERNAL_AIR_TEMP.name)
        vin_csv = log2.getLabelData(signals.VIN.name)

        self.assertTrue(log2.isBrokenFile())
        self.assertEqual(speed_csv, speed)
        self.assertEqual(afr_csv, afr)
        self.assertEqual(temp_csv, temp)
        self.assertEqual(rpm_csv, rpm)
        self.assertEqual(load_csv, load)
        self.assertEqual(maf_csv, maf)
        self.assertEqual(pedal_csv, pedal)
        self.assertEqual(fuel_lvl_csv, fuel_lvl)
        self.assertEqual(gps_long_csv, gps_long)
        self.assertEqual(gps_lat_csv, gps_lat)
        self.assertEqual(gps_alt_csv, gps_alt)
        self.assertEqual(gps_time_csv, gps_time)
        self.assertEqual(internal_temp_csv, internal_temp)
        self.assertEqual(vin_csv, vin)
        self.assertEqual(log2._VIN, "MF0DXXGAKDJP09111")

    def test_without_GPSFile(self):
        log = LogFile()
        log.loadFromFile("Random_NoGPS.test")
        time = log.getStartTime()
        end = log.getEndTime()
        fuel = log.getFuelConsumption()
        self.assertTrue(fuel is not None)
        self.assertEqual(time, "01-01-2000;00:00:00")
        self.assertEqual(end, "01-01-2000;00:00:00")

    def test_createRandomDataFile(self):
        log = LogFile()
        log.createLogfile("Random.test")
        time = range(100)
        speed = np.random.randint(100, size=100).tolist()
        rpm = np.random.randint(5000, size=100).tolist()
        load = np.random.randint(100, size=100).tolist()
        maf = np.random.randint(100, size=100).tolist()
        temp = np.random.randint(30, size=100).tolist()
        pedal = np.random.randint(100, size=100).tolist()
        afr = np.random.randint(1, size=100).tolist()
        fuel_lvl = np.random.randint(100, size=100).tolist()
        gps_long = np.random.randint(10, size=100).tolist()
        gps_lat = np.random.randint(50, size=100).tolist()
        gps_alt = np.random.randint(300, size=100).tolist()
        gps_time = ["2019-03-17T09:24:28.000Z"] * 100
        internal_temp = np.random.randint(30, size=100).tolist()
        vin = ["MF0DXXGAKDJP09111"] * 100
        for i in  range(0, len(speed)):
                log.addData([time[i], speed[i], rpm[i], load[i], maf[i], temp[i], pedal[i], afr[i], fuel_lvl[i], gps_long[i], gps_lat[i], gps_alt[i], gps_time[i], internal_temp[i], vin[i] ])

        log.appendFile()
        log2 = LogFile()
        log2.loadFromFile(log.getfilename())
        speed_csv = log2.getLabelData(signals.SPEED.name)
        afr_csv = log2.getLabelData(signals.COMMANDED_EQUIV_RATIO.name)
        temp_csv = log2.getLabelData(signals.AMBIANT_AIR_TEMP.name)
        rpm_csv = log2.getLabelData(signals.RPM.name)
        load_csv = log2.getLabelData(signals.ENGINE_LOAD.name)
        maf_csv = log2.getLabelData(signals.MAF.name)
        pedal_csv = log2.getLabelData(signals.RELATIVE_ACCEL_POS.name)
        fuel_lvl_csv = log2.getLabelData(signals.FUEL_LEVEL.name)
        gps_long_csv = log2.getLabelData(signals.GPS_Long.name)
        gps_lat_csv = log2.getLabelData(signals.GPS_Lat.name)
        gps_alt_csv = log2.getLabelData(signals.GPS_Alt.name)
        gps_time_csv = log2.getLabelData(signals.GPS_Time.name)
        internal_temp_csv = log2.getLabelData(signals.INTERNAL_AIR_TEMP.name)
        vin_csv = log2.getLabelData(signals.VIN.name)

        self.assertFalse(log2.isBrokenFile())
        self.assertEqual(speed_csv, speed)
        self.assertEqual(afr_csv, afr)
        self.assertEqual(temp_csv, temp)
        self.assertEqual(rpm_csv, rpm)
        self.assertEqual(load_csv, load)
        self.assertEqual(maf_csv, maf)
        self.assertEqual(pedal_csv, pedal)
        self.assertEqual(fuel_lvl_csv, fuel_lvl)
        self.assertEqual(gps_long_csv, gps_long)
        self.assertEqual(gps_lat_csv, gps_lat)
        self.assertEqual(gps_alt_csv, gps_alt)
        self.assertEqual(gps_time_csv, gps_time)
        self.assertEqual(internal_temp_csv, internal_temp)
        self.assertEqual(vin_csv, vin)
        self.assertEqual(log2._VIN, "MF0DXXGAKDJP09111")

    def test_createZerosDataFile(self):
        log = LogFile()
        log.createLogfile("Zeros.test")
        time = range(100)
        speed = [0]*100
        rpm = [0]*100
        load = [0]*100
        maf = [0]*100
        temp = [0]*100
        pedal = [0]*100
        afr = [0]*100
        fuel_lvl = [None]*100
        gps_long = [None]*100
        gps_lat = [None]*100
        gps_alt = [None]*100
        gps_time = [None]*100
        internal_temp = [None]*100
        vin = ["VIN12FBASSF13"] * 100
        for i in  range(0, len(speed)):
                log.addData([time[i], speed[i], rpm[i], load[i], maf[i], temp[i], pedal[i], afr[i], fuel_lvl[i], gps_long[i], gps_lat[i], gps_alt[i], gps_time[i], internal_temp[i], vin[i] ])

        log.appendFile()
        
        log2 = LogFile()
        log2.loadFromFile(log.getfilename())
        speed_csv = log2.getLabelData(signals.SPEED.name)
        afr_csv = log2.getLabelData(signals.COMMANDED_EQUIV_RATIO.name)
        temp_csv = log2.getLabelData(signals.AMBIANT_AIR_TEMP.name)
        rpm_csv = log2.getLabelData(signals.RPM.name)
        load_csv = log2.getLabelData(signals.ENGINE_LOAD.name)
        maf_csv = log2.getLabelData(signals.MAF.name)
        pedal_csv = log2.getLabelData(signals.RELATIVE_ACCEL_POS.name)
        fuel_lvl_csv = log2.getLabelData(signals.FUEL_LEVEL.name)
        gps_long_csv = log2.getLabelData(signals.GPS_Long.name)
        gps_lat_csv = log2.getLabelData(signals.GPS_Lat.name)
        gps_alt_csv = log2.getLabelData(signals.GPS_Alt.name)
        gps_time_csv = log2.getLabelData(signals.GPS_Time.name)
        internal_temp_csv = log2.getLabelData(signals.INTERNAL_AIR_TEMP.name)
        vin_csv = log2.getLabelData(signals.VIN.name)
        
        self.assertTrue(log2.isBrokenFile())
        self.assertEqual(speed_csv, speed)
        self.assertEqual(afr_csv, afr)
        self.assertEqual(temp_csv, temp)
        self.assertEqual(rpm_csv, rpm)
        self.assertEqual(load_csv, load)
        self.assertEqual(maf_csv, maf)
        self.assertEqual(pedal_csv, pedal)
        self.assertEqual(fuel_lvl_csv, fuel_lvl)
        self.assertEqual(gps_long_csv, gps_long)
        self.assertEqual(gps_lat_csv, gps_lat)
        self.assertEqual(gps_alt_csv, gps_alt)
        self.assertEqual(gps_time_csv, gps_time)
        self.assertEqual(internal_temp_csv, internal_temp)
        self.assertEqual(vin_csv, vin)

    
    def test_isBrokenFile_NoRPM(self):
        log = LogFile()
        log.loadFromFile("Zeros.test")
        broken = log.isBrokenFile()
        self.assertTrue(broken)

    def test_isBrokenFile_OK(self):
        log = LogFile()
        log.loadFromFile("Random.test")
        broken = log.isBrokenFile()
        self.assertFalse(broken)
        
    def test_StatusLogFileLoaded(self):
        log = LogFile()
        log.loadFromFile("Random.test")
        self.assertEqual(log.status(), LogStatus.LOG_FILE_LOADED)

    def test_isBrokenFile_NoGPS(self):
        log = LogFile()
        log.loadFromFile("Random_NoGPS.test")
        broken = log.isBrokenFile()
        self.assertTrue(broken)

    def test_getDistance(self):
        log = LogFile()
        log.loadFromFile("Random.test")

        self.assertTrue(log.getDistance() is not None)
    
    def test_getHashedVin(self):
        log = LogFile()
        log.loadFromFile("Random.test")

        self.assertTrue(log.getHashedVIN is not None)

    def test_getEnergyCons(self):
        log = LogFile()
        log.loadFromFile("Random.test")

        self.assertTrue(log.getEnergyCons is not None)

if __name__ == '__main__':

    unittest.main()