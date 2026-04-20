import sys,struct
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import numpy as np
from scipy.fft import fft

# Create a root window
root = tk.Tk()
root.withdraw()  # Hide the main root window

file_path = filedialog.askopenfilename(title="Select a file")

# Check if a file was selected
if file_path:
    print("Selected file:", file_path)
else:
    print("No file selected")
    sys.exit()

root.destroy() # Close the root window

chan2plot=int(sys.argv[1])
"""
#####################################################################################
# rmchan.py - read Magnus' files * pd 2026.04
# 1 argument: channel to plot
# python -m pip install -U matplotlib
#####################################################################################
"""

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

f = open(file_path, 'rb')
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

if (chan2plot == -1):
    plt.ion() # enables interactive mode

    for i in range(int(Nframes)):
        chn[i]=hso[channel_order[0]+512*i]
    graph=plt.plot(chn)
    for k in range(32):
        for i in range(int(Nframes)):
            chn[i]=hso[channel_order[k+480]+512*i]
        
        graph,=plt.plot(chn)
        plt.title("Chan"+str(k+480))
        plt.pause(1)
        graph.remove()
else:
    for i in range(int(Nframes)):
        chn[i]=hso[channel_order[chan2plot]+512*i]
    F=fft(chn)
    M=np.abs(F)
    mx=0
    for k in range(int(len(M)/2-1)):
        if(M[k+1] > mx):
            mx=M[k+1]
            jdex=k+1
    AmplMax=mx/len(M) # amplitude
    FreqMax=30000 / (len(M)/jdex)
    print(f"FFT max at point {jdex} = {FreqMax:.1f} Hz with amplitude {AmplMax:.1F} ADU")
    plt.plot(chn)
    plt.show()