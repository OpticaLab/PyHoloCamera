# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22, 2022

@author: Luca Teruzzi
"""

######################################################################################################################################################################
######################################################################################################################################################################


from termcolor import colored                                                                           # Import required libraries
import numpy as np, os, time, sys
from datetime import datetime
from utils import *
from IDS_camera import IdsCamera
import RPi.GPIO as GPIO


######################################################################################################################################################################
######################################################################################################################################################################
# Offline acquisition method:
# at first, the output direcotires are defined and, if they do not exist yet, are created.
# After Ueye camera connection and setting, N (according to the specified value) background laser images are acquired and their variance & standard deviation are
# evaluated. Afterwards, the effective hologram acquisition starts: if the registered image contains a hologram (or, at least, something meaningful)
# it is saved in the specified directory, otherwise it is ignored and the algorithm continues. This selection is based ona specific variance filter.
# Periodically the system temepratures are monitored by means of three DS18B20 temperature sensors.
# All the information and paramterers during the run are saved in a log putput file.
# AT the end of the loop, the user can choose wether to change some settings (eg: exposure time, time sleep, live option, etc...) before starting another acquisition.
# THIS METHOD IS INTERACTIVE AND THE USER CAN PROCEED AND CONTROL IT STEP-BY-STEP TRHOUGH THE RASPCONTROLLER APP ON SMARTPHONE OR TABLET. 
#
# Input:    - time_sleep: time sleep between two consecutive images
#           - exposure_time: Ueye camera exposure time
#           - black_level: Ueye camera bleck level offset
#           - image_index: (incremental) index of the acquired image
#           - sleep_option: boolean value to enable time sleep
#           - bkg_index_limit: number of images to acquire
#           - bkg_var: initialized null image variance
#           - image_extension: image format (.tif or .tiff)
#           - _extension_length: length of the 'image_extension' string
#           - pixel_size: Ueye camera pixel size
#           - wavelength: laser wavelength
#           - medium_index: medium (default, air) refractive index at the selected wavelength
#           - var_treshold: treshold to evaluate the variance comparison
#           - remote_control: auxiliary flag for LIVE software control
#           - pin_RUN: number of RPi pin to start the program
#           - pin_STOP: number of RPi pin to stop/restart image acquisition
#           - pin_LIVE: number pf RPi pin to enable/disable live image visualization
#
# Return:   - None

def start_offline_acquisition(time_sleep, exposure_time, black_level, image_index, sleep_option, bkg_index_limit, bkg_var, image_extension, _extension_length, pixel_size, wavelength, medium_index, var_treshold, pin_RUN, pin_ACQUIRE, pin_STOP, pin_EXIT, remote_control):

    GPIO.setmode(GPIO.BCM)                                                                              # Raspberry GPIO mode setting (BCM = GPIO numbering; BOARD = pin numbering)
    GPIO.setwarnings(False)                                                                             # Suppress GPIO warnings

    GPIO.setup(pin_RUN, GPIO.OUT)                                                                       # Set GPIO operation mode (OUTPUT)
    GPIO.setup(pin_ACQUIRE, GPIO.OUT)
    GPIO.setup(pin_STOP, GPIO.OUT)
    GPIO.setup(pin_EXIT, GPIO.OUT)
    GPIO.output(pin_STOP, 1)
    GPIO.output(pin_ACQUIRE, 0)
    GPIO.output(pin_EXIT, 0)

    while True:

        if GPIO.input(pin_RUN)==1:                                                                      # If pin_RUN value is HIGH, start the image acquisition

            GPIO.output(pin_STOP, 1)
            while GPIO.input(pin_RUN)==1:

                if GPIO.input(pin_STOP)==1:                                                             # While pin_STOP is HIGH, the image acquisition is performed

                    if GPIO.input(pin_EXIT)==1: sys.exit()

                    counter_idx = 0


                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - CREATING FOLDERS AND LOG FILE - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


                    os.system('clear')
                    print(colored('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -', 'green'))
                    print('\nCreating the folder for image data.\n')                                    # Creating folder for save the images, background images and log files
                    save_path = '/media/usb/'+datetime.now().strftime("%Y%m%d_%H%M%S")+'/data/'
                    log_path = '/media/usb/'+datetime.now().strftime("%Y%m%d_%H%M%S")+'/log_files/'
                    bkg_path = '/media/usb/'+datetime.now().strftime("%Y%m%d_%H%M%S")+'/background/'

                    if os.path.isdir(save_path): print('')                                              # Creates the folders if they do not already exist
                    else: os.makedirs(save_path)
                    if os.path.isdir(log_path): print('')
                    else: os.makedirs(log_path)
                    if os.path.isdir(bkg_path): print('')
                    else: os.makedirs(bkg_path)

                    log_file = open(log_path+'log_file.txt', 'w')

                    if GPIO.input(pin_EXIT)==1: 
                        log_file.close()                                                                # Close log file
                        sys.exit()


                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                    # - - - - - - - - - - - - - - - - - - - - - - - - - CONNECTING TO CAMERA AND RETRIEVING SYSTEM PARAMETERS - - - - - - - - - - - - - - - - - - - - - - - - #
                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


                    camera = IdsCamera(log_file, exposure_time, black_level, remote_control)            # Connect to the IDS Ueye camera
                    camera.connect()

                    print(colored('\nImage format:\t\t\t\t\t', 'green'), str(image_extension))          # Log file header and terminal printouts
                    print(colored('Pixel size:\t\t\t\t\t', 'green'), str(pixel_size), ' um')
                    print(colored('Wavelength:\t\t\t\t\t', 'green'), str(wavelength), ' um')
                    print(colored('Medium refractive index:\t\t\t', 'green'), '{:.05f}'.format(medium_index), '\n')

                    log_file.write('\nImage format:\t\t\t\t\t\t\t\t'+ str(image_extension))
                    log_file.write('\nPixel size:\t\t\t\t\t\t\t\t\t'+ str(pixel_size)+' um')
                    log_file.write('\nWavelength:\t\t\t\t\t\t\t\t\t'+ str(wavelength)+' um')
                    log_file.write('\nMedium refractive index:\t\t\t\t\t'+ '{:.05f}'.format(medium_index)+'\n')

                    if GPIO.input(pin_EXIT)==1: 
                        log_file.close()                                                                # Close log file
                        camera.disconnect()                                                             # Disconnect Ueye camera
                        sys.exit()


                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - BACKGROUND SIGNAL ACQUISITION - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


                    background_acquisition(camera, bkg_path, bkg_index_limit, log_file, time_sleep, 
                                           sleep_option, pin_EXIT)                                      # Background acquisition
                    print(colored('\nWaiting before starting the measurement, set GPIO 15 state to HIGH.\n', 'white'))
                    log_file.write('\n\nWaiting before starting the measurement, set GPIO 15 state to HIGH.\n')

                    if GPIO.input(pin_EXIT)==1: 
                        log_file.close()                                                                # Close log file
                        camera.disconnect()                                                             # Disconnect Ueye camera
                        sys.exit()

                    while GPIO.input(pin_ACQUIRE)==0:                                                   # Wait until the GPIO realtive to data acquisition is set to HIGH state
                        if GPIO.input(pin_ACQUIRE)==1: break

                    try :                                                                               # (Try to) upload the backgrpund images
                        bkg_var, bkg_dev = background(bkg_path, image_extension)
                        if bkg_var==0: 
                            print(colored('No background image detected or NULL background variance, invalid values!\n', 'red'))
                        exit
                    except:
                        if not os.path.isdir(bkg_path): 
                            print(colored('\nBackground folder not found!\n', 'red'))
                            log_file.write('\n\nBackground folder not found!\n')
                        elif len(os.listdir(bkg_path))==0: 
                            print(colored('\nBackground folder empty, could not upload data!\n', 'red'))
                            log_file.write('\n\nBackground folder empty, could not upload data!\n')
                        elif os.listdir(bkg_path)[0][-_extension_length:]!=image_extension and os.listdir(bkg_path)[-1][-_extension_length:]!=image_extension: 
                            print(colored('\nImage extension not recognized!\n\t- required format: '+image_extension+'\n\t- provided extension: '+os.listdir(bkg_path)[0][-_extension_length:]+'\n', 'red'))
                            log_file.write('\n\nImage extension not recognized!\n\t- required format: '+image_extension+'\n\t- provided extension: '+os.listdir(bkg_path)[0][-_extension_length:]+'\n')

                    if GPIO.input(pin_EXIT)==1: 
                        log_file.close()                                                                # Close log file
                        camera.disconnect()                                                             # Disconnect Ueye camera
                        sys.exit()


                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - HOLOGRAM IMAGES ACQUISITION - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


                    print(colored('\n- - - - - - - - - - DATA ACQUISITION START - - - - - - - - - - \n', 'green'))
                    log_file.write('\n\n- - - - - - - - - - DATA ACQUISITION START - - - - - - - - - - \n')
                    print(colored('\nSelected path:\t\t\t\t\t', 'green'), str(save_path))
                    log_file.write('\n\nSelected path:\t\t\t\t\t\t\t\t'+str(save_path))
                    if sleep_option==False: 
                        print(colored('Time sleep between two consecutive images:\t', 'green'), str(sleep_option))
                        log_file.write('\nTime sleep between two consecutive images:\t'+str(sleep_option))
                    if sleep_option==True: 
                        print(colored('Time sleep between two consecutive images:\t', 'green'), str(sleep_option), colored(', T = ', 'green'), str(time_sleep*1000), colored('ms', 'green'))
                        log_file.write('\nTime sleep between two consecutive images:\t'+str(sleep_option)+', T = '+str(time_sleep*1000)+' ms')

                    if GPIO.input(pin_EXIT)==1: 
                        log_file.close()                                                                # Close log file
                        camera.disconnect()                                                             # Disconnect Ueye camera
                        sys.exit()

                    while True:                                                                         # Continuous image display

                        frame, frame_var, frame_dev = camera.grab_image()                               # Retrieve the image from IDS Ueye camera, its variance and the stadard deviation

                        if image_index in range(0, 10): frame_name = f'image_000000{image_index}.tif'   # Settting image incremental index
                        elif image_index in range(10, 100): frame_name = f'image_00000{image_index}.tif'
                        elif image_index in range(100, 1000): frame_name = f'image_0000{image_index}.tif'
                        elif image_index in range(1000, 10000): frame_name = f'image_000{image_index}.tif'
                        elif image_index in range(10000, 100000): frame_name = f'image_00{image_index}.tif'
                        elif image_index in range(100000, 1000000): frame_name = f'image_0{image_index}.tif'
                        elif image_index >= 1000000: frame_name = f'image_{image_index}.tif'
                        image_index += 1
                        counter_idx += 1

                        if GPIO.input(pin_EXIT)==1: 
                            log_file.close()                                                            # Close log file
                            camera.disconnect()                                                         # Disconnect Ueye camera
                            sys.exit()

                        if counter_idx%50 == 0:                                                        # Retrieving RPi CPU temperature and from DS18B20
                            
                            print(colored('\nImage check', 'yellow'), '\t- Image number:\t\t\t', image_index)
                            log_file.write('\nImage check - Image number:\t\t\t\t\t'+str(image_index)+'\n')
                            image_check(frame, log_file)

                        variance_selection(bkg_var, frame_var, var_treshold, save_path, frame_name, frame, label=True)      # Save data in the specified folder and apply background filter if label==True

                        if sleep_option==True: time.sleep(time_sleep)                                   # Time gap between two consecutive images

                        if GPIO.input(pin_STOP)==0: break


                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - END OF ACQUISITION AND PARAMETERS RESETTING - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


                    camera.disconnect()                                                                 # Disconnect Ueye camera

                    print(colored('\n\n- - - - - - - - - - DATA ACQUISITION END - - - - - - - - - - - \n', 'green'))
                    log_file.write('\n\n\n- - - - - - - - - - DATA ACQUISITION END - - - - - - - - - - - \n')

                    log_file.close()                                                                    # Close log file


        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - EXIT AND CLOSE PROGRAM- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


            print(colored('\n----> EXIT PROGRAM\n', 'red'))

        if GPIO.input(pin_RUN)==0 and GPIO.input(pin_STOP)==0: break


######################################################################################################################################################################
######################################################################################################################################################################
