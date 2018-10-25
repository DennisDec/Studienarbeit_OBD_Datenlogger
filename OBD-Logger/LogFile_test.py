from LogFile import LogFile, SupportedLabels, LogStatus

import unittest
import time
import datetime

filename = 'Unittest.csv'



class TestLogFile(unittest.TestCase):

    def test_StatusNoLogFile(self):
        log = LogFile()
        self.assertEquals(log.status(), LogStatus.NO_LOGFILE)

    def test_StatusLogCreated(self):
        log = LogFile()
        log.createLogfile(filename, ["Time", "Speed", "RPM"])
        self.assertEquals(log.status(), LogStatus.LOG_CREATED)

    def test_StatusLogFileLoaded(self):
        log = LogFile()
        log.loadFromFile(filename)
        self.assertEquals(log.status(), LogStatus.LOG_FILE_LOADED)

    def test_getFilenames(self):
        LogFile.getFilenames()
        self.assertTrue(isinstance(LogFile.getFilenames(), list))

    def test_IsCorrectSpeedList(self):
        log = LogFile()
        log.createLogfile(filename, ["Time", "Speed", "RPM"])

        t1 = str(datetime.datetime.now())
        t2 = str(datetime.datetime.now())

        log.addData(t1, 30, 2400, 12, 2, 4, 5, 6, 7)
        log.addData(t2, 40, 2600, 23 ,24, 34 , 3, 6, 67)

        log.appendFile()

        log2 = LogFile()
        log2.loadFromFile(filename)

        speed = log2.getLabelData(SupportedLabels.SPEED)
        self.assertEqual(speed, [30, 40])


if __name__ == '__main__':
    unittest.main()
