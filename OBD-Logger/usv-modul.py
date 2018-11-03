from LogFile import LogFile, LogStatus, SupportedLabels
import subprocess
import signal
import time

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
signal.alarm(10)

try:
    connectToWIFI()
except Exception as ex:
    print(ex)
finally:
    signal.alarm(0)
    log = LogFile()
    files = LogFile.getFilenames()
    print(files[1])
    log.transmitToSQL(files[1])
    


