# pylint: disable=no-member
from LogFile import LogFile
import subprocess
import signal
import time
import os
import socket

def timeout_handler(num, stack):
    print("Received SIGALRM")
    raise Exception("No wireless networks connected")


def connectToWIFI():
    tmp = True
    while tmp == True:
        try:
            output = subprocess.check_output(('ping -q -c 1 -W 1 8.8.8.8'), shell=True)
            print(output)
            tmp = False
        except subprocess.CalledProcessError:
            print("No wireless networks connected")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(20)



try:
    #connectToWIFI()
    #TODO: Add for - Loop here
    log = LogFile()
    files = LogFile.getFilenames()
    print(files[2])
    log.loadFromFile(files[2])
    filename = log.transferToJson()
    print(filename)
    if(LogFile.copyFileToServer(filename)):
        print("Success!!")
    #TODO: Delete file after successful transmission
except Exception as ex:
    print(ex)
finally:
    signal.alarm(0)
    


