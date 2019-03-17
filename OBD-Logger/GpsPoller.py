import os 
from gps import *
import gps
from time import *
import time 
import threading 

class GpsPoller(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        os.system("sudo gpsd /dev/serial0 -F /var/run/gpsd.sock")

        self.session = gps.gps("localhost", "2947")
        self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        self.current_value = None 
        self.running = True 
        
    def get_current_value(self):
            return self.current_value
        
    def run(self):
        try:
            while self.running:
                self.current_value = self.session.next() 
        except StopIteration:
            pass
            