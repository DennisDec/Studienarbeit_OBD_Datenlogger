# pylint: disable=no-member
from LogFile import LogFile
import subprocess
import signal
import time
import os
import socket
import env
import shutil

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
    print(files)
    for file in files:
        log.loadFromFile(file)
        filename = log.transferToJson()
        print(filename)
        if(log.copyFileToServer(filename)):
            print("Success!!")
            with open( env.PATH + "LOG.log", "a") as f:
                f.write("Success: " + str(file) "(" + str(filename) ") has been copied to Server")
            if os.path.exists(env.PATH + file):
                shutil.copy2(env.PATH + file, env.PATH + "OLD/")
                print("copy file to old folder")
                os.remove(env.PATH  + file)
                print("[DELETE] " + str(file))
            if os.path.exists(env.PATH + "JSON/" +  filename):
                os.remove(env.PATH  + "JSON/" + filename)
                print("[DELETE] " + str(filename))
        with open( env.PATH + "LOG.log", "a") as f:
            f.write("Error: " + str(file) "(" + str(filename) ") could not be copied to Server")

except Exception as ex:
    print(ex)
finally:
    signal.alarm(0)
    


