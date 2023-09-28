#!/bin/bash

sleep 15s

echo
echo -n 1. Mounting USB storage device...
sudo mount /dev/sda1 /media/usb
echo Done

sleep 5s

echo -n 2. Stopping Ueye deamons...
sudo systemctl stop ueyeusbdrc
sudo systemctl stop ueyeethdrc
echo Done

sleep 20s

echo -n 3. Restarting Ueye deamons...
sudo systemctl start ueyeusbdrc
sudo systemctl start ueyeethdrc
echo Done

sleep 20s

echo -n 4. Running the PyCamera script...
python3 /home/pi/PyCamera_control/main/PyCamera.py
echo
