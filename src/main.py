# encoding=utf8  
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
import webbrowser
from samplerPlayer import samplerPlayer
from karaokesampler import karaokesampler
from tools.GUIutils import GUIutils
import json
import cv2
import threading
from time import sleep

from flask import Flask, url_for, render_template, jsonify, request, make_response

utils=GUIutils()

windowName="karaoke"

server = Flask(__name__, static_folder='guistatic', static_url_path='')
server.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1  # disable caching
server.config['JSON_AS_ASCII'] = False

S=samplerPlayer(windowName)
K=karaokesampler()

@server.route("/")
def init():
	return server.send_static_file('index.html')

@server.route("/createproject", methods=['GET','POST'])
def login():
	if request.method == 'POST':
		do_the_login()
	else:
		show_the_login_form()

@server.route("/getkarsongs")
def getkarsongs():
	#load song list
	songList=utils.getSongList()
	#print songList
	return json.dumps(songList,encoding='latin1')

@server.route("/getsamplers")
def getsamplers():
	#load samplerList
	samplerList=utils.getSamplerList()
	#print samplerList
	return json.dumps(samplerList)


@server.route("/loadsong",methods=['POST'])
def loadsong():
	customText=request.json["customtext"]
	filename = utils.songsFolder+"/"+request.json["filename"]
	songpath= request.json["songpath"]
	samplerName = request.json["samplerName"]
	print filename,"!!!!!!!!!!!!!!!!!	"
	S.playSong(str(filename),songpath,int(samplerName),customText)
	print "SONG FINISHED"
	K.singing=False
	return "OK"

@server.route("/songloaded")
def songloaded():
	if S.status=="ready":
		return "loaded"
	else:
		return "notloaded"

@server.route("/playsong")
def playsong():
	S.status="playing"

	#start recorder
	K.recordKaraoke()

	return "recorded"

@server.route("/stopsong")
def stopsong():
	K.singing=False
	S.status="stop"
	S.img=S.createBlackImage()
	return "stoped"

	
#def loadSong():
#	K.playSong("entregate.KAR",12)

def run_server():
	server.run(host="127.0.0.1", port=23948, threaded=True)

def statusWatcher(threadName):

	lastState=S.status

	while True:
		if S.status !=lastState:
			#status change!
			lastState=S.status
			if S.status=="ready":

				print "SONG IS LOADED!!!!!!!!!!!!!!!!"


		sleep(1)

if __name__ == "__main__":
	t = threading.Thread(target=statusWatcher, args = ("statusthread",)) #algo entre 0.1 y 0.8
	t.start()
	webbrowser.open("http://127.0.0.1:23948")

	
	#cv2.imshow(windowName,lastImage)
	
	

	run_server()



