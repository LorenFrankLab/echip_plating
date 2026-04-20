import subprocess
import sys
import time
# python translation to test iterative plating and impedance measuring [pd 2025.02 -> 2026.03]
# takes 3 arguments: the row [0..15] and column [0..31] of the channel to be tested and non-zero to do impedance measurement

TheRow=int(sys.argv[1])
TheCol=int(sys.argv[2])
DoImp=int(sys.argv[3])

dbg_print=1
# From Alison, 45 sec at 10 nA
plate_current=10    # nA
plate_dac=int(32*plate_current/200)
plate_time=45        # seconds
ntimes=1

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
        
# load the sine wave file
if (DoImp != 0):
    subprocess.run("write_daclut_file EC3sine.txt")

# just to be sure, load defalt file
WriteCMD("register_write G20.txt")

# plating loop
echip_write(int("0x20001",16))  # Token=1
for i in range(ntimes):
    WriteDAC(plate_dac)
    echip_write(int("0x1B000",16)+3+16)     # Gain 20 Plate UP
    echip_write(int("0x1B100",16)+TheRow)   # set row
    echip_write(int("0x1B200",16)+TheCol)   # set col
    echip_write(int("0x1B308",16))          # write
    print("Plate ON")
    time.sleep(plate_time)
    echip_write(int("0x1B000",16)+3)        # Gain 20 no plate
    echip_write(int("0x1B308",16))          # write
    if (DoImp != 0):
        # measure on gain 5 (G=10 ==> -g 4)
        w="set_zparameters -g 5 -m 0 -r "+str(TheRow)+" -c "+str(TheCol)+" -s 192"
        WriteCMD(w)
        w="run_zmeasurement 1"
        WriteCMD(w)
        echip_write(int("0x20001",16))  # Token=1
        # at 1 kHz, ~30 point per cycle - grab 100-200 cycles
        w="streamUSB -c 512 -p 6000"
        WriteCMD(w)
        w="run_zmeasurement 0"
        WriteCMD(w)
        out_name = f"z{TheRow:02d}{TheCol:02d}{i}.dat"
        out_dir  = r"C:\Users\lorenlab\Desktop\kyu\echip\new_scripts\plating_data"
        import shutil, os
        #shutil.move("hsdata.dat", os.path.join(out_dir, out_name))
        shutil.move("hsdata.dat",out_name)
