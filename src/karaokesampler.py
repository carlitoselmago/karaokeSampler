import aubio
import cv2
import math
import numpy as np
import pyaudio
#from synth import synth
from time import sleep
import wave
import struct
import audioop
import threading
from operator import itemgetter
import glob
import shutil
import os
import pygame
from pydub import AudioSegment
try:
	from pykinect2 import PyKinectV2
	from pykinect2.PyKinectV2 import *
	from pykinect2 import PyKinectRuntime
except:
	pass
import math
import PIL
from PIL import Image

class karaokesampler():

	#config
	KinectMode=True
	Vdevice = 1
	synth = False
	showScreenRecorder=False
	#end config
	windowName = "recorder"
	selectLimit=8 #number of audio samples to collect after recording

	recordingsFolder = "recordings/"
	samplersFolder="samplers/"

	lowCut = 0.0100#0.0174 #volumen
	lowToneCut=20 #pitch
	capW = 0
	capH = 0

	pitchGL=30
	pitchGH=80

	lastPitch = 0
	lastPitchConfidence = 0

	noteTargets=[] #the notes we are gonna try to record
	recordings=[]
	isrecording=False
	volume=5
	checkingVolume=False

	amountToAvergeVolume=2
	averageCounter=0
	lastVolumes=[]
	paint="none" #none,graph
	singing=False
	opencvReady=False

	graph = []

	#finished_threads=[]
	#event = threading.Event()

	def __init__(self):

		print("init karaokesampler")

		self.windowSize=[1920,1080]
		self.imgResizeSize=[800,450]

		self.pitch=0
		if not self.KinectMode:
			self.cap = cv2.VideoCapture(self.Vdevice)
		self.createNoteTargets()
		self.p = pyaudio.PyAudio()



		for i in range(self.amountToAvergeVolume+1):
			self.lastVolumes.append(0)



		t = threading.Thread(target=self.startVision, args = ("vision",))
		t.start()



	def createNoteTargets(self):
		#based on midi notes
		self.noteTargets=[48,53,60,65,72,77,84,89]

	def drawNoteTargets(self,img):
		for t in self.noteTargets:
			pitchH = int(self.remap(t, self.pitchGL, self.pitchGH, 0.0, self.capH))
			#print pitchH
			lineP1 = (500, pitchH)
			lineP2 = (700, pitchH)
			cv2.line(img,lineP1, lineP2, [40, 40, 120], 4)
		return img

	def remap(self, value, OldMin, OldMax, NewMin, NewMax):
		NewValue = (abs(abs(value - OldMin) * abs(NewMax - NewMin)) / abs(OldMax - OldMin)) + abs(NewMin)
		if NewValue < NewMin:
			#print("refine oldMin in remap")
			NewValue = 0.0
		if NewValue > NewMax:
			#print("refine oldMax in remap")
			NewValue = 1.0
		return NewValue

	def getAudioDevies(self):
		info = self.p.get_host_api_info_by_index(0)
		numdevices = info.get('deviceCount')
		for i in range(0, numdevices):
			#if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
			print ("Input Device id ", i, " - ", self.p.get_device_info_by_host_api_device_index(0, i).get('name'))

	def generateTone(self, FREQUENCY=500):
		BITRATE = 44100     #number of frames per second/frameset.

		#FREQUENCY = 500     #Hz, waves per second, 261.63=C4-note.
		LENGTH = 0.1   #seconds to play sound

		if FREQUENCY > BITRATE:
			BITRATE = FREQUENCY + 100

		NUMBEROFFRAMES = int(BITRATE * LENGTH)
		RESTFRAMES = NUMBEROFFRAMES % BITRATE
		WAVEDATA = ''

		#generating wawes
		for x in xrange(NUMBEROFFRAMES):
			WAVEDATA = WAVEDATA + chr(int(math.sin(x / ((BITRATE / FREQUENCY) / math.pi)) * 127 + 128))

		for x in xrange(RESTFRAMES):
			WAVEDATA = WAVEDATA + chr(128)
		return WAVEDATA

	def calculateVolume(self,CHUNK,audiobuffer):
		#if not self.checkingVolume:
		self.checkingVolume=True
		#for i in range(int(10*44100/buffer_size)): #go for a few seconds
		data = np.fromstring(audiobuffer, dtype=np.int16)
		peak = np.average(np.abs(data)) * 2
		volume = (50 * peak / 2 ** 16)
		volume = self.remap(volume, 12.0, 28.0, 0.0, 1.0)
		#self.volume=volume
		#print("checking volume")
		self.volume=volume
		#sleep(1)
		#self.checkingVolume=False
		self.checkingVolume=False


	def getJointPosition(self,joints, jointPoints, joint):
		joint0State = joints[joint].TrackingState;

		# both joints are not tracked
		if (joint0State == PyKinectV2.TrackingState_NotTracked):
			return

		# both joints are not *really* tracked
		if (joint0State == PyKinectV2.TrackingState_Inferred):
			return

		# ok, at least one is good
		try:
			position = (int(jointPoints[joint].x), int(jointPoints[joint].y))
			return position
		except:
			return False

	def midpoint(self,p1, p2):
		midpoint= (int((p1[0]+p2[0])/2), int((p1[1]+p2[1])/2))
		return midpoint

	def getdistance(self,p1,p2):
		dist = int(math.sqrt( (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 ))
		return dist

	def getFaceROI(self,index,frame, joints, jointPoints):


		ROI=False


		head=self.getJointPosition(joints, jointPoints, PyKinectV2.JointType_Head)
		neck=self.getJointPosition(joints, jointPoints, PyKinectV2.JointType_Neck)

		if neck and head:
			mouth=self.midpoint(head,neck)
			#radius=abs(int(head[0]-neck[0]))
			radius=self.getdistance(head,neck)
			radius=int(radius*1.6) #padding for the head

			screenProportion=[16,9]

			x=mouth[0]-radius
			y= mouth[1]-radius
			width=int(radius*2)
			height=int(radius*2)

			proportionalWidth=(height*screenProportion[0])/screenProportion[1]
			margin=(proportionalWidth-width)/2

			x=x-margin
			width=width+(margin*2)

			if x<2:
				x=1
			if y<2:
				y=1


			ROI=[x,y,width,height]

		if ROI:
			return ROI
		else:
			return []

	def getSubRegion(self,img,cordinates):
		img = img[int(cordinates[1]) :int(cordinates[1]) +  int(cordinates[3]) , int(cordinates[0]) : int(cordinates[0]) + int(cordinates[2])]

		return img

	def resizeImage(self,img,width,height):
		resized=cv2.resize(img,width,height, interpolation = cv2.INTER_CUBIC)
		return resized

	def startVision(self,name):
		if self.showScreenRecorder:
			cv2.namedWindow(self.windowName,cv2.WINDOW_NORMAL)
			cv2.resizeWindow(self.windowName,self.windowSize[0],self.windowSize[1])

		#print "START VISION THREAD!!"
		if self.KinectMode:
			w=1080#_kinect.depth_frame_desc.Width
			h=1920#_kinect.depth_frame_desc.Height
			shape=(w,h,4)
			_kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

			# back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
			img = pygame.Surface((_kinect.color_frame_desc.Width, _kinect.color_frame_desc.Height), 0, 32)
			_bodies=None
			sleep(2)
			bodyIndex=5

		else:
			self.capW = int(self.cap.get(3))
			self.capH = int(self.cap.get(4))

		while True:

			if self.KinectMode:
				if _kinect.has_new_color_frame():
					img=_kinect.get_last_color_frame()
					img=np.array(img,dtype=np.uint8).reshape(shape)
					self.cleanimage=img.copy()

				 #get skeletons
				if _kinect.has_new_body_frame():
					_bodies = _kinect.get_last_body_frame()

				#print skeletons
				if _bodies is not None:
					for i in range(0, _kinect.max_body_count):


						body = _bodies.bodies[i]
						if body.is_tracked:


							joints = body.joints
							# convert joint coordinates to color space
							joint_points = _kinect.body_joints_to_color_space(joints)
							#draw_body(frame,joints, joint_points, (255,255,255))

							faceROI=self.getFaceROI(i,img,joints, joint_points)

							if faceROI:

								img=self.getSubRegion(self.cleanimage,faceROI)#[faceROI,faceROI,faceROI,faceROI])

								#img=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


			else:
				#print "singing is true in vision"
				ret_val, img = self.cap.read()
				self.cleanimage=img.copy()

			if self.singing:


				if self.paint=="graph":
					img=self.drawNoteTargets(img)
					"""
					try:
						img=self.drawNoteTargets(img)
					except:
						print ("could not print note targets")
				   	"""

				volume=self.volume

				volH = int(self.remap(volume, 0.0, 0.2, 0.0, self.capH))

				#print (volH)
				lineV1 = (200, volH)
				lineV2 = (400, volH)
				if self.paint=="graph":
					try:
						cv2.line(img, lineV1, lineV2, [255, 0, 255], 2)
					except:
						print ("could not print volume line")


				if volume>self.lowCut:
					#   pitch
					pitch=self.pitch
					pitchH = int(self.remap(pitch, self.pitchGL, self.pitchGH, 0.0, self.capH))
					#print pitchH
					lineP1 = (500, pitchH)
					lineP2 = (700, pitchH)
					if self.paint=="graph":
						try:
							cv2.line(img, lineP1, lineP2, [255, 255, 255], 3)
						except:
							print ("could not print pitch line")
			self.img=img
			try:
				if self.showScreenRecorder:
					cv2.imshow(self.windowName, img)
			except:
				pass
			if cv2.waitKey(100) == 27:
				self.singing=False
				break  # esc to quit

			self.opencvReady=True

		self.opencvReady=False
		#self.cap.release()
		#cv2.destroyAllWindows()
		return ""


	def recordKaraoke(self):
		recFolder=self.recordingsFolder
		shutil.rmtree(recFolder)
		os.makedirs(recFolder)

		self.singing=True

		# open stream

		buffer_size = 1024
		CHUNK = buffer_size * 2
		pyaudio_format = pyaudio.paFloat32
		n_channels = 1
		samplerate = 44100
		stream = self.p.open(format=pyaudio_format,
							 channels=n_channels,
							 rate=samplerate,
							 input=True,
							 frames_per_buffer=buffer_size,
							 output=True)

		# Some constants for setting the PyAudio and the
		# Aubio.
		BUFFER_SIZE             = 2048
		CHANNELS                = 1
		FORMAT                  = pyaudio.paFloat32
		METHOD                  = "default"
		SAMPLE_RATE             = 44100
		HOP_SIZE                = BUFFER_SIZE//2
		PERIOD_SIZE_IN_FRAME    = HOP_SIZE

		 # setup pitch

		tolerance = 0.8
		win_s = 4096 # fft size
		hop_s = buffer_size # hop size
		pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
		pitch_o.set_unit("midi")
		pitch_o.set_tolerance(tolerance)

		print("*** starting recording")

		pitch = 0

		# Initiating PyAudio object.
		pA = pyaudio.PyAudio()
		# Open the microphone stream.
		mic = pA.open(format=FORMAT, channels=CHANNELS,
			rate=SAMPLE_RATE, input=True,
			frames_per_buffer=PERIOD_SIZE_IN_FRAME)

		# Initiating Aubio's pitch detection object.
		pDetection = aubio.pitch(METHOD, BUFFER_SIZE,
			HOP_SIZE, SAMPLE_RATE)
		# Set unit.
		pDetection.set_unit("Hz")
		# Frequency under -40 dB will considered
		# as a silence.
		pDetection.set_silence(-40)



		lastPitch=pitch

		while self.singing:

			#audio
			# Always listening to the microphone.
			data = mic.read(PERIOD_SIZE_IN_FRAME)
			# Convert into number that Aubio understand.
			signal = np.fromstring(data,
				dtype=aubio.float_type)
			# Finally get the pitch.
			#pitch = pDetection(samples)[0]
			pitch=pitch_o(signal)[0]
			self.pitch=pitch
			# Compute the energy (volume)
			# of the current frame.
			volume = float(np.sum(signal**2)/len(signal))


			# Format the volume output so it only
			# displays at most six numbers behind 0.
			volume=round(float("{:6f}".format(volume)),4)
			volume=self.remap(volume, 0.0,0.8, 0.0, 1.0)
			self.volume=volume

			confidence=1

			if self.opencvReady:

				if volume>self.lowCut and pitch>self.lowToneCut:

					#record if match
					if pitch>(lastPitch+1) or pitch<(lastPitch-1):
					#if pitch>(lastPitch+1) or pitch<(lastPitch-1):
						#pitch has changed create new audio clip
						if 'outputsink' in locals():
							outputsink.close()

						name=str(int(pitch))+"_"+str(len(self.recordings))
						self.recordings.append([name,0])
						filename = self.recordingsFolder + name
						outputsink = aubio.sink(filename+".wav", samplerate)
						#resize image
						if self.KinectMode:

							imgRes=cv2.resize(self.img,(self.imgResizeSize[0], self.imgResizeSize[1]))
						else:
							imgRes=self.img
						#imgRes=self.img.resize((self.imgResizeSize[0], self.imgResizeSize[1]), PIL.Image.ANTIALIAS)
						cv2.imwrite(filename+".jpg",imgRes)
					else:
						#same pitch, recording
						self.recordings[-1][1]+=1
						#pitch is the same, keep recording
						outputsink(signal, len(signal))

					lastPitch=pitch


			#self.S.out()
			self.lastPitch = 0
			self.lastPitchConfidence = 0

			#if pitch > 0:
			#    stream.write(self.generateTone(pitch))

		try:
			outputsink.close()
		except:
			pass
		print("*** done recording")
		#print (self.recordings)
		#stream.stop_stream()
		#stream.close()
		self.p.terminate()
		self.processRecordings(self.recordings)
		"""
		try:
			self.processRecordings(self.recordings)
		except:
			print ("could not process recordings")
		"""
		return

	def deleteAllshorterNotes(self,selectedRecodingNote):

		selectedNote=selectedRecodingNote.split("_")[0]

		for i,rec in enumerate(self.recordings):
			recordingName=rec[0]
			note=recordingName.split("_")[0]
			if note==selectedNote and recordingName!=selectedNote:
				#delete note
				print ("delete note index ",i)
				del self.recordings[i]

	def findFarestNoteWithLongestDuration(self,recordings):

		selectLimit=self.selectLimit

		selected=[int(recordings[0][0].split("_")[0])]
		selectedFiles=[recordings[0][0]]

		bestScore=0
		bestIndex=0
		index=0

		while len(selected)<selectLimit:

			baseNote=int(recordings[index][0].split("_")[0])

			for i,rec in enumerate(recordings):
				note=int(rec[0].split("_")[0])
				if note not in selected:
					duration=rec[1]
					noteDistance=abs(baseNote-note)
					score= noteDistance*(duration/5)
					#print ("score",score)
					if score>bestScore:
						bestScore=score
						bestIndex=i

			index=bestIndex

			selected.append(int(recordings[bestIndex][0].split("_")[0]))
			selectedFiles.append(recordings[bestIndex][0])
			bestScore=0

		return selected,selectedFiles

	def processRecordings(self,recordings):
		print("***Process recordings")
		recFolder=self.recordingsFolder

		if len(recordings)>self.selectLimit:

			recordings=list(reversed(sorted(recordings, key=itemgetter(1))))

			#now fill the list
			selected,selectedFiles=self.findFarestNoteWithLongestDuration(recordings)

			#prepare sampler folder
			#numOfSamplers=len(os.walk(self.samplersFolder).next()[1])+1

			#numOfSamplers=len(list(os.walk(self.samplersFolder)).next()[1])+1
			#numOfSamplers=next(len(list(os.walk(self.samplersFolder)))[1])+1

			numOfSamplers=(len(next(os.walk(self.samplersFolder))[1]))+1
			print("numOfSamplers",numOfSamplers)
			newsamplerDir=self.samplersFolder+str(numOfSamplers)

			#createfolder
			if not os.path.exists(newsamplerDir):
				os.makedirs(newsamplerDir)

			sleep(1)

			#move good files
			for s in selectedFiles:
				#print (recFolder+s)
				sWithoutDuration=s.split("_")[0]
				source=recFolder+s+".wav"
				destination=newsamplerDir+"/"+sWithoutDuration+".wav"
				print ("source,destination",source,destination)
				try:
					os.rename(source,destination)

					#jpg
					source=recFolder+s+".jpg"
					destination=newsamplerDir+"/"+sWithoutDuration+".jpg"
					#resize
					img = Image.open(source)
					img2=img.resize((self.imgResizeSize[0], self.imgResizeSize[1]), PIL.Image.ANTIALIAS)
					img2.save(destination)
				except:
					print ("skipping ",source)


				#os.rename(source,destination)

			#remove all files in recordings folder
			#shutil.rmtree(recFolder)
			#os.makedirs(recFolder)

			print ("selected",selected)
			print ("selected files",selectedFiles)
			#print ("all recordings",recordings)
			return True

		else:
			print ("not enough samples recorded!!!!!! sampler won't be created")
			#remove all files in recordings folder

			return False





if __name__ == "__main__":


	k = karaokesampler()
	#k.getAudioDevies()

	k.recordKaraoke()
