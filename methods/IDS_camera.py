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
#  This document, or source code, is provided solely as an example                                                                                                   #
#  of how to utilize IDS software libraries in a sample application.                                                                                                 #
#  IDS Imaging Development Systems GmbH does not assume any responsibility                                                                                           #
#  for the use or reliability of any portion of this document or the                                                                                                 #
#  described software.                                                                                                                                               #
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


from pyueye import ueye                                                                                 # Import required libraries
from termcolor import colored
import numpy as np, cv2


######################################################################################################################################################################
######################################################################################################################################################################


class IdsCamera(object):

    _is_SetExposureTime = ueye._bind("is_SetExposureTime",
                                     [ueye.ctypes.c_uint, ueye.ctypes.c_double,
                                      ueye.ctypes.POINTER(ueye.ctypes.c_double)], ueye.ctypes.c_int)
    IS_GET_EXPOSURE_TIME = 0x8000


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


    @staticmethod
    def is_SetExposureTime(hCam, EXP, newEXP):
        """
        Description

        The function is_SetExposureTime() sets the with EXP indicated exposure time in ms. Since this
        is adjustable only in multiples of the time, a line needs, the actually used time can deviate from
        the desired value.

        The actual duration adjusted after the call of this function is readout with the parameter newEXP.
        By changing the window size or the readout timing (pixel clock) the exposure time set before is changed also.
        Therefore is_SetExposureTime() must be called again thereafter.

        Exposure-time interacting functions:
            - is_SetImageSize()
            - is_SetPixelClock()
            - is_SetFrameRate() (only if the new image time will be shorter than the exposure time)

        Which minimum and maximum values are possible and the dependence of the individual
        sensors is explained in detail in the description to the uEye timing.

        Depending on the time of the change of the exposure time this affects only with the recording of
        the next image.

        :param hCam: c_uint (aka c-type: HIDS)
        :param EXP: c_double (aka c-type: DOUBLE) - New desired exposure-time.
        :param newEXP: c_double (aka c-type: double *) - Actual exposure time.
        :returns: IS_SUCCESS, IS_NO_SUCCESS

        Notes for EXP values:

        - IS_GET_EXPOSURE_TIME Returns the actual exposure-time through parameter newEXP.
        - If EXP = 0.0 is passed, an exposure time of (1/frame rate) is used.
        - IS_GET_DEFAULT_EXPOSURE Returns the default exposure time newEXP Actual exposure time
        - IS_SET_ENABLE_AUTO_SHUTTER : activates the AutoExposure functionality.
          Setting a value will deactivate the functionality.
          (see also 4.86 is_SetAutoParameter).
        """
        _hCam = ueye._value_cast(hCam, ueye.ctypes.c_uint)
        _EXP = ueye._value_cast(EXP, ueye.ctypes.c_double)
        ret = IdsCamera._is_SetExposureTime(_hCam, _EXP, ueye.ctypes.byref(newEXP) if newEXP is not None else None)
        return ret


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


    def __init__(self, log_file, exposure_time, black_level, remote_control, selector=''):
        self.hCam = ueye.HIDS(0)                                                                        # 0: first available camera;  1-254: The camera with the specified camera ID
        self.sInfo = ueye.SENSORINFO()
        self.cInfo = ueye.CAMINFO()
        self.pcImageMemory = ueye.c_mem_p()
        self.MemID = ueye.INT()
        self.rectAOI = ueye.IS_RECT()
        self.pitch = ueye.INT()
        self.nBitsPerPixel = ueye.INT()                                                                 # 24: bits per pixel for color mode; take 8 bits per pixel for monochrome
        self.m_nColorMode = ueye.INT()                                                                  # Y8/RGB16/RGB24/REG32
        self.bytes_per_pixel = 0
        self.width = ueye.INT()
        self.height = ueye.INT()
        self.size = (-1, -1)
        self.ok = False
        self.last_frame = None
        self.log_file = log_file
        self.exp_time = exposure_time
        self.black_level = black_level
        self.remote_control = remote_control


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


    def connect(self):

        rc = ueye.is_InitCamera(self.hCam, None)                                                        # Starts the driver and establishes the connection to the camera
        if rc != ueye.IS_SUCCESS: 
            print(colored('is_InitCamera\t\t', 'white'), colored('---> ERROR', 'red'))
            try: self.log_file.write('\nis_InitCamera\t\t---> ERROR')
            except: pass

        rc = ueye.is_GetCameraInfo(self.hCam, self.cInfo)                                               # Reads out the data hard-coded in the non-volatile camera memory
        if rc != ueye.IS_SUCCESS:                                                                       # and writes it to the data structure that cInfo points to
            print(colored('is_GetCameraInfo\t', 'white'), colored('---> ERROR', 'red'))
            try: self.log_file.write('\nis_GetCameraInfo\t---> ERROR')
            except: pass

        rc = ueye.is_GetSensorInfo(self.hCam, self.sInfo)                                               # You can query additional information about the sensor type used in the camera
        if rc != ueye.IS_SUCCESS: 
            print(colored('is_GetSensorInfo\t', 'white'), colored('---> ERROR', 'red'))
            try: self.log_file.write('\nis_GetSensorInfo\t---> ERROR')
            except: pass

        rc = ueye.is_ResetToDefault(self.hCam)
        if rc != ueye.IS_SUCCESS: 
            print(colored('is_ResetToDefault\t', 'white'), colored('---> ERROR', 'red'))
            try: self.log_file.write('\nis_ResetToDefault\t---> ERROR')
            except: pass

        rc = ueye.is_SetDisplayMode(self.hCam, ueye.IS_SET_DM_DIB)                                      # Set display mode to DIB

        if int.from_bytes(self.sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_BAYER:     # Set the right color mode
            ueye.is_GetColorDepth(self.hCam, self.nBitsPerPixel, self.m_nColorMode)                     # Setup the color depth to the current windows setting
            self.bytes_per_pixel = int(self.nBitsPerPixel / 8)
            print(colored('IS_COLORMODE_BAYER: ', 'green'), )
            try: self.log_file.write('\nIS_COLORMODE_BAYER: ')
            except: pass

        elif int.from_bytes(self.sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_CBYCRY:  # for color camera models use RGB32 mode
            self.m_nColorMode = ueye.IS_CM_BGRA8_PACKED
            self.nBitsPerPixel = ueye.INT(32)
            self.bytes_per_pixel = int(self.nBitsPerPixel / 8)
            print(colored('IS_COLORMODE_CBYCRY: ', 'green'), )
            try: self.log_file.write('\nIS_COLORMODE_CBYCRY: ')
            except: pass

        elif int.from_bytes(self.sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_MONOCHROME:
            self.m_nColorMode = ueye.IS_CM_MONO8                                                        # for color camera models use RGB32 mode
            self.nBitsPerPixel = ueye.INT(8)
            self.bytes_per_pixel = int(self.nBitsPerPixel / 8)
            print(colored('IS_COLORMODE_MONOCHROME: ', 'green'), )
            try: self.log_file.write('\nIS_COLORMODE_MONOCHROME: ')
            except: pass

        else:                                                                                           # for monochrome camera models use Y8 mode
            self.m_nColorMode = ueye.IS_CM_MONO8
            self.nBitsPerPixel = ueye.INT(8)
            self.bytes_per_pixel = int(self.nBitsPerPixel / 8)
            print(colored('Color mode: not identified', 'green'), )
            try: self.log_file.write('\nColor mode: not identified: ')
            except: pass

        print(colored('m_nColorMode: \t\t\t\t\t', 'green'), self.m_nColorMode)
        print(colored('nBitsPerPixel: \t\t\t\t\t', 'green'), self.nBitsPerPixel)
        print(colored('bytes_per_pixel: \t\t\t\t', 'green'), str(self.bytes_per_pixel)+'\n')
        
        try: 
            self.log_file.write('\nm_nColorMode: \t\t\t\t\t\t\t\t'+str(self.m_nColorMode))
            self.log_file.write('\nnBitsPerPixel: \t\t\t\t\t\t\t\t'+str(self.nBitsPerPixel))
            self.log_file.write('\nbytes_per_pixel: \t\t\t\t\t\t\t'+str(self.bytes_per_pixel)+'\n')
        except: pass

        rc = ueye.is_AOI(self.hCam, ueye.IS_AOI_IMAGE_GET_AOI, self.rectAOI, ueye.sizeof(self.rectAOI)) # Can be used to set the size and position of an 
        if rc != ueye.IS_SUCCESS:                                                                       # "area of interest"(AOI) within an image
                print(colored('is_AOI\t\t\t', 'white'), colored('---> ERROR', 'red')) 
                try: self.log_file.write('\nis_AOI\t\t\t---> ERROR')
                except: pass

        self.width = self.rectAOI.s32Width
        self.height = self.rectAOI.s32Height
        self.size = (self.width.value, self.height.value)

        if self.sInfo.strSensorName.decode('utf-8')!='':                                                # Prints out some information about the camera and the sensor
            print(colored('Camera model:\t\t\t\t\t', 'green'), self.sInfo.strSensorName.decode('utf-8'))
            try: self.log_file.write('\nCamera model:\t\t\t\t\t\t\t\t'+self.sInfo.strSensorName.decode('utf-8'))
            except: pass
        else: 
                print(colored('Camera model\t\t\t\t\t - - - - -', 'green'))
                try: self.log_file.write('\nCamera model\t\t\t\t\t\t\t - - - - -')
                except: pass
        if self.cInfo.SerNo.decode('utf-8')!='': 
            print(colored('Camera serial no.:\t\t\t\t', 'green'), self.cInfo.SerNo.decode('utf-8'))
            try: self.log_file.write('\nCamera serial no.:\t\t\t\t\t\t\t'+self.cInfo.SerNo.decode('utf-8'))
            except: pass
        else: 
                print(colored('Camera serial no.\t\t\t\t - - - - -', 'green'))
                try: self.log_file.write('\nCamera serial no.\t\t\t\t\t\t - - - - -')
                except: pass
        print(colored('Camera image size:\t\t\t\t', 'green'), str(self.size)+'\n')
        try: self.log_file.write('\nCamera image size:\t\t\t\t\t\t\t'+str(self.size)+'\n')
        except: pass
        
        self.get_camera_exposure_settings()
        self.set_camera_exposure(self.exp_time)
        self.exposure_default = self.get_camera_exposure()
        
        self.get_camera_default_blacklevel()
        self.set_camera_blacklevel(self.black_level)
        self.get_camera_blacklevel()

        self.get_camera_default_gamma()
        self.get_camera_gamma()

        rc = ueye.is_AllocImageMem(self.hCam, self.width, self.height,
                                   self.nBitsPerPixel, self.pcImageMemory, self.MemID)                  # Allocates an image memory for an image having its dimensions defined by width and height
        if rc != ueye.IS_SUCCESS:                                                                       # and its color depth defined by nBitsPerPixel
            print(colored('is_AllocImageMem\t', 'white'), colored('---> ERROR', 'red'))
            try: self.log_file.write('\nis_AllocImageMem\t---> ERROR')
            except: pass
        else:                                                                                           # Makes the specified image memory the active memory
            rc = ueye.is_SetImageMem(self.hCam, self.pcImageMemory, self.MemID)
            if rc != ueye.IS_SUCCESS: 
                    print(colored('is_SetImageMem\t\t', 'white'), colored('---> ERROR', 'red'))
                    try: self.log_file.write('\nis_SetImageMem\t\t---> ERROR')
                    except: pass
            else:                                                                                       # Set the desired color mode
                rc = ueye.is_SetColorMode(self.hCam, self.m_nColorMode)

        rc = ueye.is_CaptureVideo(self.hCam, ueye.IS_DONT_WAIT)                                         # Activates the camera's live video mode (free run mode)
        if rc != ueye.IS_SUCCESS: 
                print(colored('is_CaptureVideo\t\t', 'white'), colored('---> ERROR', 'red'))
                try: self.log_file.write('\nis_CaptureVideo\t\t---> ERROR')
                except: pass

        rc = ueye.is_InquireImageMem(self.hCam, self.pcImageMemory, self.MemID,
                                     self.width, self.height, self.nBitsPerPixel, self.pitch)           # Enables the queue mode for existing image memory sequences
        if rc != ueye.IS_SUCCESS: 
                print(colored('is_InquireImageMem\t', 'white'), colored('---> ERROR', 'red'))
                try: self.log_file.write('\nis_InquireImageMem\t---> ERROR')
                except: pass
        else:
            if self.remote_control==False: print(colored('Press x to leave the program', 'red'))
            else: print(colored('Set GPIO 17 to HIGH/LOW to stop/restart the acquisition respectively', 'red'))
            self.ok = True


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


    def grab_image(self):

        if not self.ok: return None

        array = ueye.get_data(self.pcImageMemory, self.width, 
                              self.height, self.nBitsPerPixel, self.pitch, copy=False)                  # Extract the data of our image memory

        frame = np.reshape(array, (self.height.value, self.width.value, self.bytes_per_pixel))          # Reshape it in an numpy array

        frame = cv2.resize(frame, (0, 0), fx=1.0, fy=1.0)                                               # Eventually resize the image by a given factor

        frame_var = np.var(frame)                                                                       # Image variance
        frame_dev = np.sqrt(frame_var)                                                                  # Image standard deviation

        self.last_frame = frame

        return frame, frame_var, frame_dev


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


    def disconnect(self):

        ueye.is_FreeImageMem(self.hCam, self.pcImageMemory, self.MemID)                                 # Releases an image memory that was allocated using is_AllocImageMem() 
                                                                                                        # and removes it from the driver management
        ueye.is_ExitCamera(self.hCam)                                                                   # Disables the hCam camera handle and releases the data structures 
                                                                                                        # and memory areas taken up by the uEye camera


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


    def set_camera_exposure(self, level_ms):

        p1 = ueye.DOUBLE()                                                                              # The 'level_ms' parameter defines the exposure level in milliseconds (zero for auto-exposure)
        if level_ms == 0:                                                                               # Note that you can never exceed 1000000/fps, but it is possible to change the fps
            rc = IdsCamera._is_SetExposureTime(self.hCam, ueye.IS_SET_ENABLE_AUTO_SHUTTER, p1)
            print(colored('Camera exposure setting: AUTO', 'green'))
            try: self.log_file.write('\nCamera exposure setting: AUTO')
            except: pass
        else:
            ms = ueye.DOUBLE(level_ms)
            rc = IdsCamera._is_SetExposureTime(self.hCam, ms, p1)
            print(colored(f'Camera exposure setting: requested \t\t', 'green'), '{:.03f}'.format(ms.value), colored(' ms, got ', 'green'), '{:.03f}'.format(p1.value), colored(' ms', 'green'))
            try: self.log_file.write(f'\nCamera exposure setting: requested \t\t\t'+ '{:.03f}'.format(ms.value)+' ms, got '+ '{:.03f}'.format(p1.value)+' ms')
            except: pass


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


    def get_camera_exposure(self, force_val=False):                                                     # The 'force_val' parameter, if True, will return level of exposure even if auto-exposure is on
                                                                                                        # Returns the current exposure time in milliseconds (zero if auto-exposure is on)
        p1 = ueye.DOUBLE()
        p2 = ueye.DOUBLE()

        rc = ueye.is_SetAutoParameter(self.hCam, ueye.IS_GET_ENABLE_AUTO_GAIN, p1, p2)
        rc = ueye.is_SetAutoParameter(self.hCam, ueye.IS_GET_ENABLE_AUTO_SHUTTER, p1, p2)
        if (not force_val) and p1.value == 1: return 0                                                  # Auto-exposure
        rc = IdsCamera._is_SetExposureTime(self.hCam, IdsCamera.IS_GET_EXPOSURE_TIME, p1)
        print(colored('IDS camera current exposure time:\t\t', 'green'), '{:.03f}'.format(p1.value), ' ms\n')
        try: self.log_file.write('\nIDS camera current exposure time:\t\t\t'+'{:.03f}'.format(p1.value)+' ms\n')
        except: pass
        
        return p1.value


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


    def get_camera_default_blacklevel(self):

        nOffset = ueye.INT()

        rc = ueye.is_Blacklevel(self.hCam, ueye.IS_BLACKLEVEL_CMD_GET_OFFSET_DEFAULT, nOffset, ueye.sizeof(nOffset))

        print(colored('IDS camera default black level:\t\t\t', 'green'), '{:.00f}'.format(nOffset.value))
        try: self.log_file.write('\nIDS camera default black level:\t\t\t\t'+'{:.00f}'.format(nOffset.value))
        except: pass

        return nOffset.value


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


    def get_camera_blacklevel(self):

        nOffset = ueye.INT()

        rc = ueye.is_Blacklevel(self.hCam, ueye.IS_BLACKLEVEL_CMD_GET_OFFSET, nOffset, ueye.sizeof(nOffset))
        
        print(colored('IDS camera current black level:\t\t\t', 'green'), '{:.00f}'.format(nOffset.value), '\n')
        try: self.log_file.write('\nIDS camera current black level:\t\t\t\t'+'{:.00f}'.format(nOffset.value)+'\n')
        except: pass
        
        return nOffset.value


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


    def get_camera_default_gamma(self):

        nGamma = ueye.INT()

        rc = ueye.is_Gamma(self.hCam, ueye.IS_GAMMA_CMD_GET_DEFAULT, nGamma, ueye.sizeof(nGamma))

        print(colored('IDS camera default gamma:\t\t\t', 'green'), '{:.00f}'.format(nGamma.value/100))
        try: self.log_file.write('\nIDS camera default gamma:\t\t\t\t\t'+'{:.00f}'.format(nGamma.value/100))
        except: pass
        
        return nGamma.value/100


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


    def get_camera_gamma(self):

        nGamma = ueye.INT()

        rc = ueye.is_Gamma(self.hCam, ueye.IS_GAMMA_CMD_GET, nGamma, ueye.sizeof(nGamma))

        print(colored('IDS camera current gamma:\t\t\t', 'green'), '{:.00f}'.format(nGamma.value/100), '\n')
        try: self.log_file.write('\nIDS camera current gamma:\t\t\t\t\t'+'{:.00f}'.format(nGamma.value/100)+'\n')
        except: pass

        return nGamma.value/100


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


    def set_camera_blacklevel(self, blacklevel_value):

        nOff = ueye.INT()
        nOffset = ueye.INT(blacklevel_value)

        rc = ueye.is_Blacklevel(self.hCam, ueye.IS_BLACKLEVEL_CMD_SET_OFFSET, nOffset, ueye.sizeof(nOff))

        print(colored(f'Camera black level setting: requested \t\t', 'green'), '{:.00f}'.format(nOffset.value), colored(', got ', 'green'), '{:.00f}'.format(nOffset.value))
        try: self.log_file.write(f'\nCamera black level setting: requested \t\t'+ '{:.00f}'.format(nOffset.value)+', got '+ '{:.00f}'.format(nOffset.value))
        except: pass


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #


    def get_camera_exposure_settings(self, force_val=False):                                            # The 'force_val' parameter, if True, will return level of exposure even if auto-exposure is on
                                                                                                        # Returns the current exposure time in milliseconds (zero if auto-exposure is on)
        p1 = ueye.DOUBLE()
        p2 = ueye.DOUBLE()

        rc = ueye.is_SetAutoParameter(self.hCam, ueye.IS_GET_ENABLE_AUTO_GAIN, p1, p2)
        print(colored('Enable auto gain:\t\t\t\t', 'green'), f'{p1.value == 1}')
        try: self.log_file.write(f'\nEnable auto gain:\t\t\t\t\t\t\t{p1.value == 1}')
        except: pass
        rc = ueye.is_SetAutoParameter(self.hCam, ueye.IS_GET_ENABLE_AUTO_SHUTTER, p1, p2)
        print(colored('Enable auto shutter:\t\t\t\t', 'green'), f'{p1.value == 1}')
        try: self.log_file.write(f'\nEnable auto shutter:\t\t\t\t\t\t{p1.value == 1}')
        except: pass
        if (not force_val) and p1.value == 1: return 0                                                  # Auto-exposure
        rc = IdsCamera._is_SetExposureTime(self.hCam, IdsCamera.IS_GET_EXPOSURE_TIME, p1)
        print(colored('Default exposure time:\t\t\t\t', 'green'), '{:.03f}'.format(p1.value)+' ms')
        try: self.log_file.write('\nDefault exposure time:\t\t\t\t\t\t'+'{:.03f}'.format(p1.value)+' ms')
        except: pass

        return p1.value


######################################################################################################################################################################
######################################################################################################################################################################
