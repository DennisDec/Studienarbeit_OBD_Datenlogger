from LogFile import LogFile, LogStatus, Stringbuilder
# pylint: disable=no-member
import unittest
import time
import datetime
from OBDSignal import OBDSignal 

from Signals import signals

filename = 'Unittest.csv'

class TestLogFile(unittest.TestCase):

    def test_SQL(self):
        print(Stringbuilder.SqlBuidler("test"))
        

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
        log.createLogfile(filename)
        self.assertEqual(log.status(), LogStatus.LOG_CREATED)

    def test_StatusLogFileLoaded(self):
        log = LogFile()
        log.loadFromFile(filename)
        self.assertEqual(log.status(), LogStatus.LOG_FILE_LOADED)

    def test_getFilenames(self):
        LogFile.getFilenames()
        self.assertTrue(isinstance(LogFile.getFilenames(), list))

    def test_IsCorrectSpeedList(self):
        log = LogFile()
        log.createLogfile(filename)

        t1 = str(datetime.datetime.now())

        #Test values 
        speed = [34, None, 36, 24, None, 56]
        rpm = [2000, 2001, 2100, 3100, 50000, 60000]
        load = [60, 40, 35, 30, 70, 80]
        maf = [3, 4, 3, 4, 3, 2]
        temp = [13,13,13,14,14,14]
        pedal = [30,33,24,36,21, 18]
        afr =[1, 1.2, 1.1, 1, 1, 1]
        fuel_lvl = [80, 80, 80, 79, 79, 79]
       
        for i in  range(0, len(speed)):
            log.addData([t1, speed[i], rpm[i], load[i], maf[i], temp[i], pedal[i], afr[i], fuel_lvl[i]])
            

        log.appendFile()
        
        log2 = LogFile()
        log2.loadFromFile(filename)

        speed_csv = log2.getLabelData(signals.SPEED.name)
        afr_csv = log2.getLabelData(signals.COMMANDED_EQUIV_RATIO.name)
        temp_csv = log2.getLabelData(signals.AMBIANT_AIR_TEMP.name)
        rpm_csv = log2.getLabelData(signals.RPM.name)
        load_csv = log2.getLabelData(signals.ENGINE_LOAD.name)
        maf_csv = log2.getLabelData(signals.MAF.name)
        pedal_csv = log2.getLabelData(signals.RELATIVE_ACCEL_POS.name)
        fuel_lvl_csv = log2.getLabelData(signals.FUEL_LEVEL.name)

        self.assertEqual(speed_csv, speed)
        self.assertEqual(afr_csv, afr)
        self.assertEqual(temp_csv, temp)
        self.assertEqual(rpm_csv, rpm)
        self.assertEqual(load_csv, load)
        self.assertEqual(maf_csv, maf)
        self.assertEqual(pedal_csv, pedal)
        self.assertEqual(fuel_lvl_csv, fuel_lvl)


if __name__ == '__main__':
    unittest.main()
