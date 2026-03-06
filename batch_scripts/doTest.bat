@echo off
rem batch file to test iterative plating and impedance measuring [pd 2025.02]
rem takes 2 arguments: the row [0..15] and column [0..31] of the channel to be tested
set r=%1
set c=%2
rem load sinewave file

set /A write_row=110848+%r%
set /A write_col=111104+%c%
rem pixel register is 0x1B000 + 3 (gain) + either 16 (plate up) OR 32 (plate down)
set write_pix=110611
rem for turning the pixel off
set write_pox=110595
rem Desired plating current DAC setting = 0 to 31
set dac_val=110592+30
set dac_reg=111172
set write_reg=111368
set Tok1=131073

set ntimes=3
set twait=1
echip_write %Tok1%
for /L %%g in (1,1,%ntimes%) do (
	for /L %%d in (110592,1,110623) do (
	rem set the dac plating value
	echip_write %%d
	echip_write %dac_reg%
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

)
)