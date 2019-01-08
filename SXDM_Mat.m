function SXDM_Mat(beamline_sample_path)

loadmda_function_path='/path/to/loadmda_function'

%Default wip_sample_path
splits=strsplit(beamline_sample_path,'/');
len=length(splits);
ending=splits(len)
len_sub=len-4
beginning=splits(1:len_sub)
mid='WIP^'
str1=horzcat(beginning,mid)
str2=horzcat(str1,ending)
wip_sample_path=strjoin(str2,'/')


%1) Dont put forward slashes at the end of any of these variables.
%
%2) Make all the variables strings.
%
%3) Variable 1 is the loadmda_function_path. This is the path to all of your
%APS matlab functions. 
%Example: '/home/will/Desktop/Analysis'
%
%4) Variable 2 is the beamline_sample_path. This is the path to your sample
%folder inside the Beam_Line_Data* folder made by the SXDM_folder_managment
%script. 
%Example: '/home/will/Desktop/test/Beam_Line_Data*/SXDM/APS_Filename*/1-Sample'
%
%5) Variable 3 is wip_sample_path. This is the path to your sample folder
%inside the WIP* folder made by the SXDM_folder_managment script.
%Example: '/home/will/Desktop/test/WIP*/1-Sample'

clc
        %User Changeable Values

                        %add path for the showccd functions
%loadmda_function_path='/home/will/Desktop/Analysis-hi'; 

                        %add path for the beamline data associated with a particular sample
%beamline_sample_path='/home/will/Desktop/test/Beam_Line_Data*/SXDM/APS_Filename*/1-Sample';

                        %add path for the work in progress (WIP) folder associated with a particular sample
%wip_sample_path='/home/will/Desktop/test/WIP*/1-Sample';

        %Constant Values. DO NOT CHANGE
function_location=loadmda_function_path;
cd(beamline_sample_path)
images_location=strcat(beamline_sample_path,'/Images');
try
    movefile(strcat(beamline_sample_path,'/Link to Images'),images_location)  
end   

mda_location=strcat(beamline_sample_path,'/MDA');
sample_location=wip_sample_path;
old_path= path;
path(function_location,old_path);
old_path= path;
path(images_location,old_path);
old_path= path;
path(mda_location,old_path);
old_path= path;
path(sample_location,old_path);
global wills_i
global wills_j
%warning=input('CHANGE YOUR CURRENT FOLDER TO THE FOLDER WHERE YOU STORE THE IMAGES AND MDA FOLDER FOR THIS DATA. HIT CONTROL+C, CHANGE YOUR CURRENT FOLDER THEN RERUN\nTHE SCRIPT. hit ENTER to get past this section. \n');
%warning=input('Make sure you have set the loadmda_function_path, beamline_sample_path, and wip_sample_path in the script. Hit ENTER to continue.\n');  

close all

directory=dir(mda_location);
len=length(directory);
name_len_pre=size(directory(3).name);
name_len=name_len_pre(2)-4;

fluor='n';
fluor_num=input('Number of the Fluor you want to use: ');

while fluor == 'n'
    
filename=directory(3).name;
figure(1)
data=loadmda(filename,fluor_num); 
data2=data(:,:,1);
fluor=input('Is this the correct Fluor? (y/n)   ','s');
'\n';
if fluor=='n'
    close all
    fluor_num=input('Select a new Fluor Number: ');
end
  
if fluor=='y'
    close all
end

end

roi='n';
roi_num=input('\nNumber of the ROI you want to use: ');
'\n';

while roi == 'n'
    
filename=directory(3).name;
figure(1)
data=loadmda(filename,roi_num); 
data2=data(:,:,1);
roi=input('Is this the correct ROI? (y/n)   ','s');
if roi=='n'
    close all
    roi_num=input('Select a new ROI Number: ');
end
  
if roi=='y'
    close all
end

end




for its = 3:len
counter=0;
filename=directory(its).name;
figure(1)
data=loadmda(filename,fluor_num); 
data2=data(:,:,1);
if counter==0
    fprintf(strcat('\nClick on a center point for--',' ', filename));%, '--figure shown then hit ENTER when ready to move on'));
end
counter=1;
w = waitforbuttonpress;
if w == 0
    pause(1)
    close Figure 1001
%ready=input(strcat('\nChange your center point for--',' ', filename, '-- or hit ENTER when ready to move on'));

end
%jj=input('jj Value')
%ii=input('ii Value')

data=loadmda(filename,roi_num);
data2=data(:,:,1);
output_folder_location=(strcat(sample_location,'/2-ROIMat/'));
newfilename=[output_folder_location,filename(1:name_len),'.mat'];
save(newfilename,'data2');
%close all

data=loadmda(filename,fluor_num);
data2=data(:,:,1);
output_folder_location=(strcat(sample_location,'/3-FluorMat/'));
newfilename=[output_folder_location,filename(1:name_len),'.mat'];
save(newfilename,'data2');
%close all

data=loadmda(filename,fluor_num);
data2=data(:,:,1);
output_folder_location=(strcat(sample_location,'/1-LocationMat/'));
newfilename=[output_folder_location,filename(1:name_len),'.mat'];
data2(wills_i,wills_j)=1000000;


save(newfilename,'data2'); %actually saves the data. need to specify that we are saving the data2 variable we just made
%close all



end
close all
fprintf('\n\nTask Completed For One Sample')
