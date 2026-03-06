::register_write_usb.exe global_dac2.txt ::write global DACs (eg. BiasAAF)
register_write_usb.exe global_dac2.txt
timeout /t 1
set_threshold 65535 ::turn off deblipper
timeout /t 1
write_daclut_file.exe sine1khz.txt
timeout /t 1
:: 1khz -> s=192
set_zparameters.exe -g 4 -m 1 -r 14 -c 0 -s 192
timeout /t 1
run_zmeasurement.exe 1 ::start measurement
::measure output to a scope across 1Mohm resistor
timeout /t 1
streamUSB.exe -c 512 -p 1000
timeout /t 1
python plot_echip_data.py hsdata.dat 448
timeout /t 1
run_zmeasurement.exe 0 ::stop measurement

::register_write_usb.exe ..\register_files\archive\no_clamp_gain\gain10.txt