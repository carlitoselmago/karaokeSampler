# -*- coding: utf-8 -*-
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')
import time, numpy, pygame.mixer, pygame.sndarray
try:
	from scikits.samplerate import resample
except:
	from samplerate import resample
import cv2
import time, datetime
#from tools import midifile
import pygame
from os.path import basename
import glob,os
import threading
import numpy as np
import mido
from mido import Message, MidiFile, MidiTrack
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
import operator
import zmq

class samplerPlayer():

	mode="opencv" #modes: opencv, upbge

	samplerdelay=0.16 #algo entre 0.1 y 0.8
	samplerVolume=1.5	#1.5

	preparedSounds=[]
	lyricMessageCount=0
	lyricMessageCountInBlocks=0
	lastLyrics=[]
	lastSylab=0
	#blockLines=2 #amount of lines per block of lyrics
	blockLineCounter=0
	lineJumpCounter=0
	blackListRecordings=[]

	minNote=30
	minNoteUp=24


	def __init__(self,windowName):
		print ("sampler Player init")
		self.sounds=[]
		self.notes=[]
		if self.mode=="upbge":
			self.blockLines=2
		else:
			self.blockLines=4
		#self.secondaryDisplay=[1024,768]
		self.windowSize=[2880,1800]#[1024,768]#[1920,1080]#[800,450]#[800,450]
		self.moveUp=0#5#1080#768
		self.moveLeft=0#800#0
		#self.moveUp=1050
		fonts_path = "fonts"#os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts')

		self.fonts=[
		ImageFont.truetype(os.path.join(fonts_path, 'garamondbold.ttf'), 32),
		ImageFont.truetype(os.path.join(fonts_path, 'garamond.ttf'), 32),
		ImageFont.truetype(os.path.join(fonts_path, 'garamondbold.ttf'), 32)]
		self.percentageOfmessagesForLeadTrack=5.9
		self.percentageOfspreadNotesForLeadTrack=69.0
		self.customText=""

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

		if self.mode=="upbge":
			ctx = zmq.Context.instance()
			self.s = ctx.socket(zmq.PUSH)
			url = 'tcp://127.0.0.1:5558'
			self.s.connect(url)

		if __name__ != "__main__":
			
			if self.mode=="upbge":
				print("mode:","upbge")
				t = threading.Thread(target=self.manageLyrics, args = ("manageLyrics",)) 
				t.start()
			else:
				print("mode:","openCV")
				t = threading.Thread(target=self.showImage, args = ("showImage",))
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


	def loadImagesSampler(self,samplerNumber):
		#Creo que esta funcion ya no se ejecuta
		self.imgs=[]
		for file in glob.glob("samplers/"+samplerNumber+"/*.jpg"):
			self.imgs.append( cv2.imread(file))
			

	def findClosestNote(self,notes,note):

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


	def renewSampler(self,threadName):

		tempNotes=[]
		tempSounds=[]
		tempImgs=[]
		apisendimages=[]
		for file in glob.glob("recordings/*.wav"):
			if file not in self.blackListRecordings:
				file=file.replace("\\","/")
				try:
					a = pygame.mixer.Sound(file)
					if a.get_length()>0.2:
						#good sound
						tempNotes.append(int(os.path.splitext(basename(file))[0].split("_")[0]))
						tempSounds.append(a)
						imagefile=file.replace("wav","jpg")
						tempImgs.append( cv2.imread(imagefile))
						apisendimages.append(os.getcwd()+"/"+imagefile)
						
					else:
						self.blackListRecordings.append(file)
				except:
					self.blackListRecordings.append(file)
		#print("NEW PHOTO TAKEN!",filename)
		#send only last 5 photos
		if self.mode=="upbge":
			self.s.send_json({"loadimages":apisendimages[-5:]})
		
		self.notes=tempNotes
		self.sounds=tempSounds
		self.imgs=tempImgs

		return ""



	def constructSamplerTrack(self,notesForSampler,totaltime,samplerNumber):

		preNotes=self.notes

		for n in notesForSampler: #parse all notes

			if int(n) not in self.notes:

				if int(n)<self.minNote:
					n=int(n)+self.minNoteUp


				closestNote=random.choice(preNotes)
				#closestNote=self.findClosestNote(preNotes,n)
				closestNoteFilename="samplers/"+samplerNumber+"/"+str(closestNote)+".wav"
				#print "SOX PITCH ",n
				self.soxPitch(closestNoteFilename,"samplers/"+samplerNumber+"/"+str(n)+".wav",closestNote,n)

				self.notes.append(int(n))
				self.sounds.append(pygame.mixer.Sound("samplers/"+samplerNumber+"/"+str(n)+".wav"))

		return True

	def soxPitch(self,inputFile,destinationFile,originPitch,destinationPitch):

		pitchChange=((destinationPitch-originPitch)*100)
		command='sox "'+inputFile+'" "'+destinationFile+'" speed '+str(pitchChange)+'c'
		prog = subprocess.call(command,shell=True)#, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)

		return True#process.returncode

	def getStepIndex(self,dt,totalSteps,totalTime):

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

	def calculateSemioctavesToPercent(self,origin,destination):
		cents=(origin-destination)*100.0
		percent=(1000000*pow(2,(cents/100/12)))/1000000

		"""
		s= 0.99994
		semitones=(origin-destination)
		percent=semitones/12
		#f2 = f1 * 2^( C / semitones )
		"""

		return percent

	def playSamplerNotewithDelay(self,message,delayTime):

		sleep(delayTime)
		note=message.note

		if note<self.minNote:
			#print("changing pitch",note)
			note=int(note)+self.minNoteUp
			#print("resulting note",note)
		#print ("note",note)

		if note not in self.notes:
			#create the note
			chosenStartNote=random.choice(self.notes)
			soundIndex=self.notes.index(chosenStartNote)
			chosenStartSound=self.sounds[soundIndex]
			snd_array = pygame.sndarray.array(chosenStartSound)
			percent=self.calculateSemioctavesToPercent(chosenStartNote,note)

			snd_resample = resample(snd_array,percent, "sinc_fastest").astype(snd_array.dtype)
			# take the resampled array, make it an object and stop playing after 2 seconds.
			snd_out = pygame.sndarray.make_sound(snd_resample)
			#snd_out.play()
			#self.notes
			self.notes.append(note)
			self.sounds.append(snd_out)

		#play or stop the note
		soundIndex=self.notes.index(note)
		if message.type=="note_off" or message.velocity==0:
			#note off
			self.sounds[soundIndex].stop()
			#self.sounds[soundIndex].set_volume(0)
		else:
			#note on
			if self.mode=="upbge":
				self.s.send_json({"event":"playnote"})
			self.img=random.choice(self.imgs)
			volume=(message.velocity/127.0)*self.samplerVolume
			if volume>1:
				volume=1
			try:
				self.sounds[soundIndex].set_volume(volume)
				self.sounds[soundIndex].play()
			except:
				pass
		return

	def find_nearest(self,array,value): #returns index of nearest number in array
		return min(range(len(array)), key=lambda i: abs(array[i]-value))

	def scoreNearest(self,array,target):
		#lower is better

		#first normalize the array 
		norm = [float(i)/max(array) for i in array]

		scores=[]
		for v in norm:
			distance=abs(target-v)
			scores.append(distance)
		
		scores = [float(i)/max(scores) for i in scores]
		return scores

	def find_between(self, s, first, last ):
	    try:
	        start = s.index( first ) + len( first )
	        end = s.index( last, start )
	        return s[start:end]
	    except ValueError:
	        return ""

	def unifyText(self,text):
		sylabs=[text]
		if "/" in text:
			temp=text.replace("/","")
			if temp=="":
				sylabs=["\r"]
			else:
				sylabs=["\r",temp]
		elif "\\" in text:
			temp=text.replace("\\","")
			if temp=="":
				sylabs=["\n"]
			else:
				sylabs=["\n",temp]

		return sylabs


	def getTrackNumbers(self,midiSong,songTempo):
		#Analizes midi file and finds the apropiate track for midi sampler
		
		tracks=[]
		notasInTrack=[]
		self.lyrics=[]
		lyricsAlltracks=[]
		self.typeOfLineJump="dashes"
		
		trackstepdivision=50
		trackstep=(midiSong.length/trackstepdivision)
		trackspreadScores=[]
		trackaverageNotes=[]
		musictracks=[0] * len(midiSong.tracks)
		trackmessages=0
		trackfound=False

		#track title based filter
		blacklist=["DRUMS","BATER","BATTER","HIHAT"]
		whitelist=["MELOD","VOC","VOZ"]

		trackNotes=[]
		print("SONG LENGTH",midiSong.length)
		print("SONG TEMPO",songTempo)

		# CHOOSE THE SAMPLER MIDI TRACK:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

		# add scores to each track based on: amount of notes, spread over the song, spread over pitch (avoid drums and continuous note bass), ban keywords like "bass" or "percussion"

		for i, track in enumerate(midiSong.tracks):
			messagesTypes=[0,0]#normal,lyrics
			messagesLimit=40
			newLtrack=MidiTrack()
			newLtrack.name="LETRASSSS"
			lyricsAlltracks.append(newLtrack)
			currenttrackprogress=0.0
			
			steptrackcount=0
			trackBlocks=[0] * trackstepdivision
			notesintrack=[]
			
			#print(track)
			#messagessorted=track.sort(key=operator.attrgetter('time'))
			#print(messagessorted)
			#if messagessorted:
			ismusictrack=False
			for c,message in enumerate(track):

				if not self.isLyricsMessage(message):
					#normal music message
					if hasattr(message, 'note'):
						ismusictrack=True
						trackmessages+=1
					
					currenttrackprogress+=(mido.tick2second(message.time,midiSong.ticks_per_beat,songTempo))
					#print("currenttrackprogress",currenttrackprogress)
					current_step=currenttrackprogress/trackstep
					#TODO: aumentar resolucion de steps para evitar violines y pads (tener en cuenta los porcentajes que utilizo luego abajo)
					try:
						trackBlocks[int(current_step)]=1
					except:
						pass
					try:
						notesintrack.append(message.note)
					except:
						pass
					#if currenttrackprogress
					if c<messagesLimit:
						messagesTypes[0]+=1
					#trackType="standard"
				else:
					
					if c<messagesLimit:
						messagesTypes[1]+=1

					text=message.text#self.getTextFromMessage(message)

					#TODO:CLEAN HERE MESSAGE IF NECESSARY

					lyricsAlltracks[i].append(message)
					
					"""
					sylabs=self.unifyText(text)
					for syl in sylabs:
						self.lyrics.append(syl)
					"""
			for t in blacklist:
				if  t.upper() in track.name.upper():
					ismusictrack=False
			#else:
			#	print("NOT SORTED TRACK")
			spreadScore=sum(trackBlocks)
			print("MUSIC TRACK:",track.name,ismusictrack,trackBlocks)
			#print("trackBlocks",trackBlocks)
			#print(track.name)
			#print(track.name,"spreadScore",spreadScore)
			trackType=messagesTypes.index(max(messagesTypes))
			#if trackType==0:
			if ismusictrack:
				musictracks[i]=1
				notesarray = numpy.array(notesintrack)
				if (len(notesarray)==0):
					trackaverageNotes.append(0)
				else:	
					trackaverageNotes.append(numpy.mean(notesarray))
				trackspreadScores.append(spreadScore)
			tracks.append([track.name,trackType,len(track)])

		#create a equivalence list of index for onlymusic tracks over the overall tracks 
		musiccount=0
		mtracki=[]
		for i,t in enumerate(musictracks):
			if t==1:
				mtracki.append(i)

		#TODO: todos estos loops creo que son redundantes y se podrían incluir en anteriores para optimizar el tiempo de carga
		#check what is the lyrics track with more words
		mostWords=0
		mostWordsIndex=0
		for i,track in enumerate(lyricsAlltracks):

			lCounter=len(track)
			if lCounter>mostWords:
				mostWords=lCounter
				mostWordsIndex=i

		trackWithMostLyrics=lyricsAlltracks[mostWordsIndex]
		#print ("### tracks")
		#print (tracks)
		#print ("### lyricsAlltracks")
		#print (lyricsAlltracks)
		#print ("###")
		#print (messagesTypes)
		#sys.exit()
		
		#count all standard messages
		totalMessages=trackmessages#0.0
		"""
		for i,track in enumerate(tracks):
			if track[1]==0:
				#normal track
				totalMessages+=track[2]
		"""
		#add most lyrics track back the file object
		#midiSong.tracks.append(trackWithMostLyrics)

		#get track percentages
		percentages=[]
		
		for i,track in enumerate(tracks):
			
			#Whitelist trick 
			for t in whitelist:
				if t.upper() in track[0].upper():
					trackfound=i

			if musictracks[i]==1:
			#if track[1]==0:
				percentage=(track[2]*100.0)/totalMessages
				percentages.append(percentage)
				tracks[i].append(percentage)
			#else:
			#	percentages.append(0.0)

		print("percentages",(percentages))
		print("trackspreadScores",(trackspreadScores))

		if trackfound:
			leadTrackIndex=trackfound
		else:

			#combine scores 
			norm = [float(i)/max(trackaverageNotes) for i in trackaverageNotes]
			norm2 = [float(i)/max(trackspreadScores) for i in trackspreadScores]
			norm3 = [float(i)/max(percentages) for i in percentages]
			
			print(" ")
			for i,track in enumerate(norm):
				print(tracks[mtracki[i]][0],"avgnotes",str(round(norm[i],2)),"spread",str(round(norm2[i],2)),"percent",str(round(norm3[i],2)))

			scoresNotes=np.array(self.scoreNearest(trackaverageNotes,0.75))
			scoresSpread=np.array(self.scoreNearest(trackspreadScores,0.75))
			scoresPercent=np.array(self.scoreNearest(percentages,0.51))

			print("BEST spread",tracks[ mtracki[np.where(scoresSpread==min(scoresSpread))[0][0] ]][0],"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("BEST percent",tracks[  mtracki[np.where(scoresPercent==min(scoresPercent))[0][0] ]][0],"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("BEST notes",tracks[  mtracki[np.where(scoresNotes==min(scoresNotes))[0][0] ]][0],"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

			results=scoresNotes.tolist()
			print("results",results)
			for i,r in enumerate(results):
				if scoresSpread[i]<0.32:
					results[i]=results[i]*100
				if scoresPercent[i]>0.8:
					results[i]=results[i]*100
			print("results AFTER",results)

			min_value = min(results)
			min_index = results.index(min_value)

			leadTrackIndex=mtracki[min_index]#self.trackIndex(musictracks,min_index)

			#leadTrackIndex=self.find_nearest(percentages,self.percentageOfmessagesForLeadTrack)
			#leadTrackIndex=self.find_nearest(trackspreadScores,self.percentageOfspreadNotesForLeadTrack)
		leadTrackName=tracks[leadTrackIndex][0]
		print("LEAD TRACK NAME: ",leadTrackName)

		#END  CHOOSE THE SAMPLER MIDI TRACK::::::::::::::::::::::::::::::::::::::::::::::::::::::::
		
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

			if hasattr(message, 'channel'):
				midiSong.tracks[midfileTrackNumber][i].channel=15

			if message.type =="note_on":

				if message.note not in notasInTrack:

					notasInTrack.append(message.note)

		for i,message in enumerate(midiSong.tracks[mostWordsIndex]):

			if hasattr(message, 'text'):
				text=message.text
				midiSong.tracks[mostWordsIndex][i].text=text+"[:]"
				if "\r" in text or "\n" in text:
					self.typeOfLineJump="text"
				self.lyrics.append(text)
				"""
				sylabs=self.unifyText(text)
				for syl in sylabs:
					self.lyrics.append(syl)
				"""
		#print self.typeOfLineJump

		#print "song has ",totalMessages,"standard messages"
		#print tracks
		#print self.lyrics


		#print ("MidoTrackNumber",MidoTrackNumber,"PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
		#print ("midfileTrackNumber",midfileTrackNumber,"MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")

		return midfileTrackNumber,notasInTrack,midiSong

	def separateSamplerChanel(self,midiSong,trackIndex,samplerChanel=10):
		for i, track in enumerate(midiSong.tracks):
			for c,message in enumerate(track):
				pass

	def trackIndex(self,musictracks,index):
		musiccount=0
		for i,t in enumerate(musictracks):
			if musiccount==index:
				return i
			if t==1:
				musiccount+=1
			

	def isLyricsMessage(self,message):
		#if isinstance(mido.midifiles.meta.MetaMessage):
		if hasattr(message, 'text'):
			return True
		else:
			return False

	def playSong(self,filename,songpath,samplerNumber,customText):
		print("PLAY SONG")
		self.notes=[]
		self.sounds=[]
		renewRound=0
		self.blackListRecordings=[]
		self.lastLyrics=[]
		self.lyricMessageCount=0
		#filename=filename.decode("utf-8")
		#print filename,"filename"
		self.status="loading"
		self.customText=customText
		self.songName=filename.split(".")[0]
		if self.mode=="upbge":
			self.s.send_json({"event":"loadsong","songname":self.songName.replace("KARsongs/", "").split("/")[-1],"customtext":self.customText})
		
		#get the real duration of the song
		mid = MidiFile(songpath)
		songDuration=mid.length
		songTempo=self.get_tempo(mid)
		midfileTrackNumber,notesForSampler,mid=self.getTrackNumbers(mid,songTempo)
		if self.mode=="upbge":
			self.s.send_json({"lyrics":self.lyrics})
		#print(self.lyrics)

		#prepare lyrics blocks
		self.lyricblocks=self.prepareLyricBlocks(self.lyrics)
		self.currentlyricblock=0
		self.lastsylabplayed=-1
		#self.prepareSampler(str(samplerNumber))
		#self.constructSamplerTrack(notesForSampler,songDuration,str(samplerNumber))#max(m.kartimes)) #!!!!!!!!!!!!!!

		start=datetime.datetime.now()

		dt=0.
		totalTime=songDuration#max(m.kartimes)

		lastPlayingNotes=[]
		lastPlayingNotesNames=[]

		playDelay=1.7
		img=self.lastImage

		self.status="ready"

		while self.status=="ready":
			sleep(1)

		dt=0.0
		if self.mode=="upbge":
			self.s.send_json({"event":"playsong"})
		
		try:
			if self.mode=="upbge":
				self.s.send_json({"event":"newblockoflyrics","lyrics":self.LyricBlocks[0],"nextlyrics":self.LyricBlocks[1]})
		except:
			pass

		self.customText=""
		#while True:
		with mido.open_output("Microsoft GS Wavetable Synth 0") as output:

		#while pygame.mixer.music.get_busy():
			for message in mid.play(meta_messages=True):#meta_messages=True):

				#if message.type=="lyrics":
				#	print message
				#print message.type,message
				if self.status=="stop":
					#stop the song
					if self.mode=="upbge":
						self.s.send_json({"event":"stopsong"})
					break

				nowNoteNames=[]

				dt+=message.time

				#self.m.update_karaoke(dt)

				if message.type=="note_on" or message.type=="note_off":

					if message.channel==15:#MidoTrackNumber:#midfileTrackNumber:
						if len(self.notes)>0:
							try:
								#PLAY NOTE FROM SAMPLER
								t = threading.Thread(target=self.playSamplerNotewithDelay, args = (message,self.samplerdelay)) #algo entre 0.1 y 0.8
								t.start()
							except:
								pass



				if not self.isLyricsMessage(message):
					if message.type=="marker" or message.type=="note_on" or message.type=="note_off" or message.type=="sysex" or  message.type=="program_change" or message.type=="control_change" or message.type=="pitchwheel" or message.type=="sysex":
						if hasattr(message, 'velocity'):

							message.velocity=int(message.velocity/2)
						output.send(message)
				else:
					if hasattr(message, 'text'):
						if "[:]" in message.text:
							self.lyricMessageCount+=1
					#self.lyricMessageCount+=1
					#if hasattr(message, 'text'):
					#text=self.getTextFromMessage(message)
					#print text,len(text)


					"""
					sylabs=self.unifyText(message.text)
					for syl in sylabs:
						self.lyricMessageCount+=1
					"""

				if dt>20.0 and dt>renewRound:
					renewRound=dt+10.0
					#print "sampler renewed!!"
					r = threading.Thread(target=self.renewSampler, args = ("renewSampler",)) 
					r.start()



		self.status="iddle"
		if self.mode=="upbge":
			self.s.send_json({"event":"stopsong"})
		return True

	def prepareLyricBlocks(self,lyrics):
		#XXXXXX
		#prebuilds lyrics into blocks of lines based on self.blockLines
		lyricblocks=[]
		block=[]
		line=[]
		linecounter=0
		apiscore={}
		pastcredits=False
		self.LyricBlocks=[]
		self.apiscore={} #list of events: 0 word, 1 line break, 2 block break

		for i,syl in enumerate(lyrics):
			next_syl=lyrics[i]
			if self.hasLineJump(next_syl):
				#create new line
				linecounter+=1
				if len(line)>0:
					block.append(line)
					apiscore[i]=1
				line=[]
			if linecounter==self.blockLines:
				#create new block
				lyricblocks.append(block)
				apiscore[i]=2
				block=[]
				linecounter=0
			line.append(syl)
		
		
		print("lyricblocks length:",len(lyricblocks))
		print("::::::::::::::::::")
		for b in lyricblocks:
			print(b)
		self.LyricBlocks=lyricblocks
		self.apiscore=apiscore

	def putTextPIL(self,img,text,cordinates,font=0,centered=False,color=(255,255,255)):
		pil_im = Image.fromarray(img)
		pil_d = ImageDraw.Draw(pil_im)
		if centered:
			w, h = pil_d.textsize(text,font=self.fonts[font])
			cordinates=((self.windowSize[1]-w)/2,cordinates[1])
		pil_d.text(cordinates,text,color,font=self.fonts[font])
		imgWithText = np.array(pil_im)
		return imgWithText


	def hasLineJump(self,text):
		#if "\n" or "\r" in text:
		#	return True 
		if "\n" in text or "\r" in text or "\\" in text or "/" in text or "@" in text:
			return True
		#print("no lj:",text)
		return False
	
	"""
	def isLineJump(self,text):
		if self.typeOfLineJump=="dashes":
			if "\\" in text or "/" in text:
				return True
			else:
				return False
		else:

			if "\n" in text or "\r" in text:# or "\\" in text or "/" in text:# or text=="":
				#print text ,"isLineJump"
				return True
			else:
				return False
	"""
	"""
		if self.typeOfLineJump=="dashes":
			if "\\" in text or "/" in text:
				return True
			else:
				return False
		else:

			if "\n" in text or "\r" in text:# or "\\" in text or "/" in text:# or text=="":
				#print text ,"hasLineJump"
				return True
			else:
				return False
	"""
		
	
	def manageLyrics(self,threadName):
	
		running=True

		while running:
			imgText=""

			if self.status=="playing":
				self.printLyrics()
			"""
			if self.status=="stop":
				running=False
			"""
			sleep(0.09)
	def printLyrics(self):
		#X
		#self.lyricMessageCount
		#self.lyrics
		#print self.lyrics[self.lyricMessageCount]
		#print len(self.lyrics[self.lyricMessageCount]),"index:",self.lyricMessageCount

		if self.lastSylab<self.lyricMessageCount or self.lyricMessageCount==0:
			#change of step index in lyrics

			if self.lyricMessageCount-self.lastSylab>1:
				#we missed a step reproduce both
				steps=[]
				for s in range(self.lyricMessageCount-self.lastSylab):
					steps.append((self.lastSylab+s)+1)
			else:
				steps=[self.lyricMessageCount]

			sylabCounter=0

			multiplelines=self.lastLyrics
			self.lastLyrics=[]
			for s in steps:
				#LIVE LYRICS LOOP
				sylabCounter+=1
				if len(self.lyrics)>(s):
					if self.lastsylabplayed!=s:
						
						currentSylab=self.lyrics[s]

						self.s.send_json({"currentSylab":currentSylab,"sylabindex":s})
						#print("currentSylab",currentSylab)
						if s in self.apiscore:
							if self.apiscore[s]==2:
								#block change
								#print("self.currentlyricblock",self.currentlyricblock)
								nextblocklyrics=""
								#if len(self.LyricBlocks)<self.currentlyricblock+2:
								try:
									nextblocklyrics=self.LyricBlocks[self.currentlyricblock+2]
								except:
									#last block of lyrics
									pass
								#print("nextblocklyrics!!!!!",nextblocklyrics)
								try:
									self.s.send_json({"event":"newblockoflyrics","lyrics":self.LyricBlocks[self.currentlyricblock+1],"nextlyrics":nextblocklyrics})
								except:
									pass
								self.currentlyricblock+=1
							if self.apiscore[s]==1:
								#line jump
								self.s.send_json({"event":"linejump"})
						self.lastsylabplayed=s
				self.lastSylab=s
	

	def printLyricsOpenCV(self,imgCtext):

		#self.lyricMessageCount
		#self.lyrics
		#print self.lyrics[self.lyricMessageCount]
		#print len(self.lyrics[self.lyricMessageCount]),"index:",self.lyricMessageCount

		if self.lastSylab<self.lyricMessageCount or self.lyricMessageCount==0:
			#change of step index in lyrics

			if self.lyricMessageCount-self.lastSylab>1:
				#we missed a step reproduce both
				steps=[]
				for s in range(self.lyricMessageCount-self.lastSylab):
					steps.append((self.lastSylab+s)+1)
			else:
				steps=[self.lyricMessageCount]

			sylabCounter=0

			threelines=self.lastLyrics
			self.lastLyrics=[]
			for s in steps:
				#print "STEP",s
				sylabCounter+=1
				if len(self.lyrics)>(s):
					currentSylab=self.lyrics[s]
					#print "index",s,"currentSylab",currentSylab
					#print currentSylab
					if (self.hasLineJump(currentSylab)) or (s==0): #end of block!

						self.lineJumpCounter+=1

						if self.lineJumpCounter==self.blockLines or (s==0):
							self.lineJumpCounter=0

							#if self.blockLineCounter==0:

							#print "BUILDING NEW BLOCK OF LYRICS!!!!!!"


							self.lyricMessageCountInBlocks=self.lyricMessageCount

							#let's build the new block of lyrics
							#find how many sillabs till next new block
							parsingBlock=True

							lineCounter=0
							threelines=[[]]

							#check next syllab after last break (in case it's not the first block)
							if s!=0:
								#not first block
								parser=0
								advancedSylab=self.lyrics[s]
								findingNextSylab=True
								while findingNextSylab:
									if self.typeOfLineJump=="dashes":
										if "\\" in advancedSylab or "/" in advancedSylab:
											findingNextSylab=False
									else:
										if "\n" in advancedSylab or "\r" in advancedSylab:
											findingNextSylab=False
									advancedSylab=self.lyrics[s+parser]
									s+=1
									parser+=1


							parser=0
							while parsingBlock:
								#print "s+parser",s+parser
								#print "self.lyricMessageCount+parser",s+parser
								#print "len lyrics",len(self.lyrics)
								#print "s+parser",s+prepareSampler

								if len(self.lyrics)<=(s+parser):
									parsingBlock=False
									self.blockLineCounter=0
								else:

									advancedSylab=self.lyrics[s+parser]
									#print "advancedSylab:",advancedSylab,"s+parser:",s+parser
									#print advancedSylab
									if self.hasLineJump(advancedSylab):

										lineCounter+=1
										threelines.append([])
										#LINE JUMP!
										self.blockLineCounter+=1
									#if advancedSylab=="\n":
									if (self.blockLineCounter==self.blockLines):# or (s==0):
										parsingBlock=False
										self.blockLineCounter=0
										#print "END OF BLOCK"
									#elif advancedSylab=="\r":
										#new line

									#else:
									threelines[lineCounter].append(advancedSylab)

									parser+=1


							self.lastLyrics=threelines


				#self.lyricMessageCountInBlocks=self.lyricMessageCount-sylabCounter

				self.lastSylab=s#self.lyricMessageCount

		else:
			threelines=self.lastLyrics
		#threelines=[["1","2","3"],["4","5","6"],["7","8","9"]]
		#self.lastLyrics


		paragrapahSinged=self.lyricMessageCount-self.lyricMessageCountInBlocks

		#display images
		singed=(0,255,255)
		toSing=(255,255,255)
		color=singed
		shadowcolor="black"
		y0, dy = 50, 40
		sylabCount=0



		#for i, line in enumerate(imgText.split('\n')):
		for i,line in  enumerate(threelines):
			y = y0 + i*dy
			lineX=30
			for e,sylab in enumerate(line):


				#checkSylab=sylab.strip()
				cleanSylab=sylab.replace("/","").replace("\\","").replace("_"," ")

				if "@" not in cleanSylab:

					if sylabCount==paragrapahSinged:
						color=toSing
					pil_im = Image.fromarray(imgCtext)
					pil_d = ImageDraw.Draw(pil_im)
					w, h = pil_d.textsize(cleanSylab,font=self.fonts[0])
					#print "w",w,"sylab",sylab
					#cordinates=((self.windowSize[0]-w)/2,cordinates[1])

					cordinates=(lineX,y)

					#shadow
					#pil_d.text((lineX-1, y), cleanSylab, font=self.fonts[0], fill=shadowcolor)
					pil_d.text((lineX+1, y), cleanSylab, font=self.fonts[0], fill=shadowcolor)
					#pil_d.text((lineX, y-1), cleanSylab, font=self.fonts[0], fill=shadowcolor)
					pil_d.text((lineX, y+1), cleanSylab, font=self.fonts[0], fill=shadowcolor)

					pil_d.text(cordinates,cleanSylab,color,font=self.fonts[0])
					imgCtext = np.array(pil_im)
					lineX+=w
					#sylabCount+=1
					#if checkSylab !="\n" or checkSylab !="\r" or checkSylab!="":
				sylabCount+=1
				#if self.lastSylab<self.lyricMessageCount:
				#	print sylab



		self.lastLyrics=threelines

		return imgCtext

	def showImage(self,threadName):
		cv2.namedWindow(self.windowName, cv2.WND_PROP_FULLSCREEN)
		cv2.setWindowProperty(self.windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
		cv2.imshow(self.windowName,self.img)

		cv2.resizeWindow(self.windowName, self.windowSize[0], self.windowSize[1])

		cv2.moveWindow(self.windowName,self.moveLeft,-self.moveUp)
		running=True

		while running:
			imgText=""

			imgCtext=self.img.copy()

			#check if karaoke lyrics exist
			if self.customText!="" and self.status!="playing":
				self.songName=self.songName.replace("KARsongs/", "").split("/")[-1]
				#print "show singer text"
				#self.songName.encode("ascii","ignore")

				imgCtext=self.putTextPIL(imgCtext,self.songName,(10,190),1,True,(0,255,255))
				#imgCtext=self.putTextPIL(imgCtext,"CANTA: "+self.customText.decode("utf-8").upper(),(10,230),2,True)
				imgCtext=self.putTextPIL(imgCtext,"CANTA: "+self.customText.upper(),(10,230),2,True)
				#cv2.putText(imgCtext, ord(u"É"), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255),1)
				#cv2.putText(imgCtext,"CANTA: "+self.customText, (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255),1)

			#if 'm' in self.__dict__ and self.status=="playing":
			if self.status=="playing":
				imgCtext=self.printLyricsOpenCV(imgCtext)

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

	def get_tempo(self,mid):
		for msg in mid:# Search for tempo
			if msg.type == 'set_tempo':
				return msg.tempo
		return 500000       # If not found return default tempo



if __name__ == "__main__":
	K=samplerPlayer("karaoke")
	#K.playSong("bellabestia","bellabestia.kar",20,"carlos")
	#K.playSong("bellabestia.kar",12,"custom text ñ here")
	#K.playSong("toxic","KARsongs/A-B/A-B/Britney Spears - Toxic.kar",20,"custom text here ñññ Á")
	K.playSong("mamma mia","KARsongs/A-B/A-B/Abba - Mamma Mia.kar",20,"development")
