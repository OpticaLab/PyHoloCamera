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

To run the script on his own laptop or PC, the user first need to install the specified Python
packages:

• numpy ≥ 1.21, matplotlib ≥ 3.6.2 and math (default packages);

• pyserial, for setting the serial communication through the RS232 port between the SPOS instrument and the PC;

• PyQt5, pyqtgraph, qtwidgets required for the graphical user interface;

• termcolor;

• pandas;

• os-sys ≥ 2.1.4;

• scipy ≥ 1.9.3 (optimize, interpolate), needed for computing the instrumental calibration
curve;

• miepython, for computations regardig Mie scattering parameters (eg. scattering and extinction cross sections);

• openpyxl, for exporting data in xlsx files.

To do so, after installing Python3 and pip3, you can just copy and paste the following line in the
command line:
```
pip3 install numpy≥1.21, matplotlib≥3.6.2, os-sys≥2.1.4, pyserial, PyQt5, pyqtgraph, qtwidgets, termcolor, scipy≥1.9.3, miepython, openpyxl, pandas
```
Otherwise, you can run the setup.py script in the ”setup” folder by typing:
```
python3 setup.py
```

## How to use

The algorithm is designed to be extremely user-friendly and can be run dircetly from command line by typing:

```
python3 spos_main.py
```

# Contributions

New issues and pull requests are welcomed. 

# Permissions

This code is provided under a GNU GENERAL PUBLIC LICENSE and it is in active development. Collaboration ideas and pull requests generally welcomed. Please use the citations below to credit the builders of this repository.

Copyright (c) 2023 Luca Teruzzi
