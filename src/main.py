# -*- coding: utf-8 -*- 


# karaoke sampler v.1.0


import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')



#reload(sys)  
#sys.setdefaultencoding('utf8')
import webbrowser
from samplerPlayer import samplerPlayer
from karaokesampler import karaokesampler
from tools.GUIutils import GUIutils
import json
import cv2
import threading
from time import sleep
import logging
from datetime import timedelta  
from functools import update_wrapper
from flask import Flask, url_for, render_template, jsonify, request, make_response, current_app 

utils=GUIutils()

windowName="karaoke"

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
server = Flask(__name__, static_folder='guistatic', static_url_path='')
server.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1  # disable caching
server.config['JSON_AS_ASCII'] = False

S=samplerPlayer(windowName)
K=karaokesampler(S)

def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):  
	try:
		basestring
	except:
		basestring = str
	if methods is not None:
		methods = ', '.join(sorted(x.upper() for x in methods))
	if headers is not None and not isinstance(headers, basestring):
		headers = ', '.join(x.upper() for x in headers)
	if not isinstance(origin, basestring):
		origin = ', '.join(origin)
	if isinstance(max_age, timedelta):
		max_age = max_age.total_seconds()

	def get_methods():
		if methods is not None:
			return methods

		options_resp = current_app.make_default_options_response()
		return options_resp.headers['allow']

	def decorator(f):
		def wrapped_function(*args, **kwargs):
			if automatic_options and request.method == 'OPTIONS':
				resp = current_app.make_default_options_response()
			else:
				resp = make_response(f(*args, **kwargs))
			if not attach_to_all and request.method != 'OPTIONS':
				return resp

			h = resp.headers

			h['Access-Control-Allow-Origin'] = origin
			h['Access-Control-Allow-Methods'] = get_methods()
			h['Access-Control-Max-Age'] = str(max_age)
			if headers is not None:
				h['Access-Control-Allow-Headers'] = headers
			return resp

		f.provide_automatic_options = False
		return update_wrapper(wrapped_function, f)
	return decorator

@server.route("/")
@crossdomain(origin='*')
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
	return json.dumps(songList)#,encoding='latin1')

@server.route("/getsamplers")
def getsamplers():
	#load samplerList
	samplerList=utils.getSamplerList()
	print ("samplerList",samplerList)
	return json.dumps(samplerList)


@server.route("/loadsong",methods=['POST'])
def loadsong():
	customText=request.json["customtext"]
	filename = utils.songsFolder+"/"+request.json["filename"]
	songpath= request.json["songpath"]
	samplerName = request.json["samplerName"]
	print("samplerName",samplerName)
	if samplerName=="":
		samplerName=False
	#print("QUICK FIX FOR SAMPLER NAME, FIX THIS")
	#samplerName=False
	#print songpath,"songpath"
	#print filename,"!!!!!!!!!!!!!!!!!	"
	S.playSong(str(filename),songpath,int(samplerName),customText)
	#print "SONG FINISHED"
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

@server.route("/pausesong")
def pausesong():
	K.singing=False
	S.status="pause"
	
	return "paused"

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

				print ("SONG IS LOADED!!!!!!!!!!!!!!!!")


		sleep(1)

if __name__ == "__main__":
	t = threading.Thread(target=statusWatcher, args = ("statusthread",)) #algo entre 0.1 y 0.8
	t.start()
	webbrowser.open("http://127.0.0.1:23948")

	
	#cv2.imshow(windowName,lastImage)
	
	

	run_server()



