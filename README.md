# PyHoloCamera

# Introduction 

PyHoloCamera is a Python package which allows the user to remotely control a CMOS camera simply by means of a RaspberryPi 3/4 and a smartphone or tablet.
Thanks to the open–source RaspController application (openly available on Google Play at https://play.google.com/store/apps/details?id=it.Ettore.raspcontroller&gl=US&pli=1) it is possible to
control the system by any mobile device. For example, the RaspController application allows the user to control the general–purpose input/output (GPIO) ports for swithing external devices. Python
libraries such as GPIOzero are available and make the use easy enough to implement dedicated interfaces (https://gpiozero.readthedocs.io/en/stable/). By using RaspAP (open available at https://raspap.com/), a
feature–rich wireless router software working on many popular Debian–based devices, the instrument acts as a WI–Fi router to which the user connects from outside. We stress that RaspAP only works on Lite releases of
the Raspbian operative system (both 32–bits and 64–bits), i.e. without any graphical user interface. 

The package functionality was tested with the following CMOS sensors:
- ISD camera model GV-5260CP-M-GL
- IDS camera model UI-5240CP-M-GL

# Documentation

This README gives a brief overview of the key information required to install and run the software.

## Package setup

### IDS software suite

For IDS software (required to use the Ueye camera implemented in the system): from the official IDS website download the "IDS Software Suite" software for Linux ARM operating 
systems with 64-bit architecture, version v8 and "hard" floating point (https://en.ids-imaging.com/download-details/AB.0010.1.55500.23.html?os=linux_arm&version=v8&bus=64&floatcalc=hard)
It is recommended to download the archive version ('IDS Software Suite 4.96.1 for ARMv8 64-bit (hf) - archive file') and follow the instructions in the README file for proper installation. 

In summary: 

1) Install all the required IDS packages: 
```
sudo apt-get install debconf cmake libc6 libomp5 libatomic1 libstdc++6 libqt5opengl5 libqt5concurrent5 libqt5gui5 libqt5widgets5 build-essential libcap2 libusb-1.0-0 libqt5network5 libqt5xml5
```

2) Copy the .tgz / .tar files in the Home folder and extract them: 
```
tar xvf ueye_<version>_<arch>.tar 
```

3) Run the .run file and confirm any intermediate requests: 
```
sudo sh ./ueye-<version>_<arch>.run 
```

### Python libraries and routines

1) Install Python3.9 and Pip (or verify their current installation) 

2) Install the required packages by typing on the command line: 
```
sudo pip3 install termcolor pyueye pillow opencv-python numpy 
```

3) Connect the USB stick containing the .py files for interfacing with the Ueye camera. 
If the USB is recognised immediately by the system, proceed with the following step (the USB is visible in the folder /media). 
Otherwise, it is necessary to mount the USB stick and, after the files have been copied, unmount it before removing it from the Raspberry Pi3:
```
sudo blkid (to find the name under which the USB stick is read, i.e. /dev/sda) 
sudo mkdir /media/usb 
sudo mount /dev/sda /media/usb
... 
sudo umount /media/usb
```

4) Copy the .py files from the USB stick or external hard disk into the PyCamera_control folder (to be created within the directory /home)
```
sudo mkdir /home/PyCamera_control 
sudo cp <nome del file da copiare> /home/PyCamera_control 
```

5) The .py files are set to save all results within a specially dedicated folder created on an external storage device; if you do not want to connect an external disk, or if you want to do it under another name, edit the first lines of the PyCamera.py file. 
```
sudo nano PyCamera.py  
```
When finished editing, press Ctrl+O to save and then Ctrl+X to exit.

### Bash files: 

Install the screen package: 
```
sudo apt-get screen 
```

### RaspController configuration through RaspAp application: 

1) Download the RaspController application to your smartphone or tablet.
2) Install RaspAp on Raspberry Pi3 (https://raspap.com/) and type in the command line:
```
sudo apt-get update 
sudo apt-get full-upgrade 
sudo reboot 
```
After the reboot:
```
sudo raspi-config 
curl -sL https://install.raspap.com | bash 
sudo reboot 
```
The ```sudo raspi-config``` command is required to to set the proper WiFi location options, otherwise the communication protocol may fail. 

During installation, confirm all the choices proposed by the Quick installer and ensure that the Internet connection is never lost. After the last system reboot, the access point (AP) will present the default RaspAp settings: 

**`IP address`**: 10.3.141.1 

**`Username`**: admin 

**`Password`**: secret 

**`DHCP range`**: 10.3.141.50 — 10.3.141.255 

**`SSID`**: raspi-webgui 

**`Password`**: ChangeMe

## How to use

The algorithm is designed to be extremely user-friendly and can be run directly from command line by typing:

```
bash system_setup.sh
```

Here we just introduce a general workflow to control the camera from remote 
<p align="center">
<img src="https://github.com/LucaTeruzzi/PyHoloCamera/assets/83271765/46a63f4b-d7a6-4c17-8724-eeae64965bd8" width=45% height=45%>
</p>

First, the Raspberry device connects to the camera and simultaneously recognizes any external storage
device. Measurements can be started, stopped or paused by acting through RaspController on the proper GPIO channels of the Raspberry. 

All the GPIOs are initially configured with default values of “0” (off), except for GPIO 17, which is set to “1” (on). 
This particular GPIO is used to indicate the status of the pin (“0” = disabled remote control, “1” = activated remote control). 
All GPIOs are initially configured with default values of "0" (off), except for GPIO 17, which is set to "1" (on). 
This particular GPIO is used to indicate the pin’s status (0 = deactivate remote control, 1 = activate remote control). 
The acquisition of the background starts by switching the GPIO 14 to on state. 

After acquiring the images needed to obtain the background, the system allows to start the measurement by switching the GPIO 15 to on. 
After reading each image the system checks for the presence of an object within the frame by calculating the image variance. 
If this filter is passed the image is stored into the external device. 
Alternatively, it could be processed for the holographic reconstruction in real–time. 

In our case the maximum frame rate was ∼3 images per second, although higher rates can be achieved by using devices with higher RAM capacity.
Switching the GPIO 17 off, the measurement is stopped. The procedure can be halted through GPIO 23.

The Raspberry GPIO numbers can be modified by the user and adapted to any specific situation.

# Contributions

New issues and pull requests are welcomed. 

# Permissions

This code is provided under a GNU GENERAL PUBLIC LICENSE and it is in active development. Collaboration ideas and pull requests generally welcomed. Please use the citations below to credit the builders of this repository.

Copyright (c) 2023 Luca Teruzzi
