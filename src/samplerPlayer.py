# encoding=utf8  
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
import pydub
from pydub import AudioSegment
from pydub.playback import play
import time, datetime
from tools import midifile
import pygame
from os.path import basename
import glob,os
import threading
import numpy as np


class samplerPlayer():
    
    preparedSounds=[]
    
    
    def __init__(self):
        print ("sampler Player init")
        self.samplerFolder="2"
        self.resolution=1
        
    
    def loadSampler(self):
        
        
        self.sounds=[]
        self.notes=[]
        for file in glob.glob("samplers/"+self.samplerFolder+"/*.wav"):
            self.sounds.append(pygame.mixer.Sound(file))#AudioSegment.from_file(file))
            self.notes.append(int(os.path.splitext(basename(file))[0].split("_")[0]))
            
        #print self.notes
        #print self.sounds
        
    
    def findClosestNote(self,notes,note):
        
        closestNoteIndex=0
        closestDistance=999999999
        closesNote=0
        
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
        
        division=1
        for times in range(self.resolution):
            division=division*10
        
        self.division=division
        #division=(for t in self.resolution)#10
        
        TT=round(totaltime,self.resolution)
        timesteps=int(TT*division)
        print("timesteps",timesteps)
        #create empty list of lists for each time step
        timeline=[[] for i in range(timesteps)]
        
        for t in samplerTrack: #parse all notes
            
            #indexTimeline=int(timesteps/(round(t[2],1)))
            indexTimeline=int(round(t[2],self.resolution)*division)
            
            
            if indexTimeline<timesteps:
                #print ("indexTimeline",indexTimeline)
                #print((round(t[2],1)),timesteps,indexTimeline)
                #print("indexTimeline",indexTimeline)
                timeline[indexTimeline].append(t)
                if t[0] not in self.notes:
                    closestNote=self.findClosestNote(self.notes,t[0])
                    closestNoteFilename="samplers/"+self.samplerFolder+"/"+str(closestNote)+".wav"

                    sound=AudioSegment.from_file(closestNoteFilename)
                    notePitched=self.changePitch(sound,closestNote,t[0])
                    notePitched.export("samplers/"+self.samplerFolder+"/"+str(t[0])+".wav",format="wav")
                    self.notes.append(t[0])
                    self.sounds.append(pygame.mixer.Sound("samplers/"+self.samplerFolder+"/"+str(t[0])+".wav"))
            
        
      
        #print timeline
        return timeline
  

    
    def playSong(self):
        
        #filename="visa.kar"
        filename="mammamia.KAR"
        #filename="barbiegirl.kar"
        
        m=midifile.midifile()
        samplerTrack=m.load_file(filename)
        
        
        pygame.mixer.init()
        
        self.loadSampler()
        splrPartiture=self.constructSamplerTrack(samplerTrack,max(m.kartimes))
        
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(0,0) # Start song at 0 and don't loop
        start=datetime.datetime.now()
        
        
        for n in samplerTrack:
            if int(n[0]) not in self.notes:
                self.sounds.append(self.prepareNextNote(int(n[0])))
                self.notes.append(int(n[0]))
        
        """
        noteCounter=0
        nextNote=samplerTrack[noteCounter][0]
        nextNoteTime=round(samplerTrack[noteCounter][2],1)
        nextNoteSound=self.prepareNextNote(nextNote)
        """
        #print ("nextNoteTime",nextNoteTime)
        #print ("nextNote",nextNote)
        
        SplrCounter=17#220#int(self.division*1.6) #la ventaja que lleva #old 17 con 0.1 de sleep
        print("ventaja",SplrCounter)
        
      
        dt=0.
        sleepTime=1.0
        for times in range(self.resolution):
            sleepTime=sleepTime/10.0
        #sleepTime=0.001
        #sleepTime=float(1.0/self.division)
        #while True:
        while pygame.mixer.music.get_busy():
            
            dt=(datetime.datetime.now()-start).total_seconds()
            m.update_karaoke(dt)
            dtRound=round(dt,self.resolution)
            
            #the playing note part        
            #print (max(m.kartimes)*division)
            print "splcounter",SplrCounter
            #print "SplrCounter time check",(((max(m.kartimes))*self.division)/SplrCounter)
            currentNotes=splrPartiture[SplrCounter]
            #print (currentNotes)
            
            for cn in currentNotes:
                print cn
                soundIndex=self.notes.index(cn[0])
                self.sounds[soundIndex].play()
                
                
                #t = threading.Thread(target=self.playSound, args = (soundIndex,))
                #t.start()
                #self.playSound(soundIndex)
                #play(self.sounds[soundIndex])
                #print "playy "
            #print SplrCounter
            
            SplrCounter+=1
            
            """
            if dtRound== nextNoteTime:
                for n in nextNotesounds:
                    play(n)
                nCounter+=1
                print "PLAY NOTE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            """
            print ''
            print 't=',dtRound,' of ',max(m.kartimes)
            for iline in range(3):
                print m.karlinea[iline]+'__'+m.karlineb[iline]
            print ''
            

            time.sleep(sleepTime)
    
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
        
        print("originpitch",originpitch,"destinationpitch",destinationpitch,"factor",factor)
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
    K=samplerPlayer()
    K.playSong()