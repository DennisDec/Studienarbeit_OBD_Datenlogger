import subprocess
try:
    output = subprocess.check_output(('ping -q -c 1 -W 1 8.8.8.8'), shell=True)
    print(output)
except subprocess.CalledProcessError:
    print("No wireless networks connected")