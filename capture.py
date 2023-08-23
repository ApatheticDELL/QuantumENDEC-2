import os
import sys
import time
import pathlib
import socket
import shutil
import datetime
import re

os.system('cls' if os.name == 'nt' else 'clear')

while True:
    TCP_IP = "streaming1.naad-adna.pelmorex.com"
    TCP_PORT = 8080
    BUFFER_SIZE = 100000
    NAAD1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    NAAD1.connect((TCP_IP, TCP_PORT))
    print("WE ARE CONNECTED TO PELMOREX NAAD 1")
    print(NAAD1)
    NAAD1.settimeout(90)
    
    try:
        data = str(NAAD1.recv(BUFFER_SIZE),encoding='utf-8', errors='ignore')
    except socket.timeout:
        print("ERROR - Timed out, trying again. Maybe check your network connection?")
        NAAD1.close()
        time.sleep(3)
        break
    else:
        #print(str(data))
        # - to _
        # + to p
        # : to _
        #ONLY IN sent AND ident
        
        try:
            sent = re.search(r"<sent>\s*(.*?)\s*</sent>", str(data), re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            sent = sent.replace("-","_").replace("+", "p").replace(":","_")
            print("sent =", str(sent))
        except:
            print("somthing brokey :P")
        
        try:
            identifier = re.search(r"<identifier>\s*(.*?)\s*</identifier>", str(data), re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            identifier = identifier.replace("-","_").replace("+", "p").replace(":","_")
            print("sent =", str(identifier))
        except:
            print("somthing really brokey :P")

        timeQ = f"XMLprocess/{sent}I{identifier}.xml"
        timeX = f"XMLqueue/{sent}I{identifier}.xml"
        print(f"{timeQ}\n{timeX}")

        alert = open(timeQ, 'a')
        alert.write(str(data))
        
        while '</alert>' not in data:
            data = str(NAAD1.recv(BUFFER_SIZE),encoding='utf-8', errors='ignore')
            #print(str(data))
            alert.write(str(data))
                
        alert.close()
        shutil.move(timeQ, timeX)
        print(time.strftime("Transmission recived at %H:%M:%S on %d/%m/%Y"))
    NAAD1.close()
    
#This is like the code above, but preformed just incase NAADs 1 fails
TCP_IP = "streaming2.naad-adna.pelmorex.com"
TCP_PORT = 8080
BUFFER_SIZE = 100000
NAAD2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
NAAD2.connect((TCP_IP, TCP_PORT))
print("WE ARE CONNECTED TO PELMOREX NAAD 2")
print(NAAD2)
NAAD2.settimeout(90)
   
try:
    data = str(NAAD2.recv(BUFFER_SIZE),encoding='utf-8', errors='ignore')
except socket.timeout:
    os.system('cls' if os.name == 'nt' else 'clear')
    print("ERROR - Timed out, trying again. Maybe check your network connection?")
    NAAD2.close()
    time.sleep(3)
else:
    #print(str(data))

    try:
        sent = re.search(r"<sent>\s*(.*?)\s*</sent>", str(data), re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        sent = sent.replace("-","_").replace("+", "p").replace(":","_")
        print("sent =", str(sent))
    except:
        print("somthing brokey :P")
        
    try:
        identifier = re.search(r"<identifier>\s*(.*?)\s*</identifier>", str(data), re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        identifier = identifier.replace("-","_").replace("+", "p").replace(":","_")
        print("sent =", str(identifier))
    except:
        print("somthing really brokey :P")
    
    timeQ = f"XMLprocess/{sent}I{identifier}.xml"
    timeX = f"XMLqueue/{sent}I{identifier}.xml"
    print(f"{timeQ}\n{timeX}")

    alert = open(timeQ, 'a')
    alert.write(str(data))
      
    while '</alert>' not in data:
        data = str(NAAD2.recv(BUFFER_SIZE),encoding='utf-8', errors='ignore')
        #print(str(data))
        alert.write(str(data))
                
    alert.close()
    shutil.move(timeQ, timeX)
    print(time.strftime("Transmission recived at %H:%M:%S on %d/%m/%Y"))
NAAD2.close()

#867-5309 :3
