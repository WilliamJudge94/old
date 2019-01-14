#%matplotlib notebook This will make the plots interactive but also ruin some of the scripts
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from tqdm import tqdm
from os import walk
from PIL import Image
import numpy as np
import scipy.misc
from scipy.misc import imsave
import cv2
import matplotlib.pyplot as plt1
from scipy.ndimage import median_filter
import imageio
import os
import math
from math import *
import scipy as sp
from scipy import signal
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.io import loadmat
import time
import random
import logging
import warnings
import shutil
import psutil
import matplotlib.patches as patches
from matplotlib.patches import Circle

def mem_logger(num):
    mems=psutil.virtual_memory()
    available=str(round(mems[1]/1000000000,4))
    used=str(round(mems[3]/1000000000,4))
    percent=str(round(mems[2],1))
    
    
    log.info(str(num)+'    RAM  - Available: '+available+' - Used: '+used+' - Percent: '+percent+' -')

log=logging.getLogger(__name__)
#logging.basicConfig(filename='/home/will/Desktop/SXDM.log',level=logging.INFO)

class SXDM(): 
    """Allows the User to quickly analayze SXDM data



	Variables--

	fov: (number)
		- a single number which specifies which field of fiew you are looking at
	
	scanlist: list of scan number STRINGS or NUMBERS in [] notation
		- the User can input any scan numbers they wish to analyse
		- Example (STRINGS): ['294','300','303','307','310','315','318','321','324','327','330','333','336']
		- Example (NUMBERS): [294,300,303,307,310,315,318,321,324,327,330,333,336]

	sample: string
		- A string of what the sample name is. This corresponds to the folder names
		- Acceptable values - 'pristine' 'charged' 'charged_discharged' 'sample1' 'sample2' 'sample3' ... 'sample12' 
		- If you need more acceptable values the User can add more in the .py file. They are located at the top of the __init__ function
        
        folder_path: string
                - A string to the destination where the Beam_Line_Data^ and WIP^ folders are located
                - Can only be used if the User did not change any of the default filenames. See next two variables for more details.


        beamline_data_path: string
                - This is the path to the beamline data for THE SPECIFIC SAMPLE YOU ARE ABOUT TO RUN
		- Example if this is the path to the scan folders from the beamline /home/will/Desktop/gyarados/SXDM/20170314_APS_26IDC/1-Pristine/Images/Scan_Folders
		  then the beamline_data_paths value must equal '/home/will/Desktop/gyarados/SXDM/20170314_APS_26IDC/'
                
        wip_path: string 
                - This is the path to the wip folder for THE SPECIFIC SAMPLE YOU ARE ABOUT TO RUN

	scanangles: list of scan angles NUMBERS in [] notation (Optional if you don't care about any accuracy in the Gaussian Check Function)
		- the User can input any scan angles they wish to analyse MUST BE IN SAME ORDER THE SCAN NUMBERS ARE IN
		- Example: [8.2,8.4,8.6,8.8,9,9.2,9.4,9.6,9.8,10,10.2,10.4,10.6]

	

	dx: list of scan angles NUMBERS in [] notation
		- The dx movements of the Fluorescence Images. Used to allign all the images
		- the User can manually define dx values or leave this blank and the program will auto calculate them based on the locationtif files provided
		- Example: [0,2,-6,-9,-10,-9,-4,-4,-4,-1,-3,-5]

	dy: list of scan angles NUMBERS in [] notation
		- The dy movements of the Fluorescence Images. Used to allign all the images
		- the User can manually define dy values or leave this blank and the program will auto calculate them based on the locationtif files provided
		- Example: [0,1,-2,-1,2,-3,-2,-1,0,1,2,3]

    """
            



                                                                                        
    def __init__(self,fov,scanlist,sample='',folder_path='',scanangles='',dx='',dy='',
                beamline_data_path='' ,
                wip_path='',
                ):
        log.info('__init__ BEGIN')
        logging.basicConfig(filename=folder_path+'SXDM.log',level=logging.INFO)

        #Warning about current memory amount in the computer
        if psutil.virtual_memory()[0]/1000000000 < 16:
            warnings.warn('Your Machine May Not Have Enough Memory To Complete Some Of The Scripts. It Is Advised To Have A Minimum Of 16GB of RAM.')
        
        
        if isinstance(scanlist[0],int) == True:
            log.info('User Input scanlist As A Number Array. Changing To String Array.')
            scanlist_num2str=[]
            for scan in scanlist:
                scanlist_num2str.append(str(scan))
            scanlist = scanlist_num2str

        log.info('Setting the beamline_data_path and wip_path...')
        if folder_path=='':
            if beamline_data_path!='' and wip_path!='':
                beamline_data_path=beamline_data_path
                wip_path=wip_path
            elif beamline_data_path=='' and wip_path!='' or beamline_data_path!='' and wip_path=='':
                warnings.warn('You have to set both the beamline_data_path AND the wip_path')                
            else:
                warnings.warn('You have to set the variable called folder_path to the same as the folder_path value from the SXDM_folder_managment function. Or set the beamline_data_path and wip_path manually.')
        

        elif folder_path!='':
            if beamline_data_path=='' and wip_path=='':
                beamline_data_path=folder_path+'Beam_Line_Data^/SXDM/APS_Filename^/'
                wip_path=folder_path+'WIP^/'
            elif beamline_data_path!='' and wip_path!='':
                beamline_data_path=beamline_data_path
                wip_path=wip_path
            else:
                warnings.warn('You have to set both the beamline_data_path AND the wip_path')
            time.sleep(2)
        print('The programs folder_path + beamline_data_path is currently set to: \n'+beamline_data_path)
        print(' ')
        print('The programs folder_path + wip_path is currently set to: \n'+wip_path)
        print(' ')
        log.info('The programs folder_path + beamline_data_path is currently set to: \n'+beamline_data_path)
        log.info('The programs folder_path + wip_path is currently set to: \n'+wip_path)



	#Allow the User to define which type of particle they are working on
        log.info('Setting Predetermined Folder Names...')
        if sample=='pristine':
            folderval='1-Pristine/'            
        elif sample=='charged':
            folderval='2-Charged/'
        elif sample=='charged_discharged':
            folderval='3-Charged_Discharged/'
        
	#The User Can Change These Values If They Want To. Mainly For Personal Use. These Will Just Be The Standard Values Incase The User Isn't Working With Batteries
        elif sample=='sample1':
            folderval='1-Sample/'            
        elif sample=='sample2':
            folderval='2-Sample/'
        elif sample=='sample3':
            folderval='3-Sample/'
        elif sample=='sample4':
            folderval='4-Sample/'            
        elif sample=='sample5':
            folderval='5-Sample/'
        elif sample=='sample6':
            folderval='6-Sample/'
        elif sample=='sample7':
            folderval='7-Sample/'            
        elif sample=='sample8':
            folderval='8-Sample/'
        elif sample=='sample9':
            folderval='9-Sample/'
        elif sample=='sample10':
            folderval='10-Sample/'            
        elif sample=='sample11':
            folderval='11-Sample/'
        elif sample=='sample12':
            folderval='12-Sample/'
        elif sample=='':
            warnings.warn('Set sample variable. Acceptable default values are listed in the information about this class.')



        #Don't change this variable
        elif sample=='detector':
            folderval='zDetector'
        

        if scanangles=='':
            log.info('Setting scanangles Variable to Default Array np.arange(0:len(array))...')
            scanangles=np.arange(0,len(scanlist))
            warnings.warn('scanangles variable has been set to its default array')       
        
        log.info('Creating self.variable To Define Folder Locations...')
            #Beamline Images
        self.data=beamline_data_path+folderval+'Images/'

            #Right before the Beamline Images folder and MDA folder
        self.data_pre=beamline_data_path+folderval
        
            #Beamline Detector Images To Determine Pixle Size
        self.detector=beamline_data_path+'zDetector/Images/'
            
            #Folder that holds the Location.mat files 
        self.locationmat=wip_path+folderval+'1-LocationMat/'#+'FOV'+str(fov)+ '/'

            #Folder that holds the Location.mat files 
        self.zExtra=wip_path+folderval+'zExtra/'#+'FOV'+str(fov)+ '/'
        
            #Folder that holds the ROI.mat files
        self.roimat=wip_path+folderval+'2-ROIMat/'#+'FOV'+str(fov)+ '/'
        
            #Folder that holds the Fluor.mat files
        self.fluormat=wip_path+folderval+'3-FluorMat/'#+'FOV'+str(fov)+ '/'
        
            #Folder that holds the Test.mat files
        self.testmat=wip_path+folderval+'4-TestMat/'#+'FOV'+str(fov)+ '/'
        
            #Folder that holds the Location.tif files
        self.locationtif=wip_path+folderval+'5-LocationTif/'#+'FOV'+str(fov)+ '/'
        
            #Folder that holds the ROI.tif files
        self.roitif=wip_path+folderval+'6-ROITif/'#+'FOV'+str(fov)+ '/'
        
            #Folder that holds the Fluor.tif files
        self.fluortif=wip_path+folderval+'7-FluorTif/'#+'FOV'+str(fov)+ '/'
        
            #Folder that holds the Test.tif files
        self.testtif=wip_path+folderval+'8-TestTif/'#+'FOV'+str(fov)+ '/'

            #The FOV the user has selected
        self.fov=['FOV'+ str(fov)]

            #Folder that holds the Raw tif Images for final figures
        self.raw=wip_path+folderval+'zRaw_Images/'#+'FOV'+str(fov)+ '/'
        if os.path.exists(self.raw+self.fov[0]+'/') == False:
            os.mkdir(self.raw+self.fov[0]+'/')
            print('Creating FOV Folder for zRaw_Images...')
            log.info('Creating FOV Folder for zRaw_Images...')

        if os.path.exists(self.zExtra+self.fov[0]+'/') == False:
            os.mkdir(self.zExtra+self.fov[0]+'/')
            print('Creating FOV Folder for zExtra...')
            log.info('Creating FOV Folder for zExtra...')          

        
            #Get the folder where we are going to store the 2theta figures from the MAPS in
        self.ims_2theta=wip_path+folderval+'IMS_2theta/'+self.fov[0]+'/'
        if os.path.exists(self.ims_2theta) == False:
            os.mkdir(self.ims_2theta)
            print('Creating FOV Folder for ims_2theta...')
            log.info('Creating FOV Folder for ims_2theta...')
        
            #Get the folder where we are going to store the chi figures from the MAPS in 
        self.ims_chi=wip_path+folderval+'IMS_chi/'+self.fov[0]+'/'
        if os.path.exists(self.ims_chi) == False:
            os.mkdir(self.ims_chi)
            print('Creating FOV Folder for ims_chi...')
            log.info('Creating FOV Folder for ims_chi...')
        
            #Get the folder where we are going to store the summed diffraction figures from the MAPS in 
        self.ims_summeddif=wip_path+folderval+'IMS_summeddif/'+self.fov[0]+'/'
        if os.path.exists(self.ims_summeddif) == False:
            os.mkdir(self.ims_summeddif)
            print('Creating FOV Folder for ims_summeddif...')
            log.info('Creating FOV Folder for ims_summeddif...')


            #An array of the scan numbers the user wants to load into the program
        self.scanlist=scanlist
        
            #An array of the scan angles for the selected scan numbers the user wants to import
        self.scanangles=scanangles
        
            #The state of the particle the user is looking at
        self.samplestate=sample

            #Gets the User defined folderpath to save images to
        self.folder_path=folder_path

        
       
        
            #Different folder locations for the various output image types (.png,.pdf,.pgf,.tif)
        self.Imagespdf=wip_path+folderval+'Images/PDF/'
        self.Imagespgf=wip_path+folderval+'Images/PGF/'
        self.Imagespng=wip_path+folderval+'Images/PNG/'
        self.Imagesraw=wip_path+folderval+'Images/RAW/'
        log.info('Checking To See If Files Already Exsist In Folders Before Moving Them...')
        images_change_dir=os.listdir(self.data_pre)
        if 'Link to Images' in images_change_dir:
            if 'Images' in images_change_dir:
                warnings.warn('Images folder already created. Will not overwrite file.')
                log.info('Found Files In Folders. Will Not Overwrite.')
            else:
                os.rename(self.data_pre+'Link to Images',self.data_pre+'Images')
        images_change_dir=os.listdir(self.data_pre)
        if 'Images' in images_change_dir:
            pass
        else:
            warnings.warn('You have forgotten to put the linked images folder in '+ self.data_pre)
        
            #Takes the Matlab Code the user puts into the WIP^ folder and places it into the correct FOV
        log.info('Taking Matlab Code Output And Placing It Into The Correct FOV...')
        Matlab_Move(self,'mat')
        Mat_to_Tif_Auto(self)
        Matlab_Move(self,'tif')




       
        if dx!='' and dy!='': 
            log.info('dx And dy Movements Set To User Input...')
            #dx of the selected particle state and FOV
            self.dx=dx
        
            #dy of the selected particle state and FOV
            self.dy=dy
        
        elif dx=='' and dy=='':
            log.info('dx And dy Movements Being Calulated From LocationTif Files...')
            dxarr=[]
            dyarr=[]
            
            for images in self.orderedfilenames_TIF('location')[0][0]:

                im=imageio.imread(self.locationtif+self.fov[0]+'/'+images)
                dxarr.append(np.where(im==1000000)[1])
                dyarr.append(np.where(im==1000000)[0])

            firstx=dxarr[0][0]
            firsty=dyarr[0][0]
            movementx=[]
            movementy=[]
            for array in dxarr:
                movementx.append(firstx-array[0])

            for array in dyarr:
                movementy.append(firsty-array[0])

            self.dx=movementx[1:len(movementx)]
            self.dy=movementy[1:len(movementy)]
        else:
            print(self.samplename+' dx And dy Movements Are Messed Up')
            log.info('Cannot Determine dx And dy Movements...')
      
        

        log.info('__init__ END')
       

           #Takes the raw tif image file for the chi, 2theta, roi, and summed dif and loads them into memory 
    def chi_im(self):     
        im=imageio.imread(self.raw+self.fov[0]+'/chi_raw.tif')
        return im
    
    def twotheta_im(self):
        im=imageio.imread(self.raw+self.fov[0]+'/2theta_raw.tif')
        return im

    
    def roi_im(self):
        im=imageio.imread(self.raw+self.fov[0]+'/roi_raw.tif')
        return im

        
    def summed_dif_im(self):
        im=imageio.imread(self.raw+self.fov[0]+'/summed_dif_raw.tif')
        return im

        #Allows the user to get the ordered file names of the .MAT files for the user selected folder (location, roi, fluor, or test)
    def orderedfilenames_MAT(self,fol_type):
        log.info('orderedfilenames_MAT BEGIN')
        log.info('Determening The Ordered Files For The Mat Folder - '+fol_type+' -')
        if fol_type=="location":
            file_type=self.locationmat
        
        elif fol_type=='roi':
            file_type=self.roimat
        
        elif fol_type=='fluor':
            file_type=self.fluormat
        
        elif fol_type=='test':
            file_type=self.testmat
        
        a=0                                                               # Arbitrary variable of 0 for a starting value for my forloop
        arr = [[] for _ in range(1)]                                      # Blank matrix for my forloop
        for b in range(0,len(self.fov)):                                  # loop that grabs all the file names in each folder selected by the user
        # Getting all the filenames from one of the folders. Fun in a loop to get all the file names the user wants.
            for dirpath,dirnames,filenames in walk(file_type+self.fov[a]):
                a=a+1                                                     # step to the next value in X
                arr[0].append(sorted(filenames))                          # append the filenames variable with the all the filenames in the folders
        c=sorted(arr)                                                     # Need to sort all the filenames
        modifiedlist=list(filter(None,c))                                 # Filter out all the blank cells in the list   
        log.info('orderedfilenames_MAT END') 
        return modifiedlist                                               # Returns the sorted list of file names


    def orderedfilenames_detector(self,folder='None'):
        log.info('orderedfilenames_detector BEGIN')
        log.info('Determening The Ordered Files For Folder - zDetector -')
        file_type=self.detector
        if folder=='None':
            print('You Have To Set A Folder Number')


        a=0                                                               # Arbitrary variable of 0 for a starting value for my forloop
        arr = [[] for _ in range(1)]                                      # Blank matrix for my forloop
        for b in range(0,len(self.fov)):                                  # loop that grabs all the file names in each folder selected by the user
        # Getting all the filenames from one of the folders. Fun in a loop to get all the file names the user wants.
            for dirpath,dirnames,filenames in walk(file_type+folder+'/'):
                a=a+1                                                     # step to the next value in X
                arr[0].append(sorted(filenames))                          # append the filenames variable with the all the filenames in the folders
        c=sorted(arr)                                                     # Need to sort all the filenames
        modifiedlist=list(filter(None,c))                                 # Filter out all the blank cells in the list   
        log.info('orderedfilenames_detector END') 
        return modifiedlist                     


        #Allows the user to get the ordered file names of the .TIF files for the user selected folder (location, roi, fluor, or test)
    def orderedfilenames_TIF(self,fol_type):
        log.info('orderedfilenames_TIF BEGIN')
        log.info('Determening The Ordered Files For The Tif Folder - '+fol_type+' -')
        
        if fol_type=="location":
            file_type=self.locationtif
        
        elif fol_type=='roi':
            file_type=self.roitif
        
        elif fol_type=='fluor':
            file_type=self.fluortif
        
        elif fol_type=='test':
            file_type=self.testtif  
             
        a=0                                                               # Arbitrary variable of 0 for a starting value for my forloop
        arr = [[] for _ in range(1)]
        if os.listdir(file_type+self.fov[a])==[]:
            self.Mat_to_Tif('location')  
                                                                          # Blank matrix for my forloop
        for b in range(0,len(self.fov)):                                  # loop that grabs all the file names in each folder selected by the user
        # Getting all the filenames from one of the folders. Fun in a loop to get all the file names the user wants.
            for dirpath,dirnames,filenames in walk(file_type+self.fov[a]):
                a=a+1                                                     # step to the next value in X
                arr[0].append(sorted(filenames))                          # append the filenames variable with the all the filenames in the folders
        c=sorted(arr)                                                     # Need to sort all the filenames
        modifiedlist=list(filter(None,c))                                 # Filter out all the blank cells in the list 
        log.info('orderedfilenames_TIF END')   
        
        return modifiedlist                                               # Returns the sorted list of file names 

        #Grabs the names of all the .tif images from every scan the user has selected
    def orderedfilenames_beamline_images(self):
        log.info('orderedfilenames_beamline_images BEGIN')
        a=0                                                               # Arbitrary variable of 0 for a starting value for my forloop
        arr = [[] for _ in range(1)]                                      # Blank matrix for my forloop
        for b in range(0,len(self.scanlist)):                             # loop that grabs all the file names in each folder selected by the user
                                                                          # Getting all the filenames from one of the folders. Fun in a loop to get all the file names the user wants.
            for dirpath,dirnames,filenames in walk(self.data+self.scanlist[a]):
                a=a+1                                                     # step to the next value in X
                arr[0].append(sorted(filenames))                          # append the filenames variable with the all the filenames in the folders
        c=sorted(arr)                                                     # Need to sort all the filenames
        modifiedlist=list(filter(None,c))                                 # Filter out all the blank cells in the list  
        log.info('orderedfilenames_beamline_images END')  
        return modifiedlist                                               # Returns the sorted list of file names 
        #Returns the shape of all the .mat files for a specific fol_type(roi,location,fluor,test)
    def shapeMAT(self,fol_type,matlab_variable=['data2']):   
        log.info('shapeMAT BEGIN') 
        log.info('Getting The Shape Of The Matlab Files...')
        shape=[]
        ordered_shapeMAT=self.orderedfilenames_MAT(fol_type=fol_type)
        iterations_for_shapeMAT=len(ordered_shapeMAT[0][0])
        for i in range(0,iterations_for_shapeMAT):
            initial_data=scipy.io.loadmat(self.locationmat+self.fov[0]+'/'+ordered_shapeMAT[0][0][i])[matlab_variable[0]]
            output_data=np.asarray(initial_data).astype('uint32')
            shape.append(np.shape(output_data))
        log.info('shapeMAT END') 
        return shape
        #Returns the dxdy array that is easily accessable by the program

    def dxdy(self):
        log.info('dxdy BEGIN') 
        starting_dx=0
        starting_dy=0
        dx1=[[starting_dx]+self.dx]
        dy1=[[starting_dy]+self.dy]
        dx2=np.asarray(dx1)
        dy2=np.asarray(dy1)
        dxdy=[[g, h] for g, h in zip(dx2,dy2)]
        log.info('dxdy END') 
        return dxdy
        #Returns the image locations of all the beamline .tif images in their proper location in a matrix
    def Location_Data(self):
        log.info('Location_Data BEGIN') 
        log.info('Based On The dx And dy Movements We Are Calculating Matrix Movements For The Location_Data For The Beamline Images...')
        #Redefining the variables used. This used to be a function and I am changing it into a class so it can easily be changed
        dx=self.dx
        dy=self.dy
        starting_dx=0
        starting_dy=0
        dx1=[[starting_dx]+self.dx]
        dy1=[[starting_dy]+self.dy]
        dx2=np.asarray(dx1)
        dy2=np.asarray(dy1)
        dxdy=[[g, h] for g, h in zip(dx2,dy2)]
        folderlocation=self.data
        foldernames=self.scanlist
        orderedfilenames=self.orderedfilenames_beamline_images()
        shape=self.shapeMAT(fol_type='roi')



        location_data=[]                               #Blank array I can write the location data to
        maxarr=np.asarray(max(shape))                  #Takes the list of all the shapes and finds the max

        for k in range(len(shape)):
            m=0                                        #Reset value for the x location in array
            a=[[None for x in range(maxarr[1])] for y in range(maxarr[0])]    #Creates a blank array based on the largest shape size
            for j in range(0,shape[k][0]):    
                for i in range(0,shape[k][1]):
                    if i+dxdy[0][0][k]>=0 and shape[k][0]-1-j+dxdy[0][1][k] >=0:

                        try:
                            a[shape[k][0]-1-j+dxdy[0][1][k]][i+dxdy[0][0][k]]=[folderlocation+foldernames[k]+'/'+orderedfilenames[0][k][(shape[k][1]*m)+i]]   #Grabs the image file location (the full location), corrects for dx and dy in particle movement, and stores that image location in the proper location in the array
                        except:
                            pass                            #Sometimes when you add the correction the location will be outisde the bounds of the created array. This allows you to ignore and image files that fall outside these bounds
                    else:
                        pass
                m=m+1

            location_data.append(a)
        log.info('Location_Data END') 
        return location_data
        #Summes all the data given in the beamline data images
    def summeddif_cal(self,new_location_data,contrast_change,vmin='',vmax='',background_sub='y',background_sub_reverse='n',multiplier=1,num_ims_to_ave=2,roi_box_calc=False):                    #Does the same thing as the Summedarray tool, but this does it on the shifted data collected from this program to make sure the user is doing everything correctly 
        """Allows the User to create a summed diffraction pattern from their data

	Variables--

	new_location_data: (string w/ values of 'y' or 'n')
		- If this function is before the roi_crop functions set this value to             'n'. If it comes after then set this value to 'y'

	contrast_change: (string w/ values of 'y' or 'n')
		- If you just want to change the contrast (maxval) without rerunning the          entire function set this value to 'y'

	vmin: (string w/ values of 'y' or 'n')
		- Use the histogram to determine the vmin of the data.

	vmax: (string w/ values of 'y' or 'n')
		- Use the histogram to determine the vmax of the data.

	background_sub: (string w/ values of 'y' or 'n')
		- Ask the User if they want to add a background scan subtraction to the           Summed Diffraction Pattern

	background_sub_reverse: (string w/ values of 'y' or 'n')
		- Ask the User if they want to invert the background subtraction. This            is usefull for when the array vlues overflow and reset to very high             values. This will cause the contrast of the SumDif to be off

	multiplier: (number)
		- Set the multiplier for the background value. This helps in some diffra          -ction signal cases. A go to if your diffraction signal looks off is            setting this value to equal 2

        num_ims_to_ave: (number)
                - This value is associated with the number of images from the beginning of the scan and at the end of the scan in which the program avergages together in order to make a background image for each scanning angle. Increase this number if your background in your summed diffraciton pattern does not look great.

	Returns--
	
	A numpy image matrix with the summed diffraction pattern


      """
        log.info('summeddif_cal BEGIN') 
        log.info('Summed Diffraction Pattern & Histogram')
        if roi_box_calc==False:
            print('The Summed Array Image Matrix Will Be Saved As self.s_arr')
            print(' ')
        self.rois_new_location_data=new_location_data
        self.rois_contrast_change=contrast_change
        self.rois_background_sub=background_sub
        self.rois_background_sub_reverse=background_sub_reverse
        self.rois_multiplier=multiplier
        self.rois_num_ims_to_ave=num_ims_to_ave

        	 
        time.sleep(0.5)
        length=self.tif_dim()
        shape=self.shapeMAT(fol_type='roi')
        foldernames=self.scanlist
        location_data=self.Location_Data()
        rerunall=contrast_change                   #Didnt want to rewrite all the code. rerunall doesnt mean rerunall look at this line of code. It means are you changing the contrast
        if contrast_change=='n':
            print('Initializing Background Creation...')
            log.info('Initializing Background Creation...')
            time.sleep(2)
            background_arr=self.background_for_summed(num_ims_to_ave,multiplier,5,10)
        if new_location_data=='y':
            location_data=self.location_data_crop()
        
        if rerunall=='n':
            tot_data=[[0 for x in range(length)] for y in range(length)]  
            if roi_box_calc==True:          
                roi_data = [[[0 for x in range(max(shape)[1])] for y in range(max(shape)[0])] for z in range(len(self.roi_boxes))]
            print(' ')
            print('Initializing Summed Diffraction Program...')
            time.sleep(2)
            for k in tqdm(range(0,max(shape)[0])):                           #            #For the x dim of the roi                                        

                for j in range(0,max(shape)[1]):                                    #for the y dim of the roi
                    spot_data=[]
                    for i in range(0,len(foldernames)):

                        try:
                            im=imageio.imread(location_data[i][k][j][0]).astype('uint32')
                            if background_sub=='n':
                                im2=np.subtract(im,0)
                            elif background_sub=='y':
                                if background_sub_reverse=='n':
                                    im2=np.subtract(im,background_arr[i])
                                elif background_sub_reverse=='y':                                   
                                    im2=np.subtract(

background_arr[i],im)                             
                            spot_data.append(im2)

                        except:
                            pass
                    try:
                        summed_spot=np.sum(spot_data,axis=0) 
                        tot_data=np.add(tot_data,summed_spot)
                        if roi_box_calc==True:
                            for variable,box in enumerate(self.roi_boxes):
                                roi_cropping=np.sum(summed_spot[box[1]:box[1]+box[3],box[0]:box[0]+box[2]],axis=0)
                                roi_cropping_med_blur=Wills_Median_Blur_With_Low(roi_cropping,4,10)
                                roi_cropping_sum=np.sum(roi_cropping_med_blur,axis=0)
                                roi_data[variable][k][j]=roi_cropping_sum



                    except:
                        pass
            time.sleep(1)
            log.info(str(np.min(tot_data))+'      '+str(np.max(tot_data)))
            if roi_box_calc == False:            
                fig=plt.figure(figsize=(20,10))
                grid = plt.GridSpec(2, 3, wspace=0.4, hspace=0.3)
                plt.subplot(grid[0, 0])
            

                if vmin=='' and vmax=='':
                    fig1=plt.imshow(tot_data,vmin=np.min(tot_data),vmax=np.max(tot_data))
                    plt.subplot(grid[0, 1:])
                    fig2=plt.hist(tot_data.flatten(), bins=30,range=(np.min(tot_data),np.max(tot_data)*1.1))
                    self.rois_vmin=np.min(tot_data)
                    self.rois_vmax=np.max(tot_data)
                elif vmin!='' and vmax!='':
                    fig1=plt.imshow(tot_data,vmin=vmin,vmax=vmax)
                    plt.subplot(grid[0, 1:])
                    fig2=plt.hist(tot_data.flatten(), bins=30,range=(np.min(tot_data),np.max(tot_data)*1.1))
                    self.rois_vmin=vmin
                    self.rois_vmax=vmax  
                elif vmin!='' and vmax=='':
                    fig1=plt.imshow(tot_data,vmin=vmin,vmax=np.max(tot_data))
                    plt.subplot(grid[0, 1:])
                    fig2=plt.hist(tot_data.flatten(), bins=30,range=(vmin,np.max(tot_data)*1.1)) 
                    self.rois_vmin=vmin
                    self.rois_vmax=np.max(tot_data)
                elif vmin=='' and vmax!='':
                    fig1=plt.imshow(tot_data,vmin=np.min(tot_data),vmax=vmax)
                    plt.subplot(grid[0, 1:])
                    fig2=plt.hist(tot_data.flatten(), bins=30,range=(np.min(tot_data),vmax)) 
                    self.rois_vmin=np.min(tot_data)
                    self.rois_vmax=vmax 

                 


            if new_location_data=='n':
                self.s_arr=tot_data
                print('Max X: ',self.max_x(),' Max Y: ',self.max_y(),'     Min Value: '+str(round(np.min(tot_data),2))+'   Max Value: '+str(round(np.max(tot_data),2)))
            
            elif new_location_data=='y':
                self.s_arr2=tot_data
                print('Min Value: '+str(round(np.min(tot_data),2))+'   Max Value: '+str(round(np.max(tot_data),2)))
            log.info('summeddif_cal END') 
            if roi_box_calc==False:
                return tot_data
            elif roi_box_calc==True:
                return tot_data, roi_data

        else:

            try:
                randoval=self.s_arr
            except:
                warnings.warn('You Have To Run Program Before You Can Change The Contrast. Set Contrast Variable To Equal n')
            if new_location_data=='n':
                im_arr=self.s_arr
                print('Max X: ',self.max_x(),' Max Y: ',self.max_y())
            
            
            elif new_location_data=='y':
                try:
                    randoval=self.s_arr2
                except:
                    warnings.warn('This Parameter Is Set To A New Location. Cant Change Contrast Yet. Set Contrast Variable To Equal n')
                im_arr=self.s_arr2      

            
            if roi_box_calc == False:
                fig=plt.figure(figsize=(20,10))
                grid = plt.GridSpec(2, 3, wspace=0.4, hspace=0.3)


                plt.subplot(grid[0, 0])
                if vmin=='' and vmax=='':
                    fig1=plt.imshow(im_arr,vmin=np.min(im_arr),vmax=np.max(im_arr))
                    plt.subplot(grid[0, 1:])
                    fig2=plt.hist(im_arr.flatten(), bins=30,range=(np.min(im_arr),np.max(im_arr)*1.5))
                    self.rois_vmin=np.min(im_arr)
                    self.rois_vmax=np.max(im_arr)
                elif vmin!='' and vmax!='':
                    fig1=plt.imshow(im_arr,vmin=vmin,vmax=vmax)
                    plt.subplot(grid[0, 1:])
                    fig2=plt.hist(im_arr.flatten(), bins=30,range=(vmin,vmax*1.5))
                    self.rois_vmin=vmin
                    self.rois_vmax=vmax
                elif vmin!='' and vmax=='':
                    fig1=plt.imshow(im_arr,vmin=vmin,vmax=np.max(im_arr))
                    plt.subplot(grid[0, 1:])
                    fig2=plt.hist(im_arr.flatten(), bins=30,range=(vmin,np.max(im_arr)*1.5))
                    self.rois_vmin=vmin
                    self.rois_vmax=np.max(im_arr)
                elif vmin=='' and vmax!='':
                    fig1=plt.imshow(im_arr,vmin=np.min(im_arr),vmax=vmax)
                    plt.subplot(grid[0, 1:])
                    fig2=plt.hist(im_arr.flatten(), bins=30,range=(np.min(im_arr),vmax*1.5))
                    self.rois_vmin=np.min(im_arr)
                    self.rois_vmax=vmax
            print('Min Value: '+str(round(np.min(im_arr),2))+'   Max Value: '+str(round(np.max(im_arr),2)))
            log.info('summeddif_cal END') 
            if roi_box_calc==False:
                return self.s_arr
            elif roi_box_calc==True:
                return self.s_arr, roi_data




    def new_roi_step1(self,roi_boxes='',color=['r','r','r','r']):
        """
        This will help define your ROIs. set up the roi_boxes variable as [(70, 350, 120, 500),(190, 350, 120, 500),(450, 300, 160, 600)]

        """
        if roi_boxes == '':
            roi_boxes = [(0,0,self.tif_dim(),self.tif_dim())]
        fig,ax = plt.subplots(1)
    # Display the image
        ax.imshow(self.s_arr,vmin=self.rois_vmin,vmax=self.rois_vmax)
        arrs=[]
        for variable,box in enumerate(roi_boxes):
    # Create a Rectangle patch
            color_var=color[variable]
            rect = patches.Rectangle((box[0],box[1]),box[2],box[3],linewidth=1,edgecolor=color_var,facecolor='none')
            plt.annotate(str(variable),(box[0]+box[2]/2,box[1]+box[3]/2),color=color_var,ha='center')
    # Add the patch to the Axes
            ax.add_patch(rect)
        self.roi_boxes=roi_boxes


    def new_roi_step2(self,rgb_multiplier=1):
        print('The Last ROI Box Defined Is Set To self.roi_master. Every Other ROI Will Be Normalized To RGB')
        print('')
        #will assume your last roi is the full_roi_region
        num_rois=len(self.roi_boxes)
        if num_rois<=4:
            summarr,roi_dats=self.summeddif_cal(self.rois_new_location_data,
                                                 'n',
                                                 self.rois_vmin,
                self.rois_vmax,
                self.rois_background_sub,
                self.rois_background_sub_reverse,
                self.rois_multiplier,
                self.rois_num_ims_to_ave,
                roi_box_calc=True)

            shape=self.shapeMAT(fol_type='roi')
            blank_dats=[[0 for x in range(max(shape)[1])] for y in range(max(shape)[0])] 

            if num_rois>1 and num_rois<=4:
                max_for_rgb=np.max(roi_dats[0:num_rois-1])

            if num_rois==4:
                norm_RGB=np.dstack(((roi_dats[0]/max_for_rgb)*rgb_multiplier,
                                          (roi_dats[1]/max_for_rgb)*rgb_multiplier
                                          ,(roi_dats[2]/max_for_rgb)*rgb_multiplier))
            if num_rois==3:
                norm_RGB=np.dstack(((roi_dats[0]/max_for_rgb)*rgb_multiplier,
                                          (roi_dats[1]/max_for_rgb)*rgb_multiplier
                                          ,blank_dats))
            if num_rois==2:
                norm_RGB=np.dstack(((roi_dats[0]/max_for_rgb)*rgb_multiplier,
                                          blank_dats,
                                          blank_dats))


            master_roi = roi_dats[-1]
            if num_rois==1:
                warnings.warn('Only 1 ROI area given. norm_rgb roi has been set to equivalent to the master_roi')
                norm_RGB=master_roi
            self.roi_data_raw = roi_dats
            self.roi_norm_RGB = norm_RGB
            self.roi_master = master_roi
            print('raw roi data saved to self.roi_data_raw')
        else:
            warnings.warn('The program can only do a max of 4 rois (3 for RGB and 1 for Total ROI). Please correct your mistake.')
        f, (ax1, ax2) = plt.subplots(1, 2)
        ax1.imshow(self.roi_master)
        ax1.set_title('self.roi_master')
        ax2.imshow(self.roi_norm_RGB)
        ax2.set_title('self.roi_norm_RGB')


        #Gives the max x dimension of the ROI
    def max_x(self):
        return (np.max([row[1] for row in self.shapeMAT('roi')]))
        #Gives the max y dimension of the ROI
    def max_y(self):
        return int(np.max([row[0] for row in self.shapeMAT('roi')]))
        #Test Variable 
    def movedroi(self):
        pass
        #Checks to see if what you have in frame has a good gaussian curve to the intensities for the rocking angles
    def gaussiancheck(self,tshoot='n'):
        """ Plots the Intensity vs Rocking angle for the ROI cop the User has assigned 
	Variables--
	
		- None. Just make sure to use self.gaussiancheck()

	Returns--

		- A figure of what was show to the User.   

        """	
        fig=plt.figure()
        y_arr=[]
        x=self.scanangles
        print('Gaussian Check')
        time.sleep(0.5)
        
        if len(x) == np.shape(self.Corrected_Matrix)[0]:
            find_the_range = len(x)
        elif len(x) != np.shape(self.Corrected_Matrix)[0]:
            find_the_range = len(x)
            warnings.warn('x and y dimensions are off. Program corrected as best it could.') 
             
        
        for i in range(0,find_the_range):
            y_arr.append(np.sum(self.Corrected_Matrix[i]))
        if tshoot=='y':
            return self.scanangles,x,y_arr
        elif tshoot=='n':
            plt.title(self.samplestate+' '+self.fov[0])
            plt.xlabel('Rocking Angle')
            plt.ylabel('Total Diffraction Signal')
            plt.scatter(x,y_arr)

            return fig
        
        #Crops the ROI image to what the user wants and outputs the image as Corrected_Matrix
    def roi_crop_pre(self,start_x,end_x,start_y,end_y,vmin='',vmax=''):

        """Allows the User to crop the ROI to focus on a specific area.

        Variable--

        start_x: (number)
		- the starting index for the x values the user wants to begin their crop at
        end_x: (number)
		- the ending index of the x values the user wants to end their crop at

        start_y: (number)
		- the starting index for the y values the user wants to begin their crop at
        end_y: (number)
		- the ending index of the y values the user wants to end their crop at
	
        vmin: (number)
        	- the lowest contrast value the user wants to set so the ROI image is clear
        vmax: (number)
        	- the highest contrast value the user wants to set so the ROI image is clear

        Returns--

        Nothing. Only shows the figure made inside the function.



        """
        print('ROI Crop Pre Data Correction')
        time.sleep(0.5)
        Corrected_Matrix=[]
        dxdy=self.dxdy()
        x_length=self.max_x()
        y_length=self.max_y()
        
        for k in range(0,len(self.shapeMAT(fol_type='roi'))):
            im=imageio.imread(self.roitif+self.fov[0]+'/'+self.orderedfilenames_TIF(fol_type='roi')[0][0][k])

            Burner_Mat=[[0 for x in range(x_length)] for y in range(y_length)]


            for i in range(start_y,end_y):
                for j in range(start_x,end_x):

                    if i-dxdy[0][1][k]>=0 and j-dxdy[0][0][k]>=0 and i-dxdy[0][1][k]<y_length and j-dxdy[0][0][k]<x_length:

                        Burner_Mat[i][j]=im[i-dxdy[0][1][k]][j-dxdy[0][0][k]]
                    else:
                        pass


            Corrected_Matrix.append(Burner_Mat)
        
        newim=np.sum(Corrected_Matrix,axis=0)

        fig=plt.figure(figsize=(20,10))
        grid = plt.GridSpec(2, 3, wspace=0.4, hspace=0.3)
        plt.subplot(grid[0, 0])
            

        if vmin=='' and vmax=='':
            fig1=plt.imshow(newim,vmin=np.min(newim),vmax=np.max(newim))
            plt.subplot(grid[0, 1:])
            fig2=plt.hist(newim.flatten(), bins=30,range=(np.min(newim),np.max(newim)*1.1)) 
        elif vmin!='' and vmax!='':
            fig1=plt.imshow(newim,vmin=vmin,vmax=vmax)
            plt.subplot(grid[0, 1:])
            fig2=plt.hist(newim.flatten(), bins=30,range=(np.min(newim),np.max(newim)*1.1)) 
        elif vmin!='' and vmax=='':
            fig1=plt.imshow(newim,vmin=vmin,vmax=np.max(newim))
            plt.subplot(grid[0, 1:])
            fig2=plt.hist(newim.flatten(), bins=30,range=(vmin,np.max(newim)*1.1)) 
        elif vmin=='' and vmax!='':
            fig1=plt.imshow(newim,vmin=np.min(newim),vmax=vmax)
            plt.subplot(grid[0, 1:])
            fig2=plt.hist(newim.flatten(), bins=30,range=(np.min(newim),vmax))         

        #plt.figure()
        #plt.imshow(newim,vmin=0,vmax=vmax)
        #plt.figure(figsize=(20,10))
        newim2=np.asarray(newim)
        if vmax=='':
            vmax=np.max(newim)
        if vmin=='':
            vmin=np.min(newim)
        
        
        self.x_length=x_length
        self.y_length=y_length
        self.start_x=start_x
        self.end_x=end_x
        self.start_y=start_y
        self.end_y=end_y
        self.Corrected_Matrix=Corrected_Matrix
        self.roivmax=vmax
        self.roivmin=vmin
        self.roi_crop_pre_im=newim
        
        
        #Changed all the zeros the Corrected_Matrix image to a non zero value based on the background values
    def roi_crop_post(self,row,left_col,right_col,show_new_summeddif='n',vmax=''):

        """ Fixes the roi_crop_pre

		roi_crop_post moves the images around depending on the particle drift. This function gives the User control over adding background noise to missing array values from when the alignment of the 		ROI's happened. This needs to happen inorder for the gaussiancheck function to give an accurate result.
	
	Variables--
	
	row: (number)
		- based on the roi_crop_pre image pick a row in which the particle you are looking at does not exist in

	left_col: (number)
		- based on the roi_crop_pre image pick a left starting column of the row you selected in which the particle you are looking at does not exist in

	right_col: (number)
		- based on the roi_crop_pre image pick a right ending column of the row you selected in which the particle you are looking at does not exist in
  
        show_new_summeddif: (str)
                - 'y' or 'n' string that allows the user to calculte the summed diffraction pattern for the roi selected

        vmax: (int)
                - an integer number that determines the vmax of the plt.imshow() vmax function. 

	Returns--

	The figure that was made. The User can also call self.roi_crop_post_im to get the numpy image array for the figure displayed. 

        """

        print('ROI Crop Post Data Correction')
        time.sleep(0.5)
        for i in range(0,np.shape(self.Corrected_Matrix)[0]):
            ave=self.Corrected_Matrix[i][row][left_col:right_col]
    
    
            for j in range(0,self.y_length):
        
                for k in range(0,self.x_length):
                    if self.Corrected_Matrix[i][j][k]==0:
                        len_var=right_col-left_col
                        ran_num=random.randint(1,len_var-1)
                    
                        self.Corrected_Matrix[i][j][k]=ave[ran_num]
                        
        newim=np.sum(self.Corrected_Matrix,axis=0)
        fig=plt.figure()
        plt.imshow(newim,vmin=self.roivmin,vmax=self.roivmax)
        plt.figure(figsize=(20,10))
        newim2=np.asarray(newim)
        
        self.roi_crop_post_fig=fig
        self.roi_crop_post_im=newim2
        if show_new_summeddif!='n':
            self.summeddif_cal_cropped(vmax=vmax)
        
        return fig
    
        #Work in progress do not use
#    def save(self,fig,raw,im_type):
#        
#        
#        if im_type=='roi':
#            ims_type='roi'
#            
#        if im_type=='summeddif':
#            ims_type='summed_dif'
#        
#        if im_type=='chi':
#            ims_type='chi'
#            
#        if im_type=='2theta':
#            ims_type='2theta'
#        
#        fig.savefig(self.Imagespdf+self.samplestate+self.fov[0]+'_'+ims_type+'.pdf',bbox_inches='tight',dpi=300)
#        fig.savefig(self.Imagespng+self.samplestate+self.fov[0]+'_'+ims_type+'.png',bbox_inches='tight',dpi=300)
#        fig.savefig(self.Imagespgf+self.samplestate+self.fov[0]+'_'+ims_type+'.pgf',bbox_inches='tight',dpi=300)
        
#        imageio.imwrite(self.Imagesraw+self.samplestate+self.fov[0]+'_'+ims_type+'_raw.tif',raw)
      
    def background_for_summed(self,imagestoaverage,multiplier,med_blur_number,med_blur_high):
        log.info('background_for_summed BEGIN')
        #print('If the data doesn''t look right set the multiplier a different value. Setting it to equal 2 usually works \nThe User can also set the background_sub_reverse variable to equal ''y''')
        #There are a lot of random values in this section of code because I duplicated it from another section and don't want to take the parts of the code out that arnt being used
        Chior2Theta2='chi'
        axi=CHIor2THETA(Chior2Theta2)
        #print(axi)
        orderedfilenames=self.orderedfilenames_beamline_images()
        foldernames=self.scanlist
        folderlocation=self.data



        x=imagestoaverage                               #Too lazy to rewrite code. This just changes the variable name
        endlocation=len(orderedfilenames[0][0])-1       #Get the end location of the orderedfilenames of the first file
        ims=[]                                          #Create an empty array for me to append things to
        mean_ims=[]                                     #Create another empty array for me to append my means to
        total_mean_ims=[]
        for j in tqdm(range(0,len(foldernames))):
            ims=[]                                          #Create an empty array for me to append things to
            mean_ims=[]
            for i in range(0,x):

                im1t=imageio.imread(folderlocation+foldernames[0]+'/'+orderedfilenames[0][0][i]).astype('uint32')
                #im1t2=np.sum(im1t,axis=axi)
                #im1=Wills_Median_Blur(im1t2,med_blur_number,med_blur_high)
                ims.append(im1t)                             #Import image from the beginning then append file to empty array

                im2t=imageio.imread(folderlocation+foldernames[0]+'/'+orderedfilenames[0][0][endlocation-i]).astype('uint32')
                #im2t2=np.sum(im2t,axis=axi)
                #im2=Wills_Median_Blur(im2t2,med_blur_number,med_blur_high)
                ims.append(im2t)                             #Import image from the end then append file to the array

                mean_ims=np.mean(ims,axis=0).astype('uint32')   #Averaging the array we just created

            total_mean_ims.append(mean_ims)
        log.info('background_for_summed END')
        return (np.asarray(total_mean_ims)*multiplier).astype('uint32')    











        #Creates a background chi background image for each scan angle
    def background_chi(self,imagestoaverage,multiplier,med_blur_number,med_blur_high):
        log.info('background_chi BEGIN')
        #print('If the data doesn''t look right set the multiplier a different value. Setting it to equal 2 usually works')
        Chior2Theta2='chi'
        axi=CHIor2THETA(Chior2Theta2)
        #print(axi)
        orderedfilenames=self.orderedfilenames_beamline_images()
        foldernames=self.scanlist
        folderlocation=self.data



        x=imagestoaverage                               #Too lazy to rewrite code. This just changes the variable name
        endlocation=len(orderedfilenames[0][0])-1       #Get the end location of the orderedfilenames of the first file
        ims=[]                                          #Create an empty array for me to append things to
        mean_ims=[]                                     #Create another empty array for me to append my means to
        total_mean_ims=[]
        for j in tqdm(range(0,len(foldernames))):
            ims=[]                                          #Create an empty array for me to append things to
            mean_ims=[]
            for i in range(0,x):

                im1t=imageio.imread(folderlocation+foldernames[0]+'/'+orderedfilenames[0][0][i]).astype('uint32')
                im1t2=np.sum(im1t,axis=axi)
                im1=Wills_Median_Blur(im1t2,med_blur_number,med_blur_high)
                ims.append(im1)                             #Import image from the beginning then append file to empty array

                im2t=imageio.imread(folderlocation+foldernames[0]+'/'+orderedfilenames[0][0][endlocation-i]).astype('uint32')
                im2t2=np.sum(im2t,axis=axi)
                im2=Wills_Median_Blur(im2t2,med_blur_number,med_blur_high)
                ims.append(im2)                             #Import image from the end then append file to the array

                mean_ims=np.mean(ims,axis=0).astype('uint32')   #Averaging the array we just created

            total_mean_ims.append(mean_ims)
        log.info('background_chi END')
        return (np.asarray(total_mean_ims)*multiplier).astype('uint32')    
       #Creates a 2theta background image for each scan angle
    def background_2theta(self,imagestoaverage,multiplier,med_blur_number,med_blur_high):
        log.info('background_2theta BEGIN')
        Chior2Theta2='2theta'
        axi=CHIor2THETA(Chior2Theta2)
        #print(axi)
        orderedfilenames=self.orderedfilenames_beamline_images()
        foldernames=self.scanlist
        folderlocation=self.data



        x=imagestoaverage                               #Too lazy to rewrite code. This just changes the variable name
        endlocation=len(orderedfilenames[0][0])-1       #Get the end location of the orderedfilenames of the first file
        ims=[]                                          #Create an empty array for me to append things to
        mean_ims=[]                                     #Create another empty array for me to append my means to
        total_mean_ims=[]
        for j in tqdm(range(0,len(foldernames))):
            ims=[]                                          #Create an empty array for me to append things to
            mean_ims=[]
            for i in range(0,x):

                im1t=imageio.imread(folderlocation+foldernames[0]+'/'+orderedfilenames[0][0][i]).astype('uint32')
                im1t2=np.sum(im1t,axis=axi)
                im1=Wills_Median_Blur(im1t2,med_blur_number,med_blur_high)
                ims.append(im1)                             #Import image from the beginning then append file to empty array

                im2t=imageio.imread(folderlocation+foldernames[0]+'/'+orderedfilenames[0][0][endlocation-i]).astype('uint32')
                im2t2=np.sum(im2t,axis=axi)
                im2=Wills_Median_Blur(im2t2,med_blur_number,med_blur_high)
                ims.append(im2)                             #Import image from the end then append file to the array

                mean_ims=np.mean(ims,axis=0).astype('uint32')   #Averaging the array we just created

            total_mean_ims.append(mean_ims)
        log.info('background_2theta END')
        return (np.asarray(total_mean_ims)*multiplier).astype('uint32')  
        #crops the location data based on what the user has defined for the ROI crop
    def location_data_crop(self):
        log.info('location_data_crop BEGIN')
        foldernames=self.scanlist
        location_data=self.Location_Data()
        empty_list=[]
        for i in range(0,len(foldernames)):
            location_data_new=[[None for x in range(self.x_length)] for y in range(self.y_length)]
            for j in range(self.start_y,self.end_y):
                for k in range(self.start_x,self.end_x):
                    location_data_new[j][k]=location_data[i][j][k]
            empty_list.append(location_data_new)
        log.info('location_data_crop END')
        return empty_list

    def summeddif_cal_cropped(self,vmax=''):
        counter=1
        for location1 in self.location_data_crop():
            for location2 in location1:
                for location3 in location2:
                    try:
                        for location4 in location3:
                            if counter==1:
                                summed=imageio.imread(location4).astype('uint32')
                                counter=2
                            else:
                                summed=np.add(summed,imageio.imread(location4).astype('uint32'))

                    except:
                        pass


        if vmax=='':
            plt.imshow(summed)
        else:
            plt.imshow(summed,vmax=vmax)


    def raw_images_save(self):

        try:
            print('Your sub_fov is '+self.sub_fov)
        except:
            self.sub_fov=(input('What is the sub_fov of the data you are saving? '))
        save_dic=[
        self.raw+self.fov[0]+'/'+'s_arr_'+self.fov[0]+'.'+str(self.sub_fov)+'.tif',
        self.raw+self.fov[0]+'/'+'s_arr2_'+self.fov[0]+'.'+str(self.sub_fov)+'.tif',
        self.raw+self.fov[0]+'/'+'roi_norm_rgb_'+self.fov[0]+'.'+str(self.sub_fov)+'.png',
        self.raw+self.fov[0]+'/'+'roi_master_'+self.fov[0]+'.'+str(self.sub_fov)+'.tif',
        self.raw+self.fov[0]+'/'+'roi_crop_pre_im_'+self.fov[0]+'.'+str(self.sub_fov)+'.tif',
        self.raw+self.fov[0]+'/'+'roi_crop_post_im_'+self.fov[0]+'.'+str(self.sub_fov)+'.tif',
        self.raw+self.fov[0]+'/'+'chi_centroid_'+self.fov[0]+'.'+str(self.sub_fov)+'.tif',
        self.raw+self.fov[0]+'/'+'ttheta_centroid_'+self.fov[0]+'.'+str(self.sub_fov)+'.tif']
        print('')
        save_var_im=[]
        counter_array=[]
        error_array=[]
        saved_array=[]

        try:
            save_var_im.append(self.s_arr)
            counter_array.append(0)
            saved_array.append('Saved s_arr')
        except:
            error_array.append('Unable to save s_arr')

        try:
            save_var_im.append(self.s_arr2)
            counter_array.append(1)
            saved_array.append('Saved s_arr2')
        except:
            error_array.append('Unable to save s_arr2')

        try:
            save_var_im.append(self.roi_norm_RGB)
            counter_array.append(2)
            saved_array.append('Saved roi_norm_RGB')
        except:
            error_array.append('Unable to save roi_norm_RGB')

        try:
            save_var_im.append(self.roi_master)
            counter_array.append(3)
            saved_array.append('Saved roi_master')
        except:
            error_array.append('Unable to save roi_master')

        try:
            save_var_im.append(self.roi_crop_pre_im)
            counter_array.append(4)
            saved_array.append('Saved roi_crop_pre_im')
        except:
            error_array.append('Unable to save roi_crop_pre_im')

        try:
            save_var_im.append(self.roi_crop_post_im)
            counter_array.append(5)
            saved_array.append('Saved roi_crop_post_im')
        except:
            error_array.append('Unable to save roi_crop_post_im')

        try:
            save_var_im.append(self.chi_centroid)
            counter_array.append(6)
            saved_array.append('Saved chi_centroid')
        except:
            error_array.append('Unable to save chi_centroid')

        try:
            save_var_im.append(self.ttheta_centroid)
            counter_array.append(7)
            saved_array.append('Saved ttheta_centroid')
        except:
            error_array.append('Unable to save ttheta_centroid')


        for i,number in enumerate(counter_array):
            if (os.path.isfile(save_dic[number])) == True:
                error_array.append('Already Exsists: '+save_dic[number].split('/')[-1])
            else:
                pass
                imageio.imwrite(save_dic[number],np.asarray(save_var_im[i]).astype('uint32'))

        for line in saved_array:
            print(line)

        for line in error_array:
            print(line)


        #Returns the dimensions of the raw tif images
    def tif_dim(self):
        log.info('tif_dim BEGIN')
        search='start'
        maxx=self.max_x()-1
        maxy=self.max_y()-1
        loc_data=self.Location_Data()
        while search=='start':
            xran=random.randint(0,maxx)
            yran=random.randint(0,maxy)

            try:
                output=np.shape(imageio.imread(loc_data[0][yran][xran][0]))[0]
                search='y'
            except:
                pass
        log.info('tif_dim END')
        return output
    


    def chi_step1(self,scan_number_str,vmin=0,vmax=2):
       # """ Allows the User to determine the size of the CCD pixles

        #Variables--
	
        #scan_number: (string)
                #- the folder name in a string format of the scan you have placed in the zDetector folder
        #vmin: (number)
               # - Allows the User to adjust the min contrast value.
        #vmax: (number)
                #- Allows the User to adjust the max contrast value.

        #Returns--

        #Shape of the images
       #"""

        if isinstance(scan_number_str,int):
            scan_number_str=str(scan_number_str)

        folderlocation=self.detector
        foldername=scan_number_str
        self.scan_number_str=scan_number_str
        x=foldername
        a=0                                                               # Arbitrary variable of 0 for a starting value for my forloop
        arr = [[] for _ in range(1)]                                      # Blank matrix for my forloop

        for b in range(0,len(x)):                                         # loop that grabs all the file names in each folder selected by the user


                                                   # Getting all the filenames from one of the folders. Fun in a loop to get all the file names the user wants.
            for dirpath,dirnames,filenames in walk(folderlocation+x):

                a=a+1                                                     # step to the next value in X

                arr[0].append(sorted(filenames))                          # append the filenames variable with the all the filenames in the folders

        c=sorted(arr)                                                     # Need to sort all the filenames
        modifiedlist=list(filter(None,c))                                 #Filter out all the blank cells in the list

        fig, axs = plt.subplots(4,4, figsize=(10, 10), facecolor='w', edgecolor='k')   # Trying to make a subplot for all the values
        fig.subplots_adjust(hspace = .25, wspace=.11)                                   # Spacing betweent the plots

        axs = axs.ravel()                                                              # Not 100% sure. Got this code offline
        k=np.shape(modifiedlist)                                                       # Need to know how many subplots to make

        for i in tqdm(range(k[2])):


            im = Image.open(folderlocation+foldername+'/'+modifiedlist[0][0][i])

                                                #This allows me to get the picture into an array
            imarray=np.array(im) 

            axs[i].imshow(imarray, cmap='plasma',vmin=vmin, vmax=vmax)      # Plot my image arrays (CHANGE THESE VALUES IF IT ISN'T WORKING)
            axs[i].set_title(str(modifiedlist[0][0][i]))                      # Gives the plot a title


        return np.shape(im)


    def chi_step2(self,Index_of_First_Image,Index_of_Second_Image,first_vert='',second_vert='',vmin=0,vmax=3): #Plots the detector movement scans larger so the User can pick spots to determine the distance
        """ Allows the User to determine the size of the CCD pixles step 2

        Variables--
	
        Index_of_First: (number)
                - select the first scan which you would like to use from the chi_step1 function. Values are from 1 to the end of the images shown
        Index_of_Second: (number)
                - select the last scan which you would like to use from the chi_step1 function. Values are from 1 to the end of the images shown
        first_vert: (number)
                - select a point on the first image displayed and try to get the vertical line to line up with it. (x value for vertical line)
        second_vert: (number)
                - select a point on the second image displayed that is the same as the first image point you selected and try to get the vertical line to line up with it. (x value for vertical line)
        vmin: (number)
                - Allows the User to adjust the min contrast value.
        vmax: (number)
                - Allows the User to adjust the max contrast value.

        Returns--

        Shape of the images, detector left, and detector right values

        """
        folderlocation=self.detector
        foldername=[self.scan_number_str]



        orderedfilenames=self.orderedfilenames_detector(folder=foldername[0])


        im1=imageio.imread(folderlocation+foldername[0]+'/'+orderedfilenames[0][0][Index_of_First_Image-1]).astype('uint32')
        im2=imageio.imread(folderlocation+foldername[0]+'/'+orderedfilenames[0][0][Index_of_Second_Image-1]).astype('uint32')

        fig=plt.figure()
        gridspec.GridSpec(40,40)
        # large subplot
        plt.subplot2grid((20,40), (0,0), colspan=20, rowspan=20)
        plt.locator_params(axis='x', nbins=5)
        plt.locator_params(axis='y', nbins=5)
        plt.title(orderedfilenames[0][0][Index_of_First_Image-1])
        plt.imshow(im1,'plasma',vmin=vmin,vmax=vmax)
        flat1=np.sum(im1,axis=0)
        flat1=Wills_Median_Blur(flat1,5,25)
        flat1_1=np.where(flat1==np.max(flat1))[0][0]
        if first_vert=='':
            plt.axvline(x=flat1_1)
            self.detectorlineleft=flat1_1
        else:
            plt.axvline(x=first_vert)
            self.detectorlineleft=first_vert

        # small subplot 1
        plt.subplot2grid((20,40), (0,20),colspan=20,rowspan=20)
        plt.locator_params(axis='x', nbins=5)
        plt.locator_params(axis='y', nbins=5)
        plt.title(orderedfilenames[0][0][Index_of_Second_Image-1])
        flat2=np.sum(im2,axis=0)
        flat2=Wills_Median_Blur(flat2,5,25)
        flat2_1=np.where(flat2==np.max(flat2))[0][0]
        
        if second_vert=='':
            plt.axvline(x=flat2_1)
            self.detectorlineright=flat2_1

        else:
            plt.axvline(x=second_vert)
            self.detectorlineright=second_vert

        plt.imshow(im2,'plasma',vmin=vmin,vmax=vmax)

        fig.tight_layout()
        fig.set_size_inches(w=12,h=8)


        return np.shape(im1), self.detectorlineleft, self.detectorlineright

    def chi_step3(self,Size_of_Pixles_in_um,Total_Angle_in_Degrees):

        """ Allows the User to determine the size of the CCD pixles step 3. Determining the Chi bounds

	Variables--
	
        Size_of_Pixles_in_um: (number)
            - A number value of the size of your pixles in the CCD. Make sure your units are in um.
        Total_Angle_in_Degrees: (number)
            - Based on the images you selected for the chi_step2. This value is set to the angle difference between those two images.

	Returns--

        Chi Bounds

        """

        HighValue=self.detectorlineleft
        LowValue=self.detectorlineright

        Length=((abs(HighValue-LowValue))*Size_of_Pixles_in_um)                 #Finds the distance between the two points the user selected. Multiplies by the pixel size to get the physical distance in      														micrometers
        AngleRadians=math.radians(Total_Angle_in_Degrees)                  #Need to convert the degrees of the angle provided by the user to radians so python can do math correctly
        r=((Length)/tan(AngleRadians))/1000                                #Use some trig to determine the actual distance from the sample to detector in centimeters

        Chi=math.degrees(math.atan((((((self.tif_dim())/2)*Size_of_Pixles_in_um)/1000))/r))   #Use some more math to find right bound of my angle given all of the parameters above
        
        self.chi_value=Chi
        self.r_mm=r
        self.size_of_pixles=Size_of_Pixles_in_um
        
        print('Your Upper/Lower Bound For Chi is: '+str(Chi))

        return Chi



    def beam_size_in_pixles(self,D_um,d_rN_nm,Starting_Angle_of_Detector,Kev):
		
        Chi=self.chi_value
        r_mm=self.r_mm
        Pixle_Width_um=self.size_of_pixles


        D_nm=D_um*1000
        r_nm=r_mm*1000000
        r_um=r_mm*1000
        pixle_width_nm=Pixle_Width_um*1000

        half_zone_plate_nm=D_nm/2
        (L,R,wavelength_nm)=d_spacing_angstroms(Starting_Angle_of_Detector,Chi,Kev)

        f_nm=(D_nm*d_rN_nm)/wavelength_nm

        fraction=(half_zone_plate_nm/f_nm)
        len_in_pix=r_um/Pixle_Width_um
        
        beam_rad_pix=(half_zone_plate_nm/f_nm)*len_in_pix
        self.beam_size_in_pixles_val=beam_rad_pix
        
        print('The Instrumental Broadening Of Your Beam Is: '+str(beam_rad_pix)+' pixles. It has now been stored as self.beam_size_in_pixles_val')
        
        return beam_rad_pix



    def Chi_TTheta_Maps(self,
                        detector_angle,
                        Chi,
                        sub_fov,
                        save='n',
                        ttheta_low=1,
                        ttheta_high='',
                        chi_up=1,
                        chi_down='',
                        stdev_min=35,
                        summed_ims_vmin='',
                        summed_ims_vmax='',
                        max_divide=2,
                        multiplier=1,
                        ims_2_ave=2,
                        med_blur_dist=4,
                        med_blur_hei=10,
                        background_val_set=0,
                        allchi='n',
                        rgb_ttheta_bounds='',
                        rgb_chi_bounds='',
                        troubleshooting='',
			video_image_right='roi'
                        

                       ):

        """ Allows the User to make Chi and 2Theta Maps as well as save all the data.

	Variables--

	detector_angle: (number)
		- This is the starting detector angle. Input this value as a number

	Chi: (number)
		- This value should be automatically calculated by chi_step3. Use that output for this variable. It is the upper bounds of chi for the Users data set.

	sub_fov: (number)
		- If the User has cropped their data with the Roi_Crop function they can set a different sub_fov value so when they save data it doesn't over write previously saved data.

	save: (string w/ values of 'y' or 'n')
		- Set this value to equal 'y' if you want to save your data. Otherwise it will just output some of the final results to your desktop.

	ttheta_low: (number)
		- The lowest values in pixles range is from 1 to length of the summed array image

	ttheta_high: (number)
		- The highest values in pixles range is from 1 to length of the summed array image (must be larger than ttheta_low)
	chi_up: (number)
		- The upper values in pixles range is from 1 to length of the summed array image
	chi_down: (number)
		- The lower values in pixles range is from 1 to length of the summed array image (must be larger than chi_up)
        stdev_min: (number)
                - Allows the user to change the standard deviation cut off value
        summed_ims_vmin: (number)
                - Sets the vmin value for the summed array
        summed_ims_vmax: (number)
                - Sets the vmax value for the summed array
        max_divide: (number)
                - When selecting which values to choose from on the 1D arrays it takes everything above the max divided by this number.
       
        med_blur_dist,med_blur_hei,background_val_set: DO NOT TOUCH any of these 
 
        allchi: (string w/values of 'y' or 'n')
               - Change this value to 'y' if you want the program to output all the twotheta plots for all the chi values

        rgb_ttheta_bounds,rgb_chi_bounds  (Work in Progress DO NOT TOUCH)

        troubleshooting: array w/ numbers
               - This is a number array in the format [number,number] which allows the user to only run one line of the image rather than the whole thing to get certain setting right
	                    
        Return--

        rbg image of chi and two theta arrays (This is a work in progress. Should not be used for anything)
        """
        log.info('Chi_TTheta_Maps BEGIN')
        if save=='y' and video_image_right=='roi' and troubleshooting=='':
            use_new_roi = input('The default roi has been selected. Do you want to use self.roi_master instead? y/n ')
            if use_new_roi == 'y':
                try:
                    video_image_right=self.roi_master
                except:
                    warnings.warn('Program Determined self.roi_master Is Not Valid. Default ROI Is Being Used.')
                    video_image_right = 'roi'

        if rgb_ttheta_bounds!='' or rgb_chi_bounds!='':
            if len(rgb_ttheta_bounds)!=len(rgb_chi_bounds):
                good_to_go='n'
            else:
                good_to_go='y'
        elif rgb_ttheta_bounds=='' or rgb_chi_bounds=='':
            good_to_go='n'

        if ttheta_high=='':
            ttheta_high=self.tif_dim()
        elif ttheta_high!='':
            ttheta_high=ttheta_high

        if chi_down=='':
            chi_down=self.tif_dim()
        elif chi_down!='':
            chi_down=chi_down



        print('Chi & 2Theta Maps')
        time.sleep(0.5)
        What_Axis=CHIor2THETA('chi')

        print('Chi Background Image Creation')
        time.sleep(0.5)
        Background_Images=self.background_chi(ims_2_ave,multiplier,med_blur_dist,med_blur_hei).copy()



        print('2Theta Background Image Creation')
        time.sleep(0.5)
        Background_Images2=self.background_2theta(ims_2_ave,multiplier,med_blur_dist,med_blur_hei).copy()
        tif_dim=self.tif_dim()

        ran=range(0,tif_dim)


        TwoThetaLeft=detector_angle-Chi
        TwoThetaRight=detector_angle+Chi

        line2=np.linspace(TwoThetaLeft,TwoThetaRight,tif_dim)
        line1=np.linspace(-Chi,Chi,tif_dim)


        empty_list=self.location_data_crop()
                #Get the folder where we are going to store the 2theta figures from the MAPS in
            #self.ims_2theta='/home/will/Desktop/Current_V2/'+folderval+'IMS_2theta/'+self.fov[0]+'/'

                #Get the folder where we are going to store the chi figures from the MAPS in 
            #self.ims_chi='/home/will/Desktop/Current_V2/'+folderval+'IMS_chi/'+self.fov[0]+'/'

        z=np.poly1d(np.polyfit(ran,line2,1))
        q=np.poly1d(np.polyfit(ran,line1,1))
        time.sleep(0.5)

        #Creating figures for the saved images
        print('Creating Maps...')
        fig1,ax1 = plt.subplots(1)
        fig2,ax2 = plt.subplots(1)
        fig3,ax3 = plt.subplots(1)

        #This is used for if a single particle has multiple domains
        for its in range(0,1):

            if its==0:
                TopLimit=chi_up
                BottomLimit=chi_down

                #Made it easy to come back in and add iterations to this if one wants to do multiple crops in one go

            xvals=ran

                        #Using the width I can determine the values for my x axis
            maxarr=np.asarray(max(self.shapeMAT('roi')))
                                             #Taking the larges image shape I can determine how many iterations I will continue for
            Centroid=[[0 for x in range(maxarr[1])] for y in range(maxarr[0])]
            Centroid_Two=[[0 for x in range(maxarr[1])] for y in range(maxarr[0])]
            Centroid_Three=[[0 for x in range(maxarr[1])] for y in range(maxarr[0])]
            counter=0



            if troubleshooting=='':
                troubleshooting_range=range(0,maxarr[0])
            else:
                troubleshooting_range=range(troubleshooting[0],troubleshooting[1])
            for k in tqdm(troubleshooting_range):
                #For the Height of my image I will do - 
                for j in range(0,maxarr[1]):
                                                #For the Width of my image I will do-    
                    Chi_Data=[[0 for x in range(tif_dim)] for y in range(tif_dim)]
                    Image_Data=[]
                                   #Create a Blank Array for my Chi Data for one location on array            

                    for i in range(0,len(empty_list)):


            #SECTION 1: Grab the image file, subtract the background, sum across the chi axis, store the data
                        try:
                            initial_read=imageio.imread(empty_list[i][k][j][0]).astype('uint32') #Read the first location from all the folders
                            sum_the_axis=np.sum(initial_read,axis=What_Axis)

                            testtesttest=Wills_Median_Blur(sum_the_axis.copy(),med_blur_dist,med_blur_hei)

                            background_subtraction=np.subtract(testtesttest,Background_Images[i]).astype('int32')
                            background_subtraction[background_subtraction<0]=math.ceil(np.mean(background_subtraction))
                            background_subtraction[0:chi_up]=0
                            background_subtraction[chi_down:tif_dim]=0
                            Chi_Data.append(background_subtraction)
                            Image_Data.append(initial_read)

                        except:                                                                     #If it can't load an image then do nothing
                            pass




                    Tot_I=np.sum(Chi_Data,axis=0)
                    Image_Data_Sum=np.sum(Image_Data,axis=0)


                    if good_to_go=='y':
                        Centroid_Three[k][j]=np.sum(Image_Data_Sum[chi_up:chi_down,ttheta_low:ttheta_high])
                        

                    outname1='CHI_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov)+'__'+str(k).zfill(2)+'_'+str(j).zfill(2)+'__'
                    outname=outname1+'.png'
                    outname2='2Theta_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov)+'__'+str(k).zfill(2)+'_'+str(j).zfill(2)+'__'
                    outname2=outname2+'.png'
                    outname3_1='Summed_Dif_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov)+'__'+str(k).zfill(2)+'_'+str(j).zfill(2)+'__'
                    outname3=outname3_1+'.png'


                    if save=='y':


                        #Location for the new axis
                        newax = fig1.add_axes([0.6,0.15,0.7, 0.7])
                        if video_image_right=='roi':
                            try:
                                newax.imshow(self.roi_crop_post_im,vmin=self.roivmin,vmax=self.roivmax)
                            except:
                                newax.imshow(self.roi_crop_pre_im,vmin=self.roivmin,vmax=self.roivmax)

                        elif video_image_right!='roi':
                            newax.imshow(video_image_right)
                           
            
                        circ = Circle((j,k),0.5,color='r')
                        newax.add_patch(circ)
                        newax.axis('off')
                        plt.suptitle(outname3)
                        try:
                            if summed_ims_vmin==''and summed_ims_vmax=='':
                                ax1.imshow(Image_Data_Sum,vmin=np.min(Image_Data_Sum),vmax=np.max(Image_Data_Sum),extent=(TwoThetaLeft,TwoThetaRight,Chi,-Chi))
                            elif summed_ims_vmin!='' and summed_ims_vmax=='':
                                ax1.imshow(Image_Data_Sum,vmin=summed_ims_vmin,vmax=np.max(Image_Data_Sum),extent=(TwoThetaLeft,TwoThetaRight,Chi,-Chi))
                            elif summed_ims_vmin=='' and summed_ims_vmax!='':
                                ax1.imshow(Image_Data_Sum,vmin=np.min(Image_Data_Sum),vmax=summed_ims_vmax,extent=(TwoThetaLeft,TwoThetaRight,Chi,-Chi))
                            elif summed_ims_vmin!='' and summed_ims_vmax!='':
                                ax1.imshow(Image_Data_Sum,vmin=summed_ims_vmin,vmax=summed_ims_vmax,extent=(TwoThetaLeft,TwoThetaRight,Chi,-Chi))
                            else:
                                warnings.warn('Vmin and Vmax for the Summed Diffraction Image') 

                            
                            ax1.set_xlabel('Sum-Dif-Min: '+str(round(np.min(Image_Data_Sum),2))+'  Sum-Dif_Max: '+str(round(np.max(Image_Data_Sum),2)))
                            fig1.savefig(self.ims_summeddif+outname3,bbox_inches='tight')
                            ax1.cla()
                            newax.cla()
 
                        except:
                            log.warning('The Program Has Determined There Are Missing Values In The ROI Array. This Means You Cannot Determine The Summed Dif Pattern at '+self.ims_summeddif+outname3)
                        

                    if save == 'y':
                        ax2.set_title(outname1)
                        fig2.tight_layout()
                        ax2.plot(line1,Tot_I)
                        if troubleshooting!='':
                            log.info('St.Dev of '+self.ims_summeddif+outname3+' is: '+str(round(np.std(Tot_I),1))+'Sum-Dif-Min: '+str(round(np.min(Image_Data_Sum),2))+'  Sum-Dif_Max: '+str(round(np.max(Image_Data_Sum),2)))






                    if np.std(Tot_I)<stdev_min:                  #If the standard deviation between points is too small it is probably background signal
                            Tot_I[Tot_I <= np.max(Tot_I) ] = 0               
                    else:
                                                                                                    #If standard deviation is high enough anything higher than 6 times the standard deviation is probably a hot pixle 
                        #Tot_I[Tot_I <= np.max(Tot_I)/max_divide ] = 0                               #Make hot pixles zero
                        Tot_I[Tot_I <= np.mean(Tot_I)+np.std(Tot_I) ] = 0
                        if np.std(Tot_I)<stdev_min:              #If the data without the hot pixle has a low standard deviation it is probable just background signal
                            Tot_I[Tot_I <= np.max(Tot_I) ] = background_val_set                                      #Make all values zero (make it a background value)
                    teststd=np.std(Tot_I)   
                    centroid=np.sum(xvals*Tot_I)/np.sum(Tot_I)
                    if np.isnan((np.amax(centroid)))==True:
                            centroid=background_val_set

                    if save=='y':
                        ax2.plot(line1,Tot_I)
                        ax2.axvline(q(centroid),color='r')
                        ax2.set_xlabel('St.Dev: '+str(round(np.std(Tot_I),1)))
                        fig2.savefig(self.ims_chi+outname)
                        ax2.cla()

                  ############################################################

                    if allchi=='n':
                        dochi=centroid>0
                    elif allchi=='y':
                        dochi=True


  
                    if dochi==True:
                        What_Axis2=CHIor2THETA('2theta')

                        counter_2=0
                        Chi_Data2=[]
                        Image_Data2=[]
                        for p in range(0,len(empty_list)):
                            try:
                                initial_read2=imageio.imread(empty_list[p][k][j][0]).astype('uint32') #Read the first location from all the folders
                                sum_the_axis2=np.sum(initial_read2,axis=What_Axis2)

                                testtesttest2=Wills_Median_Blur(sum_the_axis2.copy(),med_blur_dist,med_blur_hei)

                                background_subtraction2=np.subtract(testtesttest2,Background_Images2[p]).astype('int32')
                                background_subtraction2[background_subtraction2<0]=math.ceil(np.mean(background_subtraction2))
                                background_subtraction2[0:ttheta_low]=0
                                background_subtraction2[ttheta_high:tif_dim]=0
                                Chi_Data2.append(background_subtraction2)

                                Image_Data2.append(initial_read2)
                            except:
                                pass

                        Tot_I2=np.sum(Chi_Data2,axis=0)
                        if save=='y':
                            ax3.plot(line2,Tot_I2)


                        if np.std(Tot_I2)<stdev_min:
                            Tot_I2[Tot_I2 <= np.nanmax(Tot_I2) ] = 0
                        else:
                            Tot_I2[Tot_I2 <= np.mean(Tot_I2)+np.std(Tot_I2) ] = 0
                            if np.std(Tot_I2)<stdev_min:
                                Tot_I2[Tot_I2 <= np.nanmax(Tot_I2) ] = background_val_set
                        teststd2=np.std(Tot_I2)
                        centroid2=np.sum(xvals*Tot_I2)/np.sum(Tot_I2)
                        if np.isnan((np.amax(centroid2)))==True:
                            centroid2=background_val_set

                        if save=='y':

                            ax3.plot(line2,Tot_I2)
                            ax3.axvline(z(centroid2),color='r')
                            ax3.set_xlabel('St.Dev: '+str(round(np.std(Tot_I2),1)))
                            fig3.savefig(self.ims_2theta+outname2)
                            ax3.cla()


                            


                        Centroid_Two[k][j]=centroid2



                    Centroid[k][j]=centroid
        
        self.chi_ttheta_sub_fov = sub_fov
        self.chi_centroid=Centroid
        self.ttheta_centroid=Centroid_Two
        log.info('This is where the chi figures start to be made')
        fig=plt.figure()
        plt.imshow(Centroid,cmap='gnuplot')
        plt.title('CHI_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov))
        plt.colorbar()
        fig.savefig('/home/will/Desktop/Chi_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov)+'.png',bbox_inches='tight',dpi=300)
        if save=='y':
            print('Chi Figures Also Saved To Folders')
            fig.savefig(self.Imagespng+'Chi_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov)+'.png',bbox_inches='tight',dpi=300)
            fig.savefig(self.Imagespdf+'Chi_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov)+'.pdf',bbox_inches='tight',dpi=300)
            #fig.savefig(self.Imagespgf+'Chi_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov)+'.pgf',bbox_inches='tight',dpi=300)
            plt.close()
            ChiArray=np.asarray(Centroid)
            imageio.imwrite(self.Imagesraw+'Chi_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov)+'.tif',ChiArray)
        else:
            print('Chi Figures Only Saved To Desktop')
        log.info('This is where the chi figures end being made')
        fig=plt.figure()
        plt.imshow(Centroid_Two)
        plt.title('2Theta_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov))
        plt.colorbar()
        fig.savefig('/home/will/Desktop/2Theta_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov)+'.png',bbox_inches='tight',dpi=300)
        if save=='y':
            print('2Theta Figures Also Saved To Folders')
            fig.savefig(self.Imagespng+'2Theta_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov)+'.png',bbox_inches='tight',dpi=300)
            fig.savefig(self.Imagespdf+'2Theta_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov)+'.pdf',bbox_inches='tight',dpi=300)
            #fig.savefig(self.Imagespgf+'2Theta_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov)+'.pgf',bbox_inches='tight',dpi=300)
            plt.close()
            tThetaArray=np.asarray(Centroid_Two)
            imageio.imwrite(self.Imagesraw+'2Theta_'+self.samplestate+'_'+self.fov[0]+'.'+str(sub_fov)+'.tif',tThetaArray)
        else:
            print('2Theta Figures Only Saved To Desktop')
        plt.close('all')
        log.info('Chi_TTheta_Maps END')
        return Centroid_Three


    def Mat_to_Tif(self,file_type,matlab_variable=['data2']):



        if file_type=='roi':
            folderlocation=self.roimat

            orderedfilenames=self.orderedfilenames_MAT('roi')

            outputfolder_location=self.roitif

        if file_type=='location':
            folderlocation=self.locationmat

            orderedfilenames=self.orderedfilenames_MAT('location')
            print(orderedfilenames)
            string_length=len(orderedfilenames[0][0][0])-4
            outputfolder_location=self.locationtif
            

        if file_type=='fluor':
            folderlocation=self.fluormat

            orderedfilenames=self.orderedfilenames_MAT('fluor')
            string_length=len(orderedfilenames[0][0][0])-4
            outputfolder_location=self.fluortif

        if file_type=='test':
            folderlocation=self.testmat

            orderedfilenames=self.orderedfilenames_MAT('test')
            string_length=len(orderedfilenames[0][0][0])-4
            outputfolder_location=self.testtif


        






        foldername=self.fov


        max_shape=Max_Shape_of_Matlab_files(folderlocation,foldername,orderedfilenames,matlab_variable)                   #Obtain the largest shape of the fluorescence image files
        All_Fluor_Ims=[]
        for i in range(0,len(orderedfilenames[0][0])):
            initial_data=scipy.io.loadmat(folderlocation+foldername[0]+'/'+orderedfilenames[0][0][i])[matlab_variable[0]] #Load the matlab files
            output_data=np.asarray(initial_data).astype('uint32')                                                         #Make Matlab data a uint32 numpy array
            output_data=Add_Columns(output_data,max_shape)                                                                #Adds Columns to the loaded array to match the largest shape value (I add the minimum value for the selected array)
            output_data=Add_Rows(output_data,max_shape)                                                                   #Adds Rows to the loaded array to match the largest shape value (I add the minimum value for the selected array)
            output_data=np.flip(output_data,0) #Need to flip the image because Matlab outputs in wierd orientation
            output_filename=outputfolder_location+'/'+orderedfilenames[0][0][i][0:string_length]+'.tif'                              #Make a new .tif file name
            imageio.imwrite(output_filename,output_data)                                                                  #Saves the image to the location specified by the user
            All_Fluor_Ims.append(output_data)
        #return All_Fluor_Ims

    def make_video(self,outimg=None, fps=23, size=None,
                   is_color=True, format="XVID"):
        """
        Create a video from a list of images.
     
        @param      outvid      output video
        @param      images      list of images to use in the video
        @param      fps         frame per second
        @param      size        size of each frame
        @param      is_color    color
        @param      format      see http://www.fourcc.org/codecs.php
        @return                 see http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
 
        The function relies on http://opencv-python-tutroals.readthedocs.org/en/latest/.
        By default, the video will have the size of the first image.
        It will resize every image to this size before adding them to the video.
        """

        image_folder=self.ims_summeddif
        output_folder=self.zExtra+self.fov[0]+'/video.mp4'
        images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
        images=sorted(images)
    
        from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize
        fourcc = VideoWriter_fourcc(*format)
        vid = None
        for image in images:
            image=image_folder+image
            if not os.path.exists(image):
                raise FileNotFoundError(image)
            img = imread(image)
            if vid is None:
                if size is None:
                    size = img.shape[1], img.shape[0]
                vid = VideoWriter(output_folder, fourcc, float(fps), size, is_color)
            if size[0] != img.shape[1] and size[1] != img.shape[0]:
                img = resize(img, size)
            vid.write(img)
        vid.release()
        return vid


    
        

    @property
    def locatonmat(self):
        return self.locationmat

def AllBackgroundImageCreation_New(folderlocation,foldernames,orderedfilenames,imagestoaverage,multiplier,axi,med_blur_number,med_blur_high):

    
    x=imagestoaverage                               #Too lazy to rewrite code. This just changes the variable name
    endlocation=len(orderedfilenames[0][0])-1       #Get the end location of the orderedfilenames of the first file
    ims=[]                                          #Create an empty array for me to append things to
    mean_ims=[]                                     #Create another empty array for me to append my means to
    total_mean_ims=[]
    for j in tqdm(range(0,len(foldernames))):
        ims=[]                                          #Create an empty array for me to append things to
        mean_ims=[]
        for i in range(0,x):
    
            im1t=imageio.imread(folderlocation+foldernames[0]+'/'+orderedfilenames[0][0][i]).astype('uint32')
            im1t2=np.sum(im1t,axis=axi)
            im1=Wills_Median_Blur(im1t2,med_blur_number,med_blur_high)
            ims.append(im1)                             #Import image from the beginning then append file to empty array
   
            im2t=imageio.imread(folderlocation+foldernames[0]+'/'+orderedfilenames[0][0][endlocation-i]).astype('uint32')
            im2t2=np.sum(im2t,axis=axi)
            im2=Wills_Median_Blur(im2t2,med_blur_number,med_blur_high)
            ims.append(im2)                             #Import image from the end then append file to the array
    
            mean_ims=np.mean(ims,axis=0).astype('uint32')   #Averaging the array we just created
            
        total_mean_ims.append(mean_ims)
    
    return (np.asarray(total_mean_ims)*multiplier).astype('uint32')           
    
    
    

def Add_Columns(array_you_want_to_change,max_shape):

    initial_shape=np.shape(array_you_want_to_change)                     #Grabs the shape of the array you give it
    how_many_its=(np.subtract(max_shape,initial_shape))[1]               #Subtracts your shape from the max array shape caluclated above. This is how many times I want to code to run
    
    for i in range(0,how_many_its):
        addcol=[[np.amin(array_you_want_to_change) for x in range(1)] for y in range(max_shape[0])]   #An array that has 1 width and max height filled with the lowest value of the loaded array
        array_you_want_to_change = np.hstack((array_you_want_to_change, addcol))                      #Concatonates the loaded array and the column array essentially adding a column to the data given to the function
    return array_you_want_to_change

#Adds Rows to Images That Have too Few Rows - Needs to Come AFTER Add_Columns Function

def Add_Rows(array_you_want_to_change,max_shape):
    #Does the exact same thing as the Add_Columns function but instead it adds rows
    #Add_Columns Function MUST Come BEFORE the Add_Rows Function in a Script
    initial_shape=np.shape(array_you_want_to_change)
    how_many_its=(np.subtract(max_shape,initial_shape))[0]
    
    for i in range(0,how_many_its):
        addrow=[[np.amin(array_you_want_to_change) for x in range(max_shape[1])] for y in range(1)]
        array_you_want_to_change = np.vstack((array_you_want_to_change, addrow))
    return array_you_want_to_change        

def CHIor2THETA(input1):                                                                   #I didn't want to keep remembering which axis value corresponds to chi or 2theta so I created this to remember for me
    if input1 == 'chi':
        output=1
    if input1 == '2theta':
        output=0
    if input1 != 'chi' and input1 != '2theta':
        print('ERROR! ERROR! ERROR!')
    return output

def Wills_Median_Blur(input_array,median_blur_distance,cut_off_value_above_mean):       #Created my own median blur for the data 
    iteration_number=np.shape(input_array)[0]                                           #Finds out the length of the array you want to median blur. This equals the number of iterations you will perform
    median_array=[]                                                                     #Create a blank array for the final output
    for j in range(0,iteration_number):
        median_array=[]
        if j-median_blur_distance<0:                                                    #Corrects bounds if the program is out of bounds
            its_blur=range(0,j+median_blur_distance+1)
        if j+median_blur_distance>iteration_number:
            its_blur=range(j-median_blur_distance,iteration_number)
        if j-median_blur_distance>=0 and j+median_blur_distance<=iteration_number:
            its_blur=range(j-median_blur_distance,j+median_blur_distance+1)

        for i in its_blur:                                                              #Takes the indicies for one iteration and gets the values of these locations from the users array
            try:
                median_array.append(input_array[i])       
            except:
                pass
        if input_array[j]>np.median(median_array)+cut_off_value_above_mean:              #Replace a high value with the median value
            input_array[j]=np.median(median_array)
        else:
            pass
        
    return input_array

def Wills_Median_Blur_With_Low(input_array,median_blur_distance,cut_off_value_above_mean):       #Created my own median blur for the data 
    iteration_number=np.shape(input_array)[0]                                           #Finds out the length of the array you want to median blur. This equals the number of iterations you will perform
    median_array=[]                                                                     #Create a blank array for the final output
    for j in range(0,iteration_number):
        median_array=[]
        if j-median_blur_distance<0:                                                    #Corrects bounds if the program is out of bounds
            its_blur=range(0,j+median_blur_distance+1)
        if j+median_blur_distance>iteration_number:
            its_blur=range(j-median_blur_distance,iteration_number)
        if j-median_blur_distance>=0 and j+median_blur_distance<=iteration_number:
            its_blur=range(j-median_blur_distance,j+median_blur_distance+1)

        for i in its_blur:                                                              #Takes the indicies for one iteration and gets the values of these locations from the users array
            try:
                median_array.append(input_array[i])       
            except:
                pass
        if input_array[j]>np.median(median_array)+cut_off_value_above_mean:              #Replace a high value with the median value
            input_array[j]=np.median(median_array)
            #print(j,np.median(median_array),'high')
        elif input_array[j]<np.median(median_array)-cut_off_value_above_mean:
            input_array[j]=np.median(median_array)
            #print(j,np.median(median_array),'low')
        else:
            pass
        
    return input_array


def Max_Shape_of_Matlab_files(folderlocation,foldername,orderedfilenames,matlab_variable):
    shape=[]                                                                                #Empty array to store information
    for i in range(0,len(orderedfilenames[0][0])):
            initial_data=scipy.io.loadmat(folderlocation+foldername[0]+'/'+orderedfilenames[0][0][i])[matlab_variable[0]]  #Opens up a matlab
            output_data=np.asarray(initial_data).astype('uint32')                           #Converts that file into numpy array uint32
            shape.append(np.shape(output_data))                                             #Stores shape of the file into an array
    return max(shape)    

def d_spacing_angstroms(Initial_Theta,Chi,Kev):

    plancks_constant=(6.62607004*10**-34)/(1.60217662*10**-19)
    speed_of_light=299792458
    hc=(plancks_constant)*(speed_of_light)*10**9
    wavelength_in_nm=hc/(Kev*1000)
    LeftTheta=(Initial_Theta-Chi)/2   #divide by two because the thetas are 2theta and I need theta
    RightTheta=(Initial_Theta+Chi)/2
    Left_Theta_Radians=math.radians(LeftTheta)
    Right_Theta_Radians=math.radians(RightTheta)
    Left_d_Spacing=(wavelength_in_nm/(2*(math.sin(Left_Theta_Radians))))*10
    Right_d_Spacing=(wavelength_in_nm/(2*(math.sin(Right_Theta_Radians))))*10

    return Left_d_Spacing,Right_d_Spacing,wavelength_in_nm

def SXDM_folder_management(folder_path='',sample_number='',beamline_data='Beam_Line_Data^',wip='WIP^'):
    """
    Creates a Universal folder system for the users making data analysis and saving much easier.

    After you make the folder management system you will notice some folders have an ^ by them.
    These folder names you are free to change to whatever you want. Everything else should stay the same.
    The User can change any of the other ones, but would also have to change sections of the SXDM code to
    Compenstate.

    Variables-- 

    folder_path: (str)
                - this is a string to path where you want to make you folder system. 

    sample_number: (int)
                - this is an integer of how many sample you have to analyze. Different FOV's, but for the same sample do not count as different samples. FOV's are handeled seperatley. 

    beamline_data: (str)
                - this is a string to the path of your beamline data for this sample. If you have kept the filenames as stock filenames then there is no need to change this default value.

    wip: (str)
                - this is a strong to the path of your wip data for this sample. If you have kept the filenames as stock filenames then there is no need to change this degault value. 
    
    
    
    """
    if folder_path=='' or sample_number=='':
        print('folder_path or sample_number missing.\nExample: folder_path_path='"'/home/will/Desktop/'"'\nExample: sample_number=3 ')
    else:
        folder_path1=folder_path+beamline_data+'/'
        directory1 = os.path.dirname(folder_path1)
        folder_path2=folder_path+wip+'/'
        directory2 = os.path.dirname(folder_path2)
        atuple=()
        if not os.path.exists(directory1):
            for i in range(0,sample_number):
                sample=str(i+1)+'-Sample'
                os.makedirs(directory1+'/SXDM/APS_Filename^/'+sample)
                os.makedirs(directory1+'/SXDM/APS_Filename^/'+sample+'/MDA/')
                atuple=atuple+(directory2+'/'+sample+'/',)
            os.makedirs(directory1+'/SXDM/APS_Filename^/zDetector/Images/')
            


        if not os.path.exists(directory2):
            os.makedirs(directory2)

        atuple2 = ('1-LocationMat/FOV1/', '2-ROIMat/FOV1/', '3-FluorMat/FOV1/', '4-TestMat/FOV1/',
                   '5-LocationTif/FOV1/', '6-ROITif/FOV1/', '7-FluorTif/FOV1/', '8-TestTif/FOV1/',
                   'Images/PDF/','Images/PNG/','Images/PGF/','Images/RAW/','IMS_2theta/FOV1/', 'IMS_chi/FOV1/','IMS_summeddif/FOV1/',
                   'zExtra/FOV1/','zRaw_Images/FOV1/')


        for dir1 in atuple:
            for dir2 in atuple2:
                os.makedirs(os.path.join(dir1, dir2))
        #return (directory1+'/SXDM/APS_Filename^/',directory2+'/')
             



def Mat_to_Tif_Auto(self,matlab_variable=['data2']):

    for its in range(0,3):
        if its==0:
            file_type='roi'
        elif its==1:
            file_type='location'
        elif its==2:
            file_type='fluor'

        if file_type=='roi':
            folderlocation=self.roimat

            orderedfilenames=self.orderedfilenames_MAT('roi')

            outputfolder_location=self.roitif

        if file_type=='location':
            folderlocation=self.locationmat

            orderedfilenames=self.orderedfilenames_MAT('location')

            outputfolder_location=self.locationtif
            

        if file_type=='fluor':
            folderlocation=self.fluormat

            orderedfilenames=self.orderedfilenames_MAT('fluor')

            outputfolder_location=self.fluortif


        string_length=len(orderedfilenames[0][0][0])-4
        foldername=self.fov
        max_shape=Max_Shape_of_Matlab_files(folderlocation,foldername,orderedfilenames,matlab_variable)                   #Obtain the largest shape of the fluorescence image files
        All_Fluor_Ims=[]
        for i in range(0,len(orderedfilenames[0][0])):
            initial_data=scipy.io.loadmat(folderlocation+foldername[0]+'/'+orderedfilenames[0][0][i])[matlab_variable[0]] #Load the matlab files
            output_data=np.asarray(initial_data).astype('uint32')                                                         #Make Matlab data a uint32 numpy array
            output_data=Add_Columns(output_data,max_shape)                                                                #Adds Columns to the loaded array to match the largest shape value (I add the minimum value for the selected array)
            output_data=Add_Rows(output_data,max_shape)                                                                   #Adds Rows to the loaded array to match the largest shape value (I add the minimum value for the selected array)
            output_data=np.flip(output_data,0) #Need to flip the image because Matlab outputs in wierd orientation
            output_filename=outputfolder_location+'/'+orderedfilenames[0][0][i][0:string_length]+'.tif'                              #Make a new .tif file name
            imageio.imwrite(output_filename,output_data)                                                                  #Saves the image to the location specified by the user
            All_Fluor_Ims.append(output_data)
        #return All_Fluor_Ims

def Matlab_Move(self,mat_or_tif):

    for iterations in range(0,3):
        
        
        if mat_or_tif=='mat':
            if iterations==0:
                start_dir=self.locationmat
                end_dir=self.locationmat+self.fov[0]+'/'
            if iterations==1:
                start_dir=self.roimat
                end_dir=self.roimat+self.fov[0]+'/'
            if iterations==2:
                start_dir=self.fluormat
                end_dir=self.fluormat+self.fov[0]+'/'    
        if mat_or_tif=='tif':
            if iterations==0:
                start_dir=self.locationtif
                end_dir=self.locationtif+self.fov[0]+'/'
            if iterations==1:
                start_dir=self.roitif
                end_dir=self.roitif+self.fov[0]+'/'
            if iterations==2:
                start_dir=self.fluortif
                end_dir=self.fluortif+self.fov[0]+'/'    
    
        test=next(os.walk(start_dir))[2]
        try:
            test2=os.listdir(end_dir)
        except:
            os.mkdir(end_dir) 
            test2=os.listdir(end_dir)
        if test2==[]:
            files_to_move=[]
            for i in range(0,len(test)):
                file = test[i]
                if any(x in file for x in self.scanlist):
                    files_to_move.append(file)
            files_to_move
            for file in files_to_move:
                shutil.move(start_dir+file,end_dir+file)
        else:
            warnings.warn('Files will be rewritten. Will not continue. Check .log file for the file locations.')
            log.info('Files will be rewritten. Will not continue. File System: \n'+end_dir+'\n')


