@echo off
rem batch file to test iterative plating and impedance measuring [pd 2025.02]
rem takes 2 arguments: the row [0..15] and column [0..31] of the channel to be tested
set r=%1
set c=%2
rem load sinewave file
write_daclut_file EC3sine.txt
set /A write_row=110848+%r%
set /A write_col=111104+%c%
rem pixel register is 0x1B000 + 3 (gain) + either 16 (plate up) OR 32 (plate down)
set write_pix=110611
rem for turning the pixel off
set write_pox=110595
rem Desired plating current DAC setting = 0 to 31
rem dac_val should be 110592 + DAC setting. Set that number (don't make DOS add!) below
set dac_val=110623
set dac_reg=111172
set write_reg=111368
set Tok1=131073

set ntimes=3
set twait=1

for /L %%g in (1,1,%ntimes%) do (
	echip_write %Tok1%
	rem set the dac plating value
	echip_write %dac_val%
	echip_write %dac_reg%
	
	rem set the pixel value
	echip_write %write_reg%
	echip_write %write_pix%
	echip_write %write_row%
	echip_write %write_col%
	echip_write %write_reg%
	
rem turn plating on for twait
	timeout /t %twait%
	
	rem turn plating off
	echip_write %write_pox%
	echip_write %write_reg%
	rem turn on sinewave generation for impedance measurement
	set_zparameters -g 4 -m 0 -r %r% -c %c% -s 192
	run_zmeasurement 1
rem	echip_write %Tok1%
	rem at 1 kHz, ~30 point per cycle - grab 100-200 cycles
	streamUSB -c 512 -p 6000
	run_zmeasurement 0
	move /y hsdata.dat z%r%%c%%%g%.dat
)