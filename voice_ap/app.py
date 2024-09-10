#import flask libary and class
from flask import Flask, render_template, send_file 
#allows for interaction with APIs
import requests
import json
#used for audion recording and playback
import pyaudio
#used to manipulate the audio file
import pydub
import os

#creating flask instance
app = Flask(__name__)
#creating v for audio dir where audio files will be stored
AUDIO_DIR = 'audio'
#creating base dir action

@app.route("/")
def index():
	print("This is a voice application")
	#getting a list of audio files
	audio_files = [f for f in os.listdir(AUDIO_DIR) if f.endswith('.wav')]
	return render_template('index.html', audio_files=audio_files)

#creating dir to play audio
@app.route('/play/<filename>')
def play_audio(filename):
	#sending file to screen
	return send_file(os.path.join(AUDIO_DIR, filename))

if __name__ == '__main__':
	app.run(debug = True, host="0.0.0.0", port=8080)

