@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem batch file to test iterative plating and impedance measuring across all channels [pd 2025.02]

rem ---------------------------
rem Config (edit as needed)
rem ---------------------------
set ntimes=3
set twait=5

rem Desired plating current DAC setting = 0..31
rem dac_val must be 110592 + DAC_setting (precompute; do NOT use set /A here)
set dac_val=110623   rem 110592 + 31 (max)

rem ---------------------------
rem Constants (registers/tokens)
rem ---------------------------
set Tok1=131073
set write_pix=110611
set write_pox=110595
set dac_reg=111172
set write_reg=111368

rem Base addresses for row/col selection
rem write_row = 110848 + r ; write_col = 111104 + c
set row_base=110848
set col_base=111104

rem ---------------------------
rem One-time setup
rem ---------------------------
write_daclut_file EC3sine.txt

rem ---------------------------
rem Iterate over all rows and columns
rem ---------------------------
for /L %%r in (0,1,15) do (
  for /L %%c in (0,1,31) do (

    rem Precompute per-channel row/col registers
    set /A write_row=!row_base!+%%r
    set /A write_col=!col_base!+%%c

    echo Processing channel r=%%r c=%%c

    for /L %%g in (1,1,%ntimes%) do (
      set "iter=%%g"
      echo   Iteration !iter! of %ntimes% on r=%%r c=%%c
      rem Initialize / preamble
      echip_write %Tok1%

      rem Program plating DAC
      echip_write %dac_val%
      echip_write %dac_reg%

      rem Select target pixel & turn plating ON
      echip_write %write_reg%
      echip_write %write_pix%
      echip_write !write_row!
      echip_write !write_col!
      echip_write %write_reg%

      rem Plating dwell
      timeout /t %twait% >nul

      rem Turn plating OFF
      echip_write %write_pox%
      echip_write %write_reg%

      rem Configure impedance measurement for this channel
      set_zparameters -g 4 -m 0 -r %%r -c %%c -s 192
      run_zmeasurement 1

      rem Acquire data (adjust counts to taste)
      rem At 1 kHz, ~30 pts/cycle — this captures ~100–200 cycles
      streamUSB -c 512 -p 6000

      rem Stop impedance measurement
      run_zmeasurement 0

      rem Save with unique per-iteration filename
      rem Example: z0311.dat -> r=0, c=31, iter=1
      move /y hsdata.dat C:\Users\lorenlab\Desktop\kyu\echip\new_scripts\plating_data\z%%r%%c%%g.dat >nul
    )
  )
)

endlocal
