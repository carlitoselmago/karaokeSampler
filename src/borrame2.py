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

#os.system("timidity -iA -B2,8 -Os -EFreverb=0")
#sleep(2)
#mido.set_backend('mido.backends.portmidi')
print mido.get_output_names()
filename ="mammamia.KAR"

with mido.open_output("TiMidity:TiMidity port 0 129:0") as output:
    try:
        for message in MidiFile(filename).play():
            print(message)
            output.send(message)
            
    except KeyboardInterrupt:
        print()
        output.reset()