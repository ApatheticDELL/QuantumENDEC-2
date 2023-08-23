import threading, os, time
#QUANTUMENDEC LAUNCH FILE

print("QuantumENDEC")
print("Version 2: The Python Edition")
print("")
print("Devloped by...")
print("Dell ... ApatheticDELL")
print("Aaron ... secludedcfox.com :3")
print("BunnyTub ... gadielisawesome")

time.sleep(4)

os.remove("SameHistory.txt")

dir = 'XMLhistory'
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))


# start capture.py and relay.py and loop them

def startRelay():
    while True:
        os.system("python3 relay.py")
        time.sleep(0.1)

def startCapture():
    while True:
        os.system("python3 capture.py")
        time.sleep(0.1)


captureThread = threading.Thread(target=startCapture)
captureThread.start()

relayThread = threading.Thread(target=startRelay)
relayThread.start()

while True:
    time.sleep(100)
    # dont ask just keeps the file alive

