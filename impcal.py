import sys,struct
import numpy as np
from scipy.fft import fft
import math
import subprocess

#####################################################################################
# impcal.py * pd 2026.04
# simple "impedance" calc by looking for amplitude of FFT
#####################################################################################
dbg_print=0

def echip_write(d:int):
    w="echip_write "+str(d)
    WriteCMD(w)
    
def WriteCMD(w:str):
    global dbg_print
    subprocess.run(w)
    if dbg_print==1:
        print(w)
        
channel_order=[0]*512
for j in range(16):
    m=0
    for i in range(8):
        k=32*j+4*i
        channel_order[32*j+m]=k
        channel_order[32*j+m+1]=k+1
        channel_order[32*j+m+16]=k+2
        channel_order[32*j+m+17]=k+3
        m+=2
        
ShiftBy=2

# load the sine wave file
subprocess.run("write_daclut_file EC3sine.txt")

# just to be sure, load defalt file
print("Programming echip")
WriteCMD("register_write G20.txt")

fout=open("impedance.txt","w")

for channel in range(480,512):
    TheRow=math.floor(channel/32)
    TheCol=channel % 32
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
    
    f = open("hsdata.dat", 'rb')
    bin = f.read()
    f.close()
    FiLen=len(bin)
    Nframes=FiLen/1038
    print("File read. Length="+str(FiLen)+" bytes. Number of frames="+str(Nframes))

    hso=[0]*512
    tmp=[0]*512
    chn=[0]*int(Nframes)

    for i in range(int(Nframes)):
        v=struct.unpack_from('<H3I512H',bin,i*1038)
        # < little endian, H unsigned short, i is signed (4 byte) I is unsigned
        if v[0] != 0xbf55:
            print("Bad header in frame "+str(i)+" "+str(v[0]))
        if i == 0:
            for j in range(512):
                hso[j]=v[4+j]
        else:
            for j in range(512):
                tmp[j]=v[4+j] 
            hso.extend(tmp)  
            
    for i in range(int(Nframes)):
        chn[i]=hso[channel_order[channel]+512*i]
    F=fft(chn)
    M=np.abs(F)
    mx=0
    for k in range(int(len(M)/2-1)):
        if(M[k+1] > mx):
            mx=M[k+1]
            jdex=k+1
    AmplMax=mx/len(M) # amplitude
    FreqMax=30000 / (len(M)/jdex)
    OutStr=f"Channel {channel} FFT max at point {jdex} = {FreqMax:.1f} Hz with amplitude {AmplMax:.1F} ADU"
    print("*************************************************************************************************")
    print(OutStr)
    print("*************************************************************************************************")
    fout.write(OutStr+"\n")
    
fout.close()