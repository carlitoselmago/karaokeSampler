#!/usr/bin/env python
"""                                                                            
Play MIDI file on output port.
Run with (for example):
	./play_midi_file.py 'SH-201 MIDI 1' 'test.mid'
"""

import sys
import mido
from mido import MidiFile
from time import sleep
from pprint import pprint

#os.system("timidity -iA -B2,8 -Os -EFreverb=0")
#sleep(2)
#mido.set_backend('mido.backends.portmidi')
print mido.get_output_names()
filename ="mammamia.KAR"


#Microsoft GS Wavetable Synth 0
with mido.open_output("loopMIDI Port 1") as output:
	try:
		for message in MidiFile(filename).play():
			#pprint(dir(message))
			#print(message.dict)
			if message.channel==0:
				print message
			#print(message.bytes)
			#print (mido.Message.from_bytes(message.bytes))
			#print(message.bin)
			#output.send(message)
			
	except KeyboardInterrupt:
		print()
		output.reset()