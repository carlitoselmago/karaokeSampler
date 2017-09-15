stepsss=[1,2,3,4,5,6,7,8,9,11,12,13,20]

lastSylab=0
for lyricMessageCount in stepsss:
	if lyricMessageCount-lastSylab>1:
		#we missed a step reproduce both
		#print "we missed some!"
		steps=[]
		for s in range(lyricMessageCount-lastSylab):
			
			steps.append((lastSylab+s)+1)
	else:
		steps=[lyricMessageCount]

	for s in steps:
		print "STEP",s
	lastSylab=s