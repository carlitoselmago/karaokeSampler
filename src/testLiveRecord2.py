import time, numpy, pygame.mixer, pygame.sndarray
from scikits.samplerate import resample

pygame.mixer.init(44100,-16,2,4096)

# choose a file and make a sound object
sound_file = "tone.wav"
sound = pygame.mixer.Sound(sound_file)

# load the sound into an array
snd_array = pygame.sndarray.array(sound)

# resample. args: (target array, ratio, mode), outputs ratio * target array.
# this outputs a bunch of garbage and I don't know why.
#snd_resample = resample(snd_array, 1.5, "sinc_fastest")
snd_resample = resample(snd_array,3, "sinc_fastest").astype(snd_array.dtype)
# take the resampled array, make it an object and stop playing after 2 seconds.
snd_out = pygame.sndarray.make_sound(snd_resample)
snd_out.play()
time.sleep(2)