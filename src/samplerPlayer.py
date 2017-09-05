# -*- coding: utf-8 -*- 
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import cv2
import time, datetime
from tools import midifile
import pygame
from os.path import basename
import glob,os
import threading
import numpy as np
import mido
from mido import MidiFile
import subprocess
#import commands
from shutil import copyfile
import pprint
from time import sleep
import random
import  PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

class samplerPlayer():
	
	preparedSounds=[]
	
	
	def __init__(self,windowName):
		print ("sampler Player init")
		fonts_path = "fonts"#os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts')
		print fonts_path
		self.fonts=[ 
		ImageFont.truetype(os.path.join(fonts_path, 'garamondbold.ttf'), 32), 
		ImageFont.truetype(os.path.join(fonts_path, 'garamond.ttf'), 32),
		ImageFont.truetype(os.path.join(fonts_path, 'garamondbold.ttf'), 32)]
		self.windowSize=[800,450]
		self.percentageOfmessagesForLeadTrack=5.9
		self.customText=""
		self.midiTrackToSampler=0
		self.resolution=6 #sampler score resolution, the bigger the more precise
		#pygame.mixer.pre_init(44100, -16, 1, 512)
		self.windowName=windowName
		self.lastImage=self.createBlackImage()
		self.img=self.lastImage
		self.blankImage=self.lastImage
		self.octaveAdjust=-12
		self.playingSounds=[]
		self.playingSoundsTime=[]
		pygame.mixer.pre_init(44100, -16, 2, 2048)
		pygame.mixer.init()
		self.status="iddle"

		t = threading.Thread(target=self.showImage, args = ("showImage",)) #algo entre 0.1 y 0.8
		t.start()
		#pygame.init()
			
	def createBlackImage(self):
		img=cv2.imread("black.jpg")
		#img = np.zeros((800,450,3), np.uint8)
		return img
	
	def loadSampler(self,samplerNumber):
		
		
		self.sounds=[]
		self.notes=[]
		for file in glob.glob("samplers/"+samplerNumber+"/*.wav"):
			self.sounds.append(pygame.mixer.Sound(file))#AudioSegment.from_file(file))
			self.notes.append(int(os.path.splitext(basename(file))[0].split("_")[0]))
			
		#print self.notes
		#print self.sounds
		
	
	def loadImagesSampler(self,samplerNumber):
		self.imgs=[]
		for file in glob.glob("samplers/"+samplerNumber+"/*.jpg"):
			self.imgs.append( cv2.imread(file))
	
	def findClosestNote(self,notes,note):
		#print notes,note,"BAAAA"
		closestNoteIndex=0
		closestDistance=999999999
		closesNote=0
		
		if len(notes)==1:
			return notes[0]
		
		for i,n in enumerate(notes):
		   distance=abs(int(n)-note)
		   if distance<closestDistance:
			   closesDistance=distance
			   closestNoteIndex=i
			   closesNote=int(n)
			   
		return notes[closestNoteIndex]

	
	def constructSamplerTrack(self,notesForSampler,totaltime,samplerNumber):
		
		preNotes=self.notes
		
		print (notesForSampler,"NOTES REQUIRED")
		print (preNotes,"ALL NOTES AT START")

		for n in notesForSampler: #parse all notes
			
			if int(n) not in self.notes:
				#print "CREATING NOTES"
				closestNote=random.choice(preNotes)
				#closestNote=self.findClosestNote(preNotes,n)
				closestNoteFilename="samplers/"+samplerNumber+"/"+str(closestNote)+".wav"
				print "SOX PITCH ",n
				self.soxPitch(closestNoteFilename,"samplers/"+samplerNumber+"/"+str(n)+".wav",closestNote,n)
				
				self.notes.append(int(n))
				self.sounds.append(pygame.mixer.Sound("samplers/"+samplerNumber+"/"+str(n)+".wav"))

		print(self.notes,"NOTES AFTER PROCESSED")
		return True
	
	def soxPitch(self,inputFile,destinationFile,originPitch,destinationPitch):
		
		pitchChange=((destinationPitch-originPitch)*100)
		command='sox "'+inputFile+'" "'+destinationFile+'" speed '+str(pitchChange)+'c'
		prog = subprocess.call(command,shell=True)#, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
	
		return True#process.returncode
  
	def getStepIndex(self,dt,totalSteps,totalTime):
		
		#print "dt,totalSteps,totalTime",dt,totalSteps,totalTime
		return int((totalSteps*dt)/totalTime)
	
	def dump(self,obj):
		for attr in dir(obj):
		  print ("obj.%s = %s" % (attr, getattr(obj, attr)))

	def playWithDelay(self,output,message,delayTime=.200):
		sleep(delayTime)
	
		output.send(message)
		return

	def prepareSampler(self,samplerNumber):
		pygame.mixer.init()#frequency=22050, size=-16, channels=2 ,buffer=44100)
		
		self.loadSampler(samplerNumber)
		self.loadImagesSampler(samplerNumber)

	def playSamplerNotewithDelay(self,message,delayTime):
		sleep(delayTime)
		soundIndex=self.notes.index(message.note)
		if message.type=="note_off" or message.velocity==0:
			#note off
			self.sounds[soundIndex].stop()
			#self.sounds[soundIndex].set_volume(0)
		else:
			#note on
			self.img=random.choice(self.imgs)
			self.sounds[soundIndex].set_volume(message.velocity/127.0)
			self.sounds[soundIndex].play()

	def find_nearest(self,array,value): #returns index of nearest number in array
		return min(range(len(array)), key=lambda i: abs(array[i]-value))

	def getTrackNumbers(self,midiSong):

		tracks=[]
		notasInTrack=[]

		for i, track in enumerate(midiSong.tracks):
			#trackType=""
			messagesTypes=[0,0]#normal,lyrics
			messagesLimit=5
			for c,message in enumerate(track):
				
				if c==messagesLimit:
					break
				if message.type=="note_on" or message.type=="note_off" or message.type=="sysex" or  message.type=="program_change" or message.type=="control_change":
					#normal message
					
					messagesTypes[0]+=1
					#trackType="standard"
				else:
					messagesTypes[1]+=1
					#trackType="lyrics"
					#lyrics message

			trackType=messagesTypes.index(max(messagesTypes))
			
			tracks.append([track.name,trackType,len(track)])

		#count all standard messages
		totalMessages=0.0
		for i,track in enumerate(tracks):
			if track[1]==0:
				#normal track
				totalMessages+=track[2]

		#get track percentages
		percentages=[]
		for i,track in enumerate(tracks):
			if track[1]==0:
				percentage=(track[2]*100.0)/totalMessages
				percentages.append(percentage)
				tracks[i].append(percentage)
			else:
				percentages.append(0.0)

		leadTrackIndex=self.find_nearest(percentages,self.percentageOfmessagesForLeadTrack)
		leadTrackName=tracks[leadTrackIndex][0]

		count=0
		for i,track in enumerate(tracks):
			if track[1]==0:
				if i==leadTrackIndex:
					MidoTrackNumber=count
					break

				count+=1

		midfileTrackNumber=leadTrackIndex

		#construct a list of all notes that will be required during playback
		for i,message in enumerate(midiSong.tracks[midfileTrackNumber]):
			#print dir(midiSong.tracks[midfileTrackNumber][i])
			if hasattr(message, 'channel'):
				midiSong.tracks[midfileTrackNumber][i].channel=15

			if message.type =="note_on":

				if message.note not in notasInTrack:

					notasInTrack.append(message.note)

		#print "song has ",totalMessages,"standard messages"
		print tracks

		#print ("MidoTrackNumber",MidoTrackNumber,"PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
		print ("midfileTrackNumber",midfileTrackNumber,"MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")

		return midfileTrackNumber,notasInTrack,midiSong
		
	def separateSamplerChanel(self,midiSong,trackIndex,samplerChanel=10):
		for i, track in enumerate(midiSong.tracks):
			for c,message in enumerate(track):
				pass

	def playSong(self,filename,songpath,samplerNumber,customText):

		filename=filename.decode("utf-8")
		print filename,"filename"
		self.status="loading"
		self.customText=customText
		self.songName=filename.split(".")[0]
		
		#get the real duration of the song
		mid = MidiFile(songpath)
		songDuration=mid.length

		
		trackNumber=self.midiTrackToSampler
		
		self.m=midifile.midifile()
		#print "SONG HAS ",mid.tracks," TRACKS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
		midfileTrackNumber,notesForSampler,mid=self.getTrackNumbers(mid)

		#TODO: quitar dependencia de midifile.py
		samplerTrack=self.m.load_file((songpath).encode("latin1"),midfileTrackNumber) #TODO: atención esto seguramente dará error cuando cambie de canción
		
		self.prepareSampler(str(samplerNumber))
		self.constructSamplerTrack(notesForSampler,songDuration,str(samplerNumber))#max(m.kartimes))

		start=datetime.datetime.now()
		
		dt=0.
		totalTime=songDuration#max(m.kartimes)
		
		lastPlayingNotes=[]
		lastPlayingNotesNames=[]
		
		playDelay=1.7
		img=self.lastImage
		#print mido.get_output_names()
		#otherOutput=mido.open_output("loopMIDI Port 1 3") 
		
		self.status="ready"

		while self.status=="ready":
			sleep(1)
		
		
		dt=0.0

		self.customText=""
		#while True:
		with mido.open_output("Microsoft GS Wavetable Synth 0") as output:

		#while pygame.mixer.music.get_busy():
			
			for message in mid.play(meta_messages=True):#meta_messages=True):
				#print message
				if self.status=="stop":
					#stop the song
					break

				nowNoteNames=[]

				dt+=message.time

				self.m.update_karaoke(dt)

				if message.type=="note_on" or message.type=="note_off":
					
					if message.channel==15:#MidoTrackNumber:#midfileTrackNumber:
						
						t = threading.Thread(target=self.playSamplerNotewithDelay, args = (message,0.1)) #algo entre 0.1 y 0.8
						t.start()
						
					
				if message.type=="note_on" or message.type=="note_off" or message.type=="sysex" or  message.type=="program_change" or message.type=="control_change":
					output.send(message)
			

			
		self.status="iddle"
		return True
		
	def putTextPIL(self,img,text,cordinates,font=0,centered=False,color=(255,255,255)):
		pil_im = Image.fromarray(img)
		pil_d = ImageDraw.Draw(pil_im)
		if centered:
			w, h = pil_d.textsize(text,font=self.fonts[font])
			cordinates=((self.windowSize[0]-w)/2,cordinates[1])
		pil_d.text(cordinates,text,color,font=self.fonts[font])
		imgWithText = np.array(pil_im)
		return imgWithText

	def showImage(self,threadName):
		cv2.namedWindow(self.windowName, cv2.WND_PROP_FULLSCREEN)          
		cv2.setWindowProperty(self.windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
		running=True
		
		while running:
			imgText=""
			
			imgCtext=self.img.copy()
			
			#check if karaoke lyrics exist
			if self.customText!="" and self.status!="playing": 
				self.songName=self.songName.replace("KARsongs/", "")
				#print "show singer text"
				#self.songName.encode("ascii","ignore")

				imgCtext=self.putTextPIL(imgCtext,self.songName,(10,190),1,True,(0,255,255))
				imgCtext=self.putTextPIL(imgCtext,"CANTA: "+self.customText.decode("utf-8").upper(),(10,230),2,True)
				
				#cv2.putText(imgCtext, ord(u"É"), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255),1)
				#cv2.putText(imgCtext,"CANTA: "+self.customText, (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255),1)
				
			if 'm' in self.__dict__ and self.status=="playing":

				for iline in range(3):
					imgText+=self.m.karlinea[iline]
					imgText+='__'+self.m.karlineb[iline]+'\n'
				#print ''
				
					
				#display images
				y0, dy = 50, 40
				for i, line in enumerate(imgText.split('\n')):
					y = y0 + i*dy
					imgCtext=self.putTextPIL(imgCtext,line,(30,y))
					#cv2.putText(imgCtext,line, (10,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255),1)
				
			cv2.imshow(self.windowName,imgCtext)
			if cv2.waitKey(1) == 27:
				self.singing=False
				running=False
				break
				# esc to quit

			self.opencvReady=True
		cv2.destroyAllWindows()

	
	def speedx(self,sound_array, factor):
		""" Multiplies the sound's speed by some `factor` """
		indices = np.round( np.arange(0, len(sound_array), factor) )
		indices = indices[indices < len(sound_array)].astype(int)
		return sound_array[ indices.astype(int) ]
	
	def stretch(self,sound_array, f, window_size, h):
		""" Stretches the sound by a factor `f` """

		phase  = np.zeros(window_size)
		hanning_window = np.hanning(window_size)
		result = np.zeros( len(sound_array) /f + window_size)

		for i in np.arange(0, len(sound_array)-(window_size+h), h*f):

			# two potentially overlapping subarrays
			a1 = sound_array[i: i + window_size]
			a2 = sound_array[i + h: i + window_size + h]

			# resynchronize the second array on the first
			s1 =  np.fft.fft(hanning_window * a1)
			s2 =  np.fft.fft(hanning_window * a2)
			phase = (phase + np.angle(s2/s1)) % 2*np.pi
			a2_rephased = np.fft.ifft(np.abs(s2)*np.exp(1j*phase))

			# add to result
			i2 = int(i/f)
			result[i2 : i2 + window_size] += hanning_window*a2_rephased

		result = ((2**(16-4)) * result/result.max()) # normalize (16bit)

		return result.astype('int16')
	
	def pitchshift(self,snd_array, n, window_size=2**13, h=2**11):
		""" Changes the pitch of a sound by ``n`` semitones. """
		factor = 2**(1.0 * n / 12.0)
		stretched = self.stretch(snd_array, 1.0/factor, window_size, h)
		return self.speedx(stretched[window_size:], factor)
	
	def changePitch(self,sound,originpitch,destinationpitch):
		
		transS=destinationpitch-originpitch
		factor = 2**(1.0 * transS / 12.0)
		
		
		# shift the pitch up by half an octave (speed will increase proportionally)
		#octaves = adaptedPitch  #octaves is an int
		new_sample_rate = int(sound.frame_rate * factor)#(2.0 ** octaves))
		# keep the same samples but tell the computer they ought to be played at the 
		# new, higher sample rate. This file sounds like a chipmunk but has a weird sample rate.
		chipmunk_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
		# now we just convert it to a common sample rate (44.1k - standard audio CD) to 
		# make sure it works in regular audio players. Other than potentially losing audio quality (if
		# you set it too low - 44.1k is plenty) this should now noticeable change how the audio sounds.
		chipmunk_ready_to_export = chipmunk_sound.set_frame_rate(44100)
		return chipmunk_ready_to_export
		


if __name__ == "__main__":
	K=samplerPlayer("karaoke")
	#K.playSong("bellabestia.kar")
	#K.playSong("bellabestia.kar",12,"custom text ñ here")
	K.playSong("KARsongs/ANA BELÉN - DERROCHE.kar",12,"custom text here ñññ Á")
