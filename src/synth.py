from pyo import *
from time import sleep

class synth():
    
    def __init__(self):
        print("init synth")
        self.initSynth()
        
        
        
    def initSynth(self):
    
        #SYNTH ::::::::::::::::::::::::::::::::

        # Roland JP-8000 Supersaw emulator.
        freq = 100

        self.s = Server(duplex=0)
        #s.setInOutDevice(1)
        self.s.boot()

        self.synths=[]

        #1

        lfo2 = Sine(freq=freq).range(0.8, 0.8)
        self.synths.append( SuperSaw(freq=freq, detune=lfo2, mul=0.2))
        self.synths[0].mul=0
        
        #2

        lfo = Sine(freq=freq).range(0.1, 0.1)
        lfoo = Sine(freq=.25, mul=3, add=10)
        #osc = SuperSaw(freq=freq, detune=lfo4, mul=0.2)
        self.synths.append( Blit(freq=[100, 99.7]*lfoo, harms=lfoo, mul=.3).out())
        self.synths[1].mul=0

        fxs=[]
        self.mm = Mixer(outs=2, chnls=len(self.synths), time=.025)

        for i,synth in enumerate(self.synths):
            #fxs.append(Freeverb(mm[i], size=.8, damp=.8, mul=.5).out())
            fxs.append(Delay(self.synths[i], delay=[.8,.8], feedback=.8, mul=1).out())
            self.mm.addInput(i,synth)
            self.mm.setAmp(i,1,.5)

        self.s.start()
        
        #self.modulateSynth(1,45)
        return self
    
    def out(self):
        self.mm.out()
        
        return self
    
    def modulateSynth(self,vol,tone):
        #vol=1.0
        #tone=66.572433
        self.synths[0].mul=float(vol)
        self.synths[0].freq=float(tone)
        return self
        

