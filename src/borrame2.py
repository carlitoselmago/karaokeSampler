#!/usr/bin/env python
"""                                                                            
Play MIDI file on output port.
Run with (for example):
    ./play_midi_file.py 'SH-201 MIDI 1' 'test.mid'
"""

import sys
import mido
from mido import MidiFile

#mido.set_backend('mido.backends.rtmidi')
print mido.get_output_names()
filename ="entregate.kar"

with mido.open_output("TiMidity:TiMidity port 1 129:1") as output:
    try:
        for message in MidiFile(filename).play():
            print(message)
            output.send(message)

    except KeyboardInterrupt:
        print()
        output.reset()