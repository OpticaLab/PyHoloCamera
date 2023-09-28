# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22, 2022

@author: Luca Teruzzi
"""

######################################################################################################################################################################
######################################################################################################################################################################


from termcolor import colored                                                                           # Import required libraries
import numpy as np, cv2, time, sys, os
from PIL import Image
from IDS_camera import IdsCamera
import RPi.GPIO as GPIO


######################################################################################################################################################################
######################################################################################################################################################################
# Progress bar method: 
# draw an incremental progress bar in terminal to monitor the acquisition progress
#
# Input:    - percent: percentage progress
#           - barlen = 100
#
# Return:   - None

def ProgressBar(percent, barLen = 100):                                                                 # Progress bar printed and updated on command line

	sys.stdout.write("\r")
	progress = ""
	for i in range(barLen):
		if i <= int(barLen * percent):
			progress += "="
		else:
			progress += " "
	sys.stdout.write("[ %s ] %.2f%%" % (progress, percent * 100))
	sys.stdout.flush()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Background aquisition method: 
# save a fixed number of background images before starting the holograms acuisition and register the information on a log output file
#
# Input:    - camera: the Ueye camera object to perform the acquisition
#           - bkg_path: path to save background images
#           - image_index_limit: number of images to acquire
#           - log_file: output file
#           - time_sleep: (optional) time between two consecutive images
#           - sleep_option: boolean value to enable time sleep
#
# Return:   - None

def background_acquisition(camera, bkg_path, image_index_limit, log_file, time_sleep, sleep_option, pin_EXIT):

    image_index = 1                                                                                     # Incremental image number

    print(colored('\n- - - - - - - - - BACKGROUND ACQUISITION START - - - - - - - - - \n', 'green'))
    log_file.write('\n\n- - - - - - - - - BACKGROUND ACQUISITION START - - - - - - - - - \n')
    print(colored('\nSelected path:\t\t\t\t\t', 'green'), str(bkg_path))
    log_file.write('\n\nSelected path:\t\t\t\t\t\t\t\t'+str(bkg_path))
    print(colored('Number of background images:\t\t\t', 'green'), str(image_index_limit))
    log_file.write('\nNumber of background images:\t\t\t\t'+str(image_index_limit))
    if sleep_option==False: 
        print(colored('Time sleep between two consecutive images:\t', 'green'), str(sleep_option))
        log_file.write('\nTime sleep between two consecutive images:\t'+str(sleep_option))
    if sleep_option==True: 
        print(colored('Time sleep between two consecutive images:\t', 'green'), str(sleep_option), colored(', T = ', 'green'), str(time_sleep*1000), colored('ms', 'green'))
        log_file.write('\nTime sleep between two consecutive images:\t'+str(sleep_option)+', T = '+str(time_sleep*1000)+' ms')

    if GPIO.input(pin_EXIT)==1: 
        log_file.close()                                                                                # Close log file
        camera.disconnect()                                                                             # Disconnect Ueye camera
        sys.exit()

    for i in range(image_index, image_index_limit+1):                                                   # Continuous image display

        frame, _, _ = camera.grab_image()                                                               # Retrieve the image from IDS Ueye camera, its variance and the stadard deviation

        if image_index in range(0, 10): frame_name = f'image_00000{image_index}.tif'                    # Settting image incremental index
        elif image_index in range(10, 100): frame_name = f'image_0000{image_index}.tif'
        elif image_index in range(100, 1000): frame_name = f'image_000{image_index}.tif'
        elif image_index in range(1000, 10000): frame_name = f'image_00{image_index}.tif'
        elif image_index in range(10000, 100000): frame_name = f'image_0{image_index}.tif'
        elif image_index >= 100000: frame_name = f'image_{image_index}.tif'
        image_index += 1

        if GPIO.input(pin_EXIT)==1: 
            log_file.close()                                                                            # Close log file
            camera.disconnect()                                                                         # Disconnect Ueye camera
            sys.exit()
        
        if image_index%25 == 0:    
            print(colored('\nImage check', 'yellow'), '\t- Image number:\t\t\t', image_index)
            log_file.write('\nImage check - Image number:\t\t\t\t\t'+str(image_index)+'\n')
            image_check(frame, log_file)

        cv2.imwrite(bkg_path+frame_name, np.array(frame))                                               # Save data in the specified folder

        if sleep_option==True: time.sleep(time_sleep)                                                   # Time gap between two consecutive images

        if cv2.waitKey(1) & 0xFF == ord('q'): break                                                     # Press q if you want to end the loop

    cv2.destroyAllWindows() 

    print(colored('\n- - - - - - - - - BACKGROUND ACQUISITION END - - - - - - - - - -\n', 'green'))
    log_file.write('\n\n- - - - - - - - - BACKGROUND ACQUISITION END - - - - - - - - - -\n')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Background analysis method:
# analyze the previously acuired background images and compute image variance and standard deviation
#
# Input:    - bkg_path: path where background images are stored
#           - image_extension: image format (.tif or .tiff)
#
# Return:   - var: background images mean variance
#           - dev: backgound images mean standard deviation

def background(bkg_path, image_extension):

    background_image_number = len(os.listdir(bkg_path))                                                 # Getting the # of images in the directory
    var_list = []

    for i in range(2, background_image_number+1):                                                       # Background images upload
        
        if i in range(0, 10): index = '00000'+str(i)                                                    # Set the appropiate suffix for image selection 
        elif i in range(10, 100): index = '0000'+str(i)
        elif i in range(100, 1000): index = '000'+str(i)
        elif i in range(1000, 10000): index = '00'+str(i)
        elif i in range(10000, 100000): index = '0'+str(i)
        elif i >= 100000: index = str(i)

        bkg_image = Image.open(bkg_path+'image_'+index+'.'+image_extension)
        bkg_image = np.array(bkg_image)
        var_list.append(np.var(bkg_image))

    var = float(np.mean(var_list))                                                                      # Variance
    dev = np.sqrt(var)                                                                                  # Standard deviation

    return var, dev 


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Variance filter method:
# with reference to the background images mean variance, check wether the acquired image contains a hologram (or, at least, something meaningful) or not; 
# if so, the image is saved in the appropriate directory
#
# Input:    - bkg_var: mean background variance
#           - img_var: new image variance
#           - var_treshold: treshold to evaluate the variance comparison
#           - save_path: path to save the newly acquired image
#           - frame_name: image name
#           - frame: the acquired image
#           - label: boolean value to perform the variance selection or not
#
# Return:   - save_status: boolean value (TRUE if the image has been saved, FALSE otherwise)

def variance_selection(bkg_var, img_var, var_treshold, save_path, frame_name, frame, label):

    if label==True:
        if ((abs(img_var - bkg_var)/img_var)*100) >= var_treshold: save_status = cv2.imwrite(save_path+frame_name, np.array(frame)) 
        else: save_status = False

    elif label==False:
        save_status = cv2.imwrite(save_path+frame_name, np.array(frame))

    return save_status
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Image control method:
# performs some statistics on the acquired image, before saving it; the minimum and maximum value, the average one and the standard deviation are computed, as well as
# the number of pixels with value exactly equal to 0 and the number of saturated pixels; these results are reported in the command line while the scipt is running
#
# Input:    - img: image to be analyzed
#           - log_file: output file
#
# Return:   - None

def image_check(img, log_file):

    M, m, avg, dev_std = int(img[100:850, 300:1050].max()), int(img[100:850, 300:1050].min()), np.mean(img[100:850, 300:1050]), img[100:850, 300:1050].std()
    idx_null = np.where(img[100:850, 300:1050]==0.0)[0]
    idx_sat = np.where(img[100:850, 300:1050]==255.0)[0]
    
    print('\t\t- Minimum image value:\t\t', m)
    print('\t\t- Maximum image value:\t\t', M)
    print('\t\t- Average image value:\t\t', '{:.3f}'.format(avg))
    print('\t\t- Image Std deviation:\t\t', '{:.3f}'.format(dev_std))
    print('\t\t- Number of NULL pixels:\t', len(idx_null))
    print('\t\t- Number of saturated pixels:\t', len(idx_sat), '\n')

    log_file.write('\t\t\t- Minimum image value:\t\t\t'+str(m)+'\n')
    log_file.write('\t\t\t- Maximum image value:\t\t\t'+str(M)+'\n')
    log_file.write('\t\t\t- Average image value:\t\t\t'+'{:.3f}'.format(avg)+'\n')
    log_file.write('\t\t\t- Image Std deviation:\t\t\t'+'{:.3f}'.format(dev_std)+'\n')
    log_file.write('\t\t\t- Number of NULL pixels:\t\t'+str(len(idx_null))+'\n')
    log_file.write('\t\t\t- Number of saturated pixels:\t'+str(len(idx_sat))+'\n\n')


######################################################################################################################################################################
######################################################################################################################################################################
