import subprocess
import sys
import time

#
# 1 argument: number of cycles
#

dbg_print=0

Ntimes=int(sys.argv[1])

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
    
def PlateUP():    # set every channel to plate up
    echip_write(int("0x1B000",16)+16)
    for r in range(16):
        echip_write(int("0x1B100",16)+r)
        for c in range(32):
            echip_write(int("0x1B200",16)+c)
            echip_write(int("0x1B308",16))
            
def PlateDN():    # set every channel to plate down
    echip_write(int("0x1B000",16)+32)
    for r in range(16):
        echip_write(int("0x1B100",16)+r)
        for c in range(32):
            echip_write(int("0x1B200",16)+c)
            echip_write(int("0x1B308",16))

rstep=1

#subprocess.run("register_write G20.txt")

for c in range(Ntimes):
    # set all pixels to plate up
    subprocess.run("register_write G20UP.txt")
    echip_write(int("0x20001",16))  # Token=1
    print(f"Cycle {c+1:2.0f} Up __",end="",flush=True)
    for d in range(0,32,rstep):
        print(f"\b\b{d:2.0f}",end="",flush=True)
        WriteDAC(d)
    for d in range(0,32,rstep):
        dd=31-d
        print(f"\b\b{dd:2.0f}",end="",flush=True)
        WriteDAC(dd) 
    # set all pixels to plate down
    subprocess.run("register_write G20DN.txt")
    echip_write(int("0x20001",16))  # Token=1
    print("\b\b\b\b\bDn __",end="",flush=True) 
    for d in range(0,32,rstep):
        print(f"\b\b{d:2.0f}",end="",flush=True)
        WriteDAC(d)
    for d in range(0,32,rstep):
        dd=31-d
        print(f"\b\b{dd:2.0f}",end="",flush=True)
        WriteDAC(dd)
    print("\r")
# set all pixels to not plate
subprocess.run("register_write G20.txt")