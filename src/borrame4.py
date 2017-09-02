
import pygame
from pygame.locals import *
pygame.init()
(width, height) = (300, 200)
screen = pygame.display.set_mode((width, height))
pygame.display.flip()
from pygame.locals import *
#pygame.init()
from samplerPlayer import samplerPlayer

S=samplerPlayer("test")
S.prepareSampler()
print S.notes

done = False
pygame.mixer.set_num_channels(8)
voice = pygame.mixer.Channel(5)


while not done:


	for event in pygame.event.get():
		# any other key event input
		if event.type == QUIT:
			done = True
		"""        
		elif event.type == pygame.KEYDOWN:
			#if event.key == pygame.K_ESC:
			#    done = True
			if event.key == pygame.K_F1:
				print "hi world mode"
		"""
	# get key current state
	keys = pygame.key.get_pressed()
	if keys[pygame.K_SPACE]:
		#repeating fire while held
		note=66
		soundIndex=S.notes.index(note)
		#milisecondsOfDuration=int(message.time*10000)
		#print milisecondsOfDuration
		
		#S.sounds[soundIndex].play()
		if voice.get_busy():
			S.sounds[soundIndex].stop()
			print "is playing"
		voice.play(S.sounds[soundIndex],5,100)
		print "note"
		#fire() 