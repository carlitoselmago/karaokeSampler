import aubio
import cv2
import math
import numpy as np
import pyaudio
from synth import synth
from time import sleep
import wave

class karaokesampler():
    
    #config
    Vdevice = 1
    synth = True
    #end config
    windowName = "karaoke"

    recordingsFolder = "recordings/"
    
    lowCut = 0.05 #volumen
    lowToneCut=10 #pitch
    capW = 0
    capH = 0
    
    pitchGL=30
    pitchGH=80
    
    lastPitch = 0
    lastPitchConfidence = 0
    
    noteTargets=[] #the notes we are gonna try to record
    recordings=[]
    isrecording=False
    
    graph = []
    
    def __init__(self):
        
        print("init karaokesampler")
        self.createNoteTargets()
        self.p = pyaudio.PyAudio()
        
        self.cap = cv2.VideoCapture(self.Vdevice)
        self.capW = int(self.cap.get(3))
        self.capH = int(self.cap.get(4))
        
        

        #init window
        ret_val, img = self.cap.read()
        cv2.imshow(self.windowName, img)
        
    
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
        NewValue = (((value - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
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
            print "Input Device id ", i, " - ", self.p.get_device_info_by_host_api_device_index(0, i).get('name')
    
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
    
    def singKaraoke(self):
        
        if self.synth:
            print("SYNTH ENABLED")
        
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
                        
        #recorder
        filename = self.recordingsFolder + "test.wav"
        outputsink = aubio.sink(filename, samplerate)

        # setup pitch
        tolerance = 0.8
        win_s = 4096 # fft size
        hop_s = buffer_size # hop size
        pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
        pitch_o.set_unit("midi")
        pitch_o.set_tolerance(tolerance)
        
        print("*** starting recording")
        volume = 0
        pitch = 0
        while True:
            #image
            ret_val, originalImage = self.cap.read()
            img = originalImage.copy()
            
            img=self.drawNoteTargets(img)
            
            #audio
            audiobuffer = stream.read(buffer_size)
            signal = np.fromstring(audiobuffer, dtype=np.float32)
            volume = np.sum(signal ** 2) / len(signal)

           
            #print("{:10.4f}".format(energy))
            

            
            
            
            #for i in range(int(10*44100/buffer_size)): #go for a few seconds
            data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
            peak = np.average(np.abs(data)) * 2
            volume = (50 * peak / 2 ** 16)
            volume = self.remap(volume, 12.0, 28.0, 0.0, 1.0)
            
            #pitch Value
            pitch = pitch_o(signal)[0]
            confidence = pitch_o.get_confidence()

            if confidence > self.lastPitchConfidence:
                self.lastPitch = pitch
                self.lastPitchConfidence = confidence
            else:
                pitch = self.lastPitch
            outputsink(signal, len(signal))
            if volume > self.lowCut and pitch>self.lowToneCut:
                
                #record if match
                
                
                if int(pitch) in self.noteTargets:
                    if not self.isrecording:
                        #start recording
                        print ("started recording")
                        self.recordings.append(str(int(pitch))+"_"+str(len(self.recordings)))
                        filename = self.recordingsFolder + str(int(pitch))+"_"+str(len(self.recordings))+".wav"
                        #outputsink = aubio.sink(filename, samplerate)
                        self.isrecording=True
                    else:
                        print("#keep recording")
                        if outputsink:
                            pass
                            #outputsink(signal, len(signal))
                else:
                   if self.isrecording:
                       self.isrecording=False
                       print("#stop recording")
                       #outputsink.close()
  
                
                #end record if match
         
                volH = int(self.remap(volume, 0.0, 1.0, 0.0, self.capH))
                #print (volH)
                lineV1 = (200, volH)
                lineV2 = (400, volH)
                cv2.line(img, lineV1, lineV2, [255, 0, 255], 2)
                
                #   pitch
                pitchH = int(self.remap(pitch, self.pitchGL, self.pitchGH, 0.0, self.capH))
                #print pitchH
                lineP1 = (500, pitchH)
                lineP2 = (700, pitchH)

                cv2.line(img, lineP1, lineP2, [255, 255, 255], 3)
                
                #if self.synth:
                    #synthPitch = pitch
                    #print ("synthPitch", synthPitch)
                    #self.S.modulateSynth(volume,pitch)
                    #sleep(0.01)
            
            if self.synth:
                #self.S.modulateSynth(0,0)
                pass
            
            #self.S.out()
            self.lastPitch = 0
            self.lastPitchConfidence = 0
            
            #if pitch > 0:
            #    stream.write(self.generateTone(pitch))
            
            cv2.imshow(self.windowName, img)
            if cv2.waitKey(1) == 27: 
                break  # esc to quit
        
        print("*** done recording")
        print (self.recordings)
        stream.stop_stream()
        stream.close()
        self.p.terminate()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    
    
    k = karaokesampler()
    #k.getAudioDevies()
    
    k.singKaraoke()
    
