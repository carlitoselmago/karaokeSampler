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
	return json.dumps(songList)

@server.route("/getsamplers")
def getsamplers():
	#load samplerList
	samplerList=utils.getSamplerList()
	#print samplerList
	return json.dumps(samplerList)


@server.route("/loadsong",methods=['POST'])
def loadsong():
	filename = utils.songsFolder+"/"+request.json["filename"]
	samplerName = request.json["samplerName"]
	print filename,"!!!!!!!!!!!!!!!!!	"
	S.playSong(str(filename),int(samplerName))
	return "OK"

	
#def loadSong():
#	K.playSong("entregate.KAR",12)

def run_server():
	server.run(host="127.0.0.1", port=23948, threaded=True)




if __name__ == "__main__":
	
	webbrowser.open("http://127.0.0.1:23948")

	#cv2.namedWindow(windowName, cv2.WND_PROP_FULLSCREEN)          
	#cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	#cv2.imshow(windowName,lastImage)
	
	

	run_server()



