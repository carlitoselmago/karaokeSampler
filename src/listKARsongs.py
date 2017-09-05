from tools.GUIutils import GUIutils

utils=GUIutils()

songslistsfile = open('songs.txt', 'w')

#songslistsfile .write("\n".join(utils.getSongList()))

for song in utils.getSongList():
	songslistsfile.write("%s\n" % song[0])
	#print song[0]