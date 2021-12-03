#Karaoke Sampler tools

http://htmlfiesta.com/xtreme/karaoke-sampler/

##Config
Edit settings in karaokesampler.py

KinectMode=True -> enables kinect mode or webcam mode
Vdevice = 1 -> check this if in webcam mode doesn't work play with values between 0 and 1

(In Windows) The recording audio device will be the system's default

#Requirements
Python 3.6
Recomended Conda 32 bits (there's a workaround for 64 bits in https://github.com/Kinect/PyKinect2/issues/37 )

##Requirements hardware
Kinect 2 with the proper PC adapter.
Even it's not 100% necessary for the audio part, some errors will show but continue to run.


##Requirements for Windows
Kinect for Windows Runtime 2.0 (drivers) (restart required)
https://www.microsoft.com/en-us/download/confirmation.aspx?id=44559
Kinect for Windows SDK 2.0
https://www.microsoft.com/en-us/download/confirmation.aspx?id=44561


##Songs
This software works with .kar files wich are like a matroska file for karaoke (.mid + .txt combined)
You can find them in some abandonware sites like http://www.vanbasco.com/

Create a folder named "scr/KARsongs/" and drop them there, the code will traverse subfolders inside that folder
