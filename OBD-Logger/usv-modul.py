# pylint: disable=no-member
from LogFile import LogFile
import subprocess
import signal
import time
import os
import socket
import env
import shutil
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(19,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)
GPIO.output(21, GPIO.HIGH)

def timeout_handler(num, stack):
    print("Received SIGALRM")
    raise Exception("No wireless networks connected")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(20)



try:
    print(env.PATH)
    log = LogFile()
    files = LogFile.getFilenames()
    print(files)
    for file in files:        
        log.loadFromFile(file)
        #Delete Files without content
        if(log.isBrokenFile()):
            if os.path.exists(env.PATH + file):
                os.remove(env.PATH  + file)
                print("[DELETE] broken file: " + str(file))
                with open( env.PATH + "LOG.log", "a") as f:
                    f.write("[DELETE]: " + str(file) +  " - File was broken (No GPS or RPM signals) "+ "\n")
            continue
        filename = log.transferToJson()
        print(filename)
        success, err = log.copyFileToServer(filename)
        print(success)
        print(err)
        if(success):
            print("Success!!")
            GPIO.output(19, GPIO.HIGH)
            with open( env.PATH + "LOG.log", "a") as f:
                f.write("Success: " + str(file) + "(" + str(filename) + ") has been copied to Server\n")
            if os.path.exists(env.PATH + file):
                shutil.copy2(env.PATH + file, env.PATH + "OLD/")
                print("copy file to old folder")
                os.remove(env.PATH  + file)
                print("[DELETE] " + str(file))
            if os.path.exists(env.PATH + "JSON/" +  filename):
                os.remove(env.PATH  + "JSON/" + filename)
                print("[DELETE] " + str(filename))
            
        else:
            GPIO.output(23, GPIO.HIGH)
            with open( env.PATH + "LOG.log", "a") as f:
                f.write("Error: " + str(file) + "(" + str(filename) + ") could not be copied to Server: "+ str(err) + "\n")
                
except Exception as ex:
    print(ex)
    for i in range(3):
        GPIO.output(23, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(23, GPIO.LOW)
        time.sleep(0.1)
finally:
    time.sleep(1)
    GPIO.output(23, GPIO.LOW)
    GPIO.output(19, GPIO.LOW)
    GPIO.output(21, GPIO.LOW)
    signal.alarm(0)
    


