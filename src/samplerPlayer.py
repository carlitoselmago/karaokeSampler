# encoding=utf8  
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
from pydub import AudioSegment
from pydub.playback import play
import time, datetime
from tools import midifile
import pygame
from os.path import basename
import glob,os
import threading


class samplerPlayer():
    
    preparedSounds=[]
    
    def __init__(self):
        print ("sampler Player init")
        
    def loadSampler(self):
        self.sounds=[]
        self.notes=[]
        for file in glob.glob("samplers/3/*.wav"):
            self.sounds.append(AudioSegment.from_file(file))
            self.notes.append(int(os.path.splitext(basename(file))[0].split("_")[0]))
            
        #print self.notes
        #print self.sounds
        
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
        
        if note>closesNote:
            adaptedPitch = ((note-closesNote)/12)+1
        else:
            adaptedPitch = ((closesNote-note)/12)-1
        notePitched=self.changePitch(closestNoteSound,adaptedPitch)
        return notePitched
        
    
    def constructSamplerTrack(self,samplerTrack,totaltime):
        
        TT=round(totaltime,1)
        timesteps=int(TT*10)
        #create empty list of lists for each time step
        timeline=[[] for i in range(timesteps)]
        
        for t in samplerTrack: #parse all notes
            
            
            
            indexTimeline=int(timesteps/(round(t[2],1)))
            #print((round(t[2],1)),timesteps,indexTimeline)
            #print("indexTimeline",indexTimeline)
            timeline[indexTimeline].append([t[0],t[1]])
            
        
        """
        for t in range(int(TT*10)):
            time=t/10.0
            if time in samplerTrack[2]:
                for 
        """
        print timeline
        return timeline
    
    """
    def getNextNote(self,nCounter):
        nextNote=samplerTrack[nCounter][0]
        nextNoteTime=round(samplerTrack[nCounter][2],1)
        aheadNoteTime=nextNoteTime
        nextNoteSounds=[]
        nAhead=nCounter
        while nextNoteTime==aheadNoteTime:
            aheadNoteTime=round(samplerTrack[nCounter][2],1)
            nextNoteSounds.append(XXXXX)
            nAhead+=1
    """
    
    def playSound(self,index):
        play(self.sounds[index])
        return
    
    def playSong(self):
        
        #filename="visa.kar"
        filename="mammamia.KAR"
        #filename="barbiegirl.kar"
        
        m=midifile.midifile()
        samplerTrack=m.load_file(filename)
        
        splrPartiture=self.constructSamplerTrack(samplerTrack,max(m.kartimes))
        
        pygame.mixer.init()
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
        
        SplrCounter=0
        
        
        dt=0.
        while pygame.mixer.music.get_busy():
            
            dt=(datetime.datetime.now()-start).total_seconds()
            m.update_karaoke(dt)
            
            #the playing note part
            dtRound=round(dt,1)
            currentNotes=splrPartiture[SplrCounter]
            print (currentNotes)
            """
            for cn in currentNotes:
                soundIndex=self.notes.index(cn[0])
                t = threading.Thread(target=self.playSound, args = (soundIndex,))
                t.start()
                #self.playSound(soundIndex)
                #play(self.sounds[soundIndex])
                #print "playy "
            #print SplrCounter
            """
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
            

            time.sleep(.1)
        
    
    def changePitch(self,sound,pitch):
        
        #TODO:calculate octaves based on origin pitch and destination pitch
        
        octaves = pitch #octaves is an int
        new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
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
    K.loadSampler()
    K.playSong()