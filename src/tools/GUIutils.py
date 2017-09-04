# encoding=utf8 
import os
import glob

class GUIutils():

	songsFolder="KARsongs"
	samplerFolder="samplers"

	def __init__(self):
		print "init GUI utils"

	def getSongList(self):
		songlist=[]
		for root, dirs, files in os.walk(self.songsFolder):
		    for file in files:
		        if file.endswith(".kar"):
		            songlist.append(os.path.splitext(file)[0].decode('unicode_escape').encode('utf-8'))

		return songlist

	def getSamplerList(self):
		samplerlist=[]
		for root, dirs, files in os.walk(self.samplerFolder):
			for dirName in dirs:
				try:
					samplerlist.append([dirName,self.getFirstImageInFolder(self.samplerFolder+"/"+dirName)])
				except:
					#folder corrupted
					pass

		return samplerlist

	def getFirstImageInFolder(self,folderURI):
		return glob.glob(folderURI+"/*.jpg")[0]
