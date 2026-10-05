import subprocess
import sys
import time

#
# plate all channels as per Allison's guidance: 10 nA for 45s
#

dbg_print=0

def echip_write(d:int):
    w="echip_write "+str(d)
    WriteCMD(w)

def WriteDAC(d:int):    # d is DAC value
    echip_write(int("0x1B000",16)+d)
    echip_write(int("0x1B244",16))    # DAC address 
    echip_write(int("0x1B308",16))    # Write
    
def WriteCMD(w:str):
    global dbg_print
    subprocess.run(w)
    if dbg_print==1:
        print(w)
        
# set all pixels to plate up
print("Setting Plate UP",end="",flush=True)
#WriteCMD("register_write G20UP_2nd64.txt") 
WriteCMD("register_write G20UP.txt") 
#        xxxxxxxxxxxxxxxxxx
print("\rPlating On        \r",end="",flush=True)
WriteDAC(2) # nom. 2 for 10 nA
time.sleep(45)
echip_write(int("0x1A340",16)) # RESET
print("\rPlating Off       \r",end="",flush=True)
WriteCMD("register_write G20.txt") 
