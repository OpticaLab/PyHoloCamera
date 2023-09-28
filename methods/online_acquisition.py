# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22, 2022

@author: Luca Teruzzi
"""

######################################################################################################################################################################
######################################################################################################################################################################


from termcolor import colored                                                                           # Import required libraries
import numpy as np, cv2, os, time
from datetime import datetime
from utils import *
from IDS_camera import IdsCamera


######################################################################################################################################################################
######################################################################################################################################################################
# Online acquisition method:
# at first, the output direcotires are defined and, if they do not exist yet, are created.
# After Ueye camera connection and setting, N (according to the specified value) background laser images are acquired and their variance & standard deviation are
# evaluated. Afterwards, the effective hologram acquisition starts: if the registered image contains a hologram (or, at least, something meaningful)
# it is saved in the specified directory, otherwise it is ignored and the algorithm continues. This selection is based ona specific variance filter.
# Periodically the system temepratures are monitored by means of three DS18B20 temperature sensors.
# All the information and paramterers during the run are saved in a log putput file.
# AT the end of the loop, the user can choose wether to change some settings (eg: exposure time, time sleep, etc...) before starting another acquisition.
# THIS METHOD IS INTERACTIVE AND THE USER CAN PROCEED AND CONTROL IT STEP-BY-STEP TRHOUGH COMMAND LINE. 
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
#
# Return:   - None

def start_online_acquisition(time_sleep, exposure_time, black_level, image_index, sleep_option, bkg_index_limit, bkg_var, image_extension, _extension_length, pixel_size, wavelength, medium_index, var_treshold, remote_control):

    try:
        print(colored('\n\nProceed with data acquisition? [y/n]', 'yellow'), end=' '); choice = input()       # Choose wether to start acquisition or not

        if choice in ['y', 'Y', 'yes', 'YES', 'Yes']:

            while True:

                counter_idx = 0


                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - CREATING FOLDERS AND LOG FILE - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


                os.system('clear')
                print(colored('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -', 'green'))
                print('\nCreating the folder for image data.\n')                                            # Creating folder for save the images, background images and log files
                save_path = '/media/usb/data/'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'/'
                log_path = '/media/usb/log_files/'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'/'
                bkg_path = '/media/usb/background/'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'/'        # Path to background images (for data pre-selection)

                if os.path.isdir(save_path): print('')                                                      # Creates the folders if they do not already exist
                else: os.makedirs(save_path)
                if os.path.isdir(log_path): print('')
                else: os.makedirs(log_path)
                if os.path.isdir(bkg_path): print('')
                else: os.makedirs(bkg_path)

                log_file = open(log_path+'log_file.txt', 'w')


                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                # - - - - - - - - - - - - - - - - - - - - - - - - - CONNECTING TO CAMERA AND RETRIEVING SYSTEM PARAMETERS - - - - - - - - - - - - - - - - - - - - - - - - #
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


                camera = IdsCamera(log_file, exposure_time, black_level, remote_control)                    # Connect to the IDS Ueye camera
                camera.connect()

                print(colored('\nImage format:\t\t\t\t\t', 'green'), str(image_extension))                  # Log file header and terminal printouts
                print(colored('Pixel size:\t\t\t\t\t', 'green'), str(pixel_size), ' um')
                print(colored('Wavelength:\t\t\t\t\t', 'green'), str(wavelength), ' um')
                print(colored('Medium refractive index:\t\t\t', 'green'), '{:.05f}'.format(medium_index), '\n')

                log_file.write('\nImage format:\t\t\t\t\t\t\t\t'+ str(image_extension))
                log_file.write('\nPixel size:\t\t\t\t\t\t\t\t\t'+ str(pixel_size)+' um')
                log_file.write('\nWavelength:\t\t\t\t\t\t\t\t\t'+ str(wavelength)+' um')
                log_file.write('\nMedium refractive index:\t\t\t\t\t'+ '{:.05f}'.format(medium_index)+'\n')


                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - BACKGROUND SIGNAL ACQUISITION - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


                background_acquisition(camera, bkg_path, bkg_index_limit, log_file, time_sleep, 
                                    sleep_option)                                                           # Background acquisition
                print(colored('\nWaiting before starting the measurement, press <k> to proceed.\n', 'white'), end=' ')
                log_file.write('\n\nWaiting before starting the measurement, press <k> to proceed.\n')
                proceed_with_acquisition = input()                                                          # Wait the user action (press <k> key) to proceed with data acquisition

                if proceed_with_acquisition == 'k':

                    try :                                                                                   # (Try to) upload the backgrpund images
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
                    print(colored('\nTemperature monitoring every 50 images [°C] and image check\n', 'green'))
                    log_file.write('\n\nTemperature monitoring every 50 images [°C] and image check\n\n')

                    try:
                        while True:                                                                         # Continuous image acquisition

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

                            if counter_idx%50 == 0:
                            
                                print(colored('\nImage check', 'yellow'), '\t- Image number:\t\t\t', image_index)
                                log_file.write('\nImage check - Image number:\t\t\t\t\t'+str(image_index)+'\n')
                                image_check(frame, log_file)

                            variance_selection(bkg_var, frame_var, var_treshold, save_path, frame_name, frame, label=True)      # Save data in the specified folder and apply background filter if label==True

                            if sleep_option==True: time.sleep(time_sleep)                                   # Time gap between two consecutive images


                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - END OF ACQUISITION AND PARAMETERS RESETTING - - - - - - - - - - - - - - - - - - - - - - - - - - - #
                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


                    except KeyboardInterrupt:                                                               # If the keyboard shortucut Ctrl+C is pressed -> stop the acquisition 
                        camera.disconnect()                                                                 # Disconnect Ueye camera
                        cv2.destroyAllWindows()                                                             # Close the OpenCv windows

                        print(colored('\n\n- - - - - - - - - - DATA ACQUISITION END - - - - - - - - - - - \n', 'green'))
                        log_file.write('\n\n\n- - - - - - - - - - DATA ACQUISITION END - - - - - - - - - - - \n')

                        log_file.close()                                                                    # Close log file

                        print(colored('\nStart another task and proceed with data acquisition? [y/n]', 'yellow'), end=' '); choice = input() 
                        if choice in ['y', 'Y', 'yes', 'YES', 'Yes']:                                       # Choose wether to change some setting before start a new image acquisition
                            print(colored('\nChange some acquisition settings? [y/n]', 'yellow'), end=' '); setting_choice = input()
                            if setting_choice in ['y', 'Y', 'yes', 'YES', 'Yes']: 
                                print('- Exposure time (set value '+str(exposure_time)+' ms):\t\t\t', end=' '); exposure_time = float(input())
                                print('- Background images number (set value '+str(bkg_index_limit)+'):\t\t', end=' '); bkg_index_limit = int(input())
                                print('- Time sleep (set value '+str(time_sleep*1000)+' ms):\t\t\t', end=' '); time_sleep = float(input())/1000
                                print('- Variance treshold for image filtering (set value '+str(var_treshold)+'):\t', end=' '); var_treshold = float(input())
                            else: continue
                            continue
                        else: break


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - EXIT AND CLOSE PROGRAM- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


            print(colored('\n----> EXIT PROGRAM\n', 'red'))

        else: print(colored('\n----> EXIT PROGRAM\n', 'red'))

    except KeyboardInterrupt:                                                                               # If the shortcut Ctrl+C is pressed, the execution stops 
        print(colored('\nCtrl-C pressed, stopping program!\n', 'yellow'))
        sys.exit()


######################################################################################################################################################################
######################################################################################################################################################################
