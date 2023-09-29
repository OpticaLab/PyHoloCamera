# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22, 2022

@author: Luca Teruzzi
"""

#====================================================================================================================================================================#
#                                                                                                                                                                    #
#  Copyright (C) 2006 - 2018                                                                                                                                         #
#  IDS Imaging Development Systems GmbH                                                                                                                              #
#  Dimbacher Str. 6-8                                                                                                                                                #
#  D-74182 Obersulm, Germany                                                                                                                                         #
#                                                                                                                                                                    #
#  The information in this document is subject to change without notice                                                                                              #
#  and should not be construed as a commitment by IDS Imaging Development                                                                                            #
#  Systems GmbH. IDS Imaging Development Systems GmbH does not assume any                                                                                            #
#  responsibility for any errors that may appear in this document.                                                                                                   #
#                                                                                                                                                                    #
#  General permission to copy or modify, but not for profit, is hereby                                                                                               #
#  granted, provided that the above copyright notice is included and                                                                                                 #
#  reference made to the fact that reproduction privileges were granted                                                                                              #
#  by IDS Imaging Development Systems GmbH.                                                                                                                          #
#                                                                                                                                                                    #
#  IDS Imaging Development Systems GmbH cannot assume any responsibility                                                                                             #
#  for the use or misuse of any portion of this software for other than                                                                                              #
#  its intended diagnostic purpose in calibrating and testing IDS                                                                                                    #
#  manufactured cameras and software.                                                                                                                                #
#                                                                                                                                                                    #
#====================================================================================================================================================================#


######################################################################################################################################################################
######################################################################################################################################################################


import sys, os
sys.path.insert(0, '/home/pi/PyCamera_control/methods')
from utils import *                                                                                     # Import required libraries
from online_acquisition import *
from offline_acquisition import *


######################################################################################################################################################################
######################################################################################################################################################################


time_sleep = 0.3                                                                                        # Time sleep
exposure_time = 0.01                                                                                    # CCD exposure time [ms]
black_level = 220                                                                                       # Black level offset for image acquisition
image_index = 1                                                                                         # Incremental image number
sleep_option = True                                                                                     # Label for time sleep between consecutive images
bkg_index_limit = 250                                                                                   # Number of background images
bkg_var = 0
image_extension = 'tif'                                                                                 # Image extension
_extension_length = len(image_extension)
pixel_size = 5.3                                                                                        # Camera pixel sixe [um]
wavelength = 0.6335                                                                                     # Laser wavelength [um]
A, B, C, D, E = 8060.51, 2480990, 132.274, 17455.7, 39.32957                                            # Parameters to compute air refractive index at the specified wavelength
medium_index = (A + B/(C - wavelength**(-2)) + D/(E - wavelength**(-2)))*10**(-8) + 1                   # Air refractive index --- see: https://www.scirp.org/reference/referencespapers.aspx?referenceid=2136018&msclkid=51882231a8f311eca529a84e37286153
var_treshold = 5

pin_RUN, pin_ACQUIRE, pin_STOP, pin_EXIT = 14, 15, 17, 23
start_offline_acquisition(time_sleep, exposure_time, black_level, image_index, sleep_option, bkg_index_limit, bkg_var, image_extension, _extension_length, pixel_size, wavelength, medium_index, var_treshold, pin_RUN, pin_ACQUIRE, pin_STOP, pin_EXIT, remote_control)

os.system('sudo umount /media/usb')


######################################################################################################################################################################
######################################################################################################################################################################
