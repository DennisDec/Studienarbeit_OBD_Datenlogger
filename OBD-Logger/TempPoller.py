import os 
from gps import *
import gps
from time import *
import time 
import threading 
import glob
import RPi.GPIO as GPIO


class TempPoller(threading.Thread):
    """
    Thread:
    This class is responsible for reading the latetest temperature values from DS18BD temperature sensor.
    Usage:
    temp = TempPoller()
    temp.start()

    temp.get_current_value()  #To get the latetst value
    """
    
    def __init__(self):
        threading.Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        base_dir = '/sys/bus/w1/devices/'

        device_folder = None

        try:
            device_folder = glob.glob(base_dir + '28*')[0]
        except IndexError:
            device_folder = None
        print(device_folder)

        if (device_folder != None):
            self.device_file = device_folder + '/w1_slave'
            self.TemperaturMessung(self.device_file)
        else:
            self.device_file = None
        print(self.device_file)
        
        self.current_value = None 
        self.running = True 
        
    def get_current_value(self):
            return self.current_value
        
    def run(self):
        try:
            while self.running:
                self.current_value = self.TemperaturAuswertung(self.device_file)
                time.sleep(2)
        except StopIteration:
            pass


    def TemperaturMessung(self, device_file):
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def TemperaturAuswertung(self, device_file):
        if (device_file != None):
            lines = self.TemperaturMessung(device_file)
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.1)
                lines = self.TemperaturMessung(device_file)
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c
            else:
                return None
        else:
            return None
