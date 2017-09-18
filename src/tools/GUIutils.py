# -*- coding: utf-8 -*- 
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
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
				if file.endswith(".kar") or file.endswith(".KAR"):
					#songName=os.path.splitext(file)[0].decode('latin-1').encode("utf-8")#decode('unicode_escape').encode('utf-8')
					filename=root.replace("\\\\", "/")+"/"+file#os.path.join(root, file)
					filename=filename.replace("\\","/")
					songName=filename.split("/")[-1].replace(".kar","").replace(".KAR","")
					#print filename
					
					songlist.append([songName,filename])

		#print songlist
		return songlist

	def getSamplerList(self):
		samplerlist=[]
		for root, dirs, files in os.walk(self.samplerFolder):
			for dirName in sorted(dirs,key=int,reverse=True):
				try:
					samplerlist.append([dirName,self.getFirstImageInFolder(self.samplerFolder+"/"+dirName)])
				except:
					#folder corrupted
					pass

		return samplerlist

	def getFirstImageInFolder(self,folderURI):
		return glob.glob(folderURI+"/*.jpg")[0]
