import aubio
import cv2
import math
import numpy as np
import pyaudio
from synth import synth
from time import sleep
import wave
import struct
import audioop

class karaokesampler():
    
    #config
    Vdevice = 0
    synth = False
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
    volume=5
    checkingVolume=False
    
    amountToAvergeVolume=2
    averageCounter=0
    lastVolumes=[]
    paint="graph" #none,graph
    
    graph = []
    
    #finished_threads=[]
    #event = threading.Event()
    
    def __init__(self):
        
        print("init karaokesampler")
        self.createNoteTargets()
        self.p = pyaudio.PyAudio()
        
        self.cap = cv2.VideoCapture(self.Vdevice)
        self.capW = int(self.cap.get(3))
        self.capH = int(self.cap.get(4))
        
        for i in range(self.amountToAvergeVolume+1):
            self.lastVolumes.append(0)

        #init window
        #ret_val, img = self.cap.read()
        #cv2.imshow(self.windowName, img)
        
    
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
        """
        thisthread = threading.current_thread()
        self.finished_threads.append(thisthread)
        if len(self.finished_threads) > 1 and self.finished_threads[1] == thisthread:
            #yay we are number two!
            self.checkingVolume=False
            self.event.set()
        """
            
    
    def get_rms(self, block ):
        SHORT_NORMALIZE = (0.00003051757)
        # RMS amplitude is defined as the square root of the 
        # mean over time of the square of the amplitude.
        # so we need to convert this string of bytes into 
        # a string of 16-bit samples...

        # we will get one short out for each 
        # two chars in the string.
        count = len(block)/2
        format = "%dh"%(count)
        shorts = struct.unpack( format, block )

        # iterate over the block.
        sum_squares = 0.0
        for sample in shorts:
            # sample is a signed short in +/- 32768. 
            # normalize it to 1.0
            n = sample * SHORT_NORMALIZE
            sum_squares += n*n

        return math.sqrt( sum_squares / count )
    
    def singKaraoke(self):
        
        if self.synth:
            print("SYNTH ENABLED")
        
        # open stream
        """
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
        #filename = self.recordingsFolder + "test.wav"
        #outputsink = aubio.sink(filename, samplerate)

        # setup pitch
        
        tolerance = 0.8
        win_s = 4096 # fft size
        hop_s = buffer_size # hop size
        pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
        pitch_o.set_unit("midi")
        pitch_o.set_tolerance(tolerance)
        
        print("*** starting recording")

        pitch = 0
        """
        
        # Some constants for setting the PyAudio and the
        # Aubio.
        BUFFER_SIZE             = 2048
        CHANNELS                = 1
        FORMAT                  = pyaudio.paFloat32
        METHOD                  = "default"
        SAMPLE_RATE             = 44100
        HOP_SIZE                = BUFFER_SIZE//2
        PERIOD_SIZE_IN_FRAME    = HOP_SIZE

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
        
        while True:
            #image
            ret_val, originalImage = self.cap.read()
            img = originalImage.copy()
            
            if self.paint=="graph":
                img=self.drawNoteTargets(img)
            
            #audio
            # Always listening to the microphone.
            data = mic.read(PERIOD_SIZE_IN_FRAME)
            # Convert into number that Aubio understand.
            samples = np.fromstring(data,
                dtype=aubio.float_type)
            # Finally get the pitch.
            pitch = pDetection(samples)[0]
            # Compute the energy (volume)
            # of the current frame.
            volume = np.sum(samples**2)/len(samples)
            # Format the volume output so it only
            # displays at most six numbers behind 0.
            vol=("{:6f}".format(volume))
            print(str(pitch) + " " + str(vol))
            confidence=1
            """
            audiobuffer = stream.read(buffer_size)
            signal = np.fromstring(audiobuffer, dtype=np.float32)
            """
            #volume = np.sum(signal ** 2) / len(signal)
            
            """
            self.lastVolumes[self.averageCounter]=volume
            self.averageCounter+=1
            if self.averageCounter>self.amountToAvergeVolume:
                self.averageCounter=0
            """
            
            #volume=np.average(self.lastVolumes)
            #volume = self.get_rms( audiobuffer )
            #print(volume)
            #self.volume = np.sum(signal ** 2) / len(signal)
            #self.volume=audioop.max(signal, 4)
            #self.volume =( audioop.rms(audiobuffer, 2))
            #self.volume=(self.remap(self.volume, 11904, 1800, 0.0, self.capH))
            
            #outputsink(signal, len(signal))
           
            #print("{:10.4f}".format(energy))
            
            #self.calculateVolume(CHUNK,audiobuffer)
            #if not self.checkingVolume:
                #threading.Thread(target=self.calculateVolume, args = (CHUNK,audiobuffer)).start()
                #t = threading.Thread(target=self.calculateVolume, args = (CHUNK,audiobuffer))
                #t.start()
            #data=stream.read(CHUNK)
            #rms = audioop.rms(data,2)
            #rms=self.rms(signal)
            #print rms
            #print (self.volume)
            #volume=self.volume
            #pitch Value
            #pitch = pitch_o(signal)[0]
            #confidence = pitch_o.get_confidence()
            """
            if confidence > self.lastPitchConfidence:
                self.lastPitch = pitch
                self.lastPitchConfidence = confidence
            else:
                pitch = self.lastPitch
            """
            if volume > self.lowCut and pitch>self.lowToneCut:
                
                #record if match
                """
                if int(pitch) in self.noteTargets:
                    if not self.isrecording:
                        #start recording
                        print ("started recording")
                        self.recordings.append(str(int(pitch))+"_"+str(len(self.recordings)))
                        filename = self.recordingsFolder + str(int(pitch))+"_"+str(len(self.recordings))+".wav"
                        outputsink = aubio.sink(filename, samplerate)
                        self.isrecording=True
                    else:
                        print("#keep recording")
                        if outputsink:
                            pass
                            outputsink(signal, len(signal))
                else:
                   if self.isrecording:
                       self.isrecording=False
                       #print("#stop recording")
                       outputsink.close()
                """
                
                #end record if match
                """
                volH = int(self.remap(volume, 0.0, 1.0, 0.0, self.capH))
                #print (volH)
                lineV1 = (200, volH)
                lineV2 = (400, volH)
                if self.paint=="graph":
                    cv2.line(img, lineV1, lineV2, [255, 0, 255], 2)
                
                #   pitch
                pitchH = int(self.remap(pitch, self.pitchGL, self.pitchGH, 0.0, self.capH))
                #print pitchH
                lineP1 = (500, pitchH)
                lineP2 = (700, pitchH)
                if self.paint=="graph":
                    cv2.line(img, lineP1, lineP2, [255, 255, 255], 3)
                """
                
                
                #if self.synth:
                    #synthPitch = pitch
                    #print ("synthPitch", synthPitch)
                    #self.S.modulateSynth(volume,pitch)
            
            
            #self.S.out()
            self.lastPitch = 0
            self.lastPitchConfidence = 0
            
            #if pitch > 0:
            #    stream.write(self.generateTone(pitch))
            
            #cv2.imshow(self.windowName, img)
            #if cv2.waitKey(1) == 27: 
            #    break  # esc to quit
        
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
    
