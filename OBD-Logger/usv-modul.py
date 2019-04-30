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

with open( env.PATH + "LALA.log", "a") as f:
    f.write("ltest123\n")
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(20)



try:
    #connectToWIFI()
    #TODO: Add for - Loop here
    print(env.PATH)
    log = LogFile()
    files = LogFile.getFilenames()
    print(files)
    for file in files:
        log.loadFromFile(file)
        filename = log.transferToJson()
        print(filename)
        
        success, err = log.copyFileToServer(filename)
        print(success)
        print(err)
        if(success):
            print("Success!!")
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
            with open( env.PATH + "LOG.log", "a") as f:
                f.write("Error: " + str(file) + "(" + str(filename) + ") could not be copied to Server: "+ str(err) + "\n")

except Exception as ex:
    print(ex)
finally:
    signal.alarm(0)