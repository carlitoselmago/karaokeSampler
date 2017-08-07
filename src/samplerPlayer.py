# encoding=utf8  
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
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
import commands
from shutil import copyfile
import pprint



class samplerPlayer():
    
    preparedSounds=[]
    
    
    def __init__(self,windowName):
        print ("sampler Player init")
        self.samplerFolder="8"
        self.midiTrackToSampler=3
        self.resolution=6 #sampler score resolution, the bigger the more precise
        #pygame.mixer.pre_init(44100, -16, 1, 512)
        self.windowName=windowName
        self.lastImage=self.createBlackImage()
        self.blankImage=self.lastImage
    
    def createBlackImage(self):
        img = np.zeros((512,512,3), np.uint8)
        return img
    
    def loadSampler(self):
        
        
        self.sounds=[]
        self.notes=[]
        for file in glob.glob("samplers/"+self.samplerFolder+"/*.wav"):
            self.sounds.append(pygame.mixer.Sound(file))#AudioSegment.from_file(file))
            self.notes.append(int(os.path.splitext(basename(file))[0].split("_")[0]))
            
        #print self.notes
        #print self.sounds
        
    
    def loadImagesSampler(self):
        self.imgs=[]
        for file in glob.glob("samplers/"+self.samplerFolder+"/*.jpg"):
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
    
    """
    def prepareNextNote(self,note):
        
        closestNoteIndex=0
        closestDistance=999999999
        closesNote=0
        
        for i,n in enumerate(self.notes):
            distance=abs(int(n)-note)
            if distance<closestDistance:
                closesDistance=distance
                closestNoteIndex=i
                closesNote=int(n)
        
        closestNoteSound=self.sounds[closestNoteIndex]
        
       
        notePitched=self.changePitch(closestNoteSound,adaptedPitch)
        return notePitched
    """
    
    def constructSamplerTrack(self,samplerTrack,totaltime):
        """
        division=1
        for times in range(self.resolution):
            division=division*10
        
        self.division=division
        #division=(for t in self.resolution)#10
        
        TT=round(totaltime,self.resolution)
        timesteps=int(TT*division)
        """
        timesteps=int(totaltime*(self.resolution*60))
        print("timesteps!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",timesteps)
        #create empty list of lists for each time step
        timeline=[[] for i in range(timesteps)]
        
        
        firstStep=0
        
        preNotes=self.notes
        
        for t in samplerTrack: #parse all notes
            
            #indexTimeline=int(timesteps/(round(t[2],1)))
            #indexTimeline=int(round(t[2],self.resolution)*division)
            indexTimeline=self.getStepIndex(t[3],timesteps,totaltime)
            
            if indexTimeline<timesteps:
                #print ("indexTimeline",indexTimeline)
                #print((round(t[2],1)),timesteps,indexTimeline)
                #print("indexTimeline",indexTimeline)
                
                #stablish the note "blocks"
                
                tmpStep=[]
                
                
                if t[0]=="on":
                    if firstStep==0:
                        firstStep=indexTimeline
                    timeline[indexTimeline].append(t)
                    
                    
                if t[0]=="off":
                    #search previous same note on and fill the gaps with on
                    count=(indexTimeline-1)
                    gapsTofill=True
                    Ton=t
                    Ton[0]="on"
                    while gapsTofill:
                        for g in timeline[count]:
                            #for each existing note in past step
                            if g[1]==t[1] and g[0]=="on":
                                #if its the same note and has the on attribute, we reached our destiny
                                gapsTofill=False
                                break
                        
                        if gapsTofill:
                            #ok, no same note found in prev step, let's create it with note on
                            timeline[count].append(Ton)
                           
                        count-=1
                
                #if t[0]=="off":
                #    pass
                """
                lastT=timeline[-1]
                for s in lastT:
                    #modify each note that matches in the last step
                    if s[0]=="on" and t[0]!="off":
                        
                        timeline[indexTimeline].append(t)
                        
                """
                   
                
                
                
                
                if t[1] not in self.notes:
                    print "CREATING NOTES"
                    closestNote=self.findClosestNote(preNotes,t[1])
                    closestNoteFilename="samplers/"+self.samplerFolder+"/"+str(closestNote)+".wav"

                    #sound=AudioSegment.from_file(closestNoteFilename)
                    self.soxPitch(closestNoteFilename,"samplers/"+self.samplerFolder+"/"+str(t[1])+".wav",closestNote,t[1])
                    
                    self.notes.append(t[1])
                    self.sounds.append(pygame.mixer.Sound("samplers/"+self.samplerFolder+"/"+str(t[1])+".wav"))
                    """
                    notePitched=self.changePitch(sound,closestNote,t[1])
                    notePitched.export("samplers/"+self.samplerFolder+"/"+str(t[1])+".wav",format="wav",parameters=["-acodec", "pcm_s16le", "-ac", "1"])
                    self.notes.append(t[1])
                    self.sounds.append(pygame.mixer.Sound("samplers/"+self.samplerFolder+"/"+str(t[1])+".wav"))
                    """
        
      
        
      
        #print timeline
        #print "firstStep ",firstStep
        return timeline
    
    def soxPitch(self,inputFile,destinationFile,originPitch,destinationPitch):
        
        pitchChange=((destinationPitch-originPitch)*100)
  
        #tempoChange=float(destinationPitch-originPitch)/24
        #shell='sox "'+inputFile+'" "'+destinationFile+'" pitch '+str(pitchChange)+' tempo '+str(tempoChange)
        #command=['sox', '"'+inputFile+'"', '"'+destinationFile+'"', 'speed', str(pitchChange)+'c']  
        command='sox "'+inputFile+'" "'+destinationFile+'" speed '+str(pitchChange)+'c'
        print command
        #command="ls"
        #os.system(command)
        #time.sleep(2)
        prog = subprocess.call(command,shell=True)#, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
        #out, err = prog.communicate()
        #process = subprocess.call(command)#,shell=True)
        #process.wait()
        
        #create copy of image too
        originImage=inputFile.split(".")[0]+".jpg"
        destinationImage=destinationFile.split(".")[0]+".jpg"
        copyfile(originImage, destinationImage)
        self.imgs.append( cv2.imread(destinationImage))
        return True#process.returncode
  
    def getStepIndex(self,dt,totalSteps,totalTime):
        
        #print "dt,totalSteps,totalTime",dt,totalSteps,totalTime
        return int((totalSteps*dt)/totalTime)
    
    def dump(self,obj):
        for attr in dir(obj):
          print "obj.%s = %s" % (attr, getattr(obj, attr))
    
    def playSong(self,filename):
        
        #filename="visa.kar"
        #filename="mammamia.KAR"
        #filename="barbiegirl.kar"
        trackNumber=self.midiTrackToSampler
        
        #get the real duration of the song
        mid = MidiFile(filename)
        songDuration=mid.length
        
        m=midifile.midifile()
        samplerTrack=m.load_file(filename,trackNumber)
        
        
        pygame.mixer.init()#frequency=22050, size=-16, channels=2 ,buffer=44100)
        
        self.loadSampler()
        self.loadImagesSampler()
        
        splrPartiture=self.constructSamplerTrack(samplerTrack,songDuration)#max(m.kartimes))
        time.sleep(2)
        #pygame.mixer.music.load(filename)
        #pygame.mixer.music.play(0,0) # Start song at 0 and don't loop
        start=datetime.datetime.now()
        
        """
        for n in samplerTrack:
            if int(n[1]) not in self.notes:
                self.sounds.append(self.prepareNextNote(int(n[1])))
                self.notes.append(int(n[1]))
        """
        """
        noteCounter=0
        nextNote=samplerTrack[noteCounter][0]
        nextNoteTime=round(samplerTrack[noteCounter][2],1)
        nextNoteSound=self.prepareNextNote(nextNote)
        """
        #print ("nextNoteTime",nextNoteTime)
        #print ("nextNote",nextNote)
        
        #SplrCounter=17#220#int(self.division*1.6) #la ventaja que lleva #old 17 con 0.1 de sleep
        #print("ventaja",SplrCounter)
        
      
        dt=0.
        totalTime=songDuration#max(m.kartimes)
        totalSteps=len(splrPartiture)
        #sleepTime=1.0
        #for times in range(self.resolution):
        #    sleepTime=sleepTime/10.0
        #sleepTime=0.001
        #sleepTime=float(1.0/self.division)
        #while True:
        
        lastPlayingNotes=[]
        lastPlayingNotesNames=[]
        
        playDelay=1.7
        img=self.lastImage
        
        
        #while True:
        with mido.open_output("TiMidity:TiMidity port 0 129:0") as output:
        #while pygame.mixer.music.get_busy():
            
            for message in MidiFile(filename).play():
                
                dt=(datetime.datetime.now()-start).total_seconds()
                m.update_karaoke(dt)
                dtRound=round(dt,self.resolution)

                #the playing note part        
                #print (max(m.kartimes)*division)
                #print "splcounter",SplrCounter
                #print "SplrCounter time check",(((max(m.kartimes))*self.division)/SplrCounter)


                stepIndex=self.getStepIndex((dt+playDelay),totalSteps,totalTime)
                currentNotes=splrPartiture[stepIndex]
                #print stepIndex
                nowNoteNames=[]
                
                if message.type=="note_on":
                    self.dump(message)
                    print("..")
                
                if message.type=="note_on" and message.channel==self.midiTrackToSampler:
                    soundIndex=self.notes.index(message.note)
                    
                    self.sounds[soundIndex].play()
                output.send(message)
                
                """

                for cn in currentNotes:
                    if cn[0]=="on":
                        nowNoteNames.append(cn[1])

                    if cn[1] not in lastPlayingNotesNames and cn[0]=="on":
                        soundIndex=self.notes.index(cn[1])

                        self.sounds[soundIndex].play()
                        img=self.imgs[soundIndex]


                for n in lastPlayingNotes:
                    if n[1] not in nowNoteNames and n[0]=="on":
                        playingSoundIndex=self.notes.index(n[1])
                        #self.sounds[playingSoundIndex].stop()

                        
                lastPlayingNotesNames=nowNoteNames
                lastPlayingNotes=currentNotes
                
                """

                #print ''
                #print 't=',dtRound,' of ',songDuration#max(m.kartimes)

                imgText=""

                for iline in range(3):
                    imgText+=m.karlinea[iline]
                    imgText+='__'+m.karlineb[iline]+'\n'
                #print ''
                
                """
                #display images
                imgCtext=img.copy()
                y0, dy = 50, 30
                for i, line in enumerate(imgText.split('\n')):
                    y = y0 + i*dy
                    cv2.putText(imgCtext,line, (10,y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),1)
                    
                cv2.imshow(self.windowName,imgCtext)
                if cv2.waitKey(1) == 27:
                    self.singing=False
                    break  # esc to quit

                self.opencvReady=True

                """

                """
                if dtRound== nextNoteTime:
                    for n in nextNotesounds:
                        play(n)
                    nCounter+=1
                    print "PLAY NOTE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                """

            

            #time.sleep(0.01)#sleepTime)
            
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
        
        #print("originpitch",originpitch,"destinationpitch",destinationpitch,"factor",factor)
        """
        npSound= self.pitchshift(sound,transS)
        
        audio_segment = pydub.AudioSegment(
            npSound.tobytes(), 
            frame_rate=44100,
            sample_width=npSound.dtype.itemsize, 
            channels=1
        )
        return audio_segment
        """
        
        #TODO:calculate octaves based on origin pitch and destination pitch
        """
        
        if destinationpitch>originpitch:
            adaptedPitch = ((destinationpitch-originpitch)/12)+1
        else:
            adaptedPitch = ((originpitch-destinationpitch)/12)-1
        """
        """
        mult=0.08334
        
        if destinationpitch>originpitch:
            adaptedPitch = ((float(destinationpitch)-float(originpitch)))*mult
        else:
            adaptedPitch = ((float(originpitch)-float(destinationpitch)))*mult
        
        """
        
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
        


#sound = AudioSegment.from_file('samplers/3/63_1.wav')
# shift the pitch up by half an octave (speed will increase proportionally)




#for i in range(50):   
    #play(chipmunk_ready_to_export )
    

if __name__ == "__main__":
    K=samplerPlayer("karaoke")
    #K.playSong("bellabestia.kar")
    K.playSong("mammamia.KAR")