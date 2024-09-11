#import flask libary and and supporting classes
from flask import Flask, render_template, send_file, request as f_request, redirect, url_for, send_from_directory,jsonify 
#allows for interaction with APIs
import requests
import time
#used for audio recording and playback
import pyaudio
#used to manipulate the audio file
from pydub.playback import play
from pydub import AudioSegment
import numpy as np 
#allows to manipulate wave files
import wave
#allows for interaction with dir in os
import os

#creating flask instance
app = Flask(__name__)
#creating v for audio dir where audio files will be stored
AUDIO_DIR = 'audio'
app.config['AUDIO_DIR'] = AUDIO_DIR


#creating base dir action
@app.route("/")
def index():
	#getting a list of audio files
	audio_files = [f for f in os.listdir(AUDIO_DIR) if f.endswith('.wav')]
	return render_template('index.html', audio_files=audio_files)

#creating dir to upload already recorded audio
@app.route('/upload', methods = ['POST'])
def upload_audio():
	if 'audio_file' not in f_request.files:
		return "No Audio File Found"
	audio_file = f_request.files['audio_file']
	if audio_file.filename =='':
		return 'No Selected Audio File'
	if audio_file:
		audio_file.save(os.path.join(app.config['AUDIO_DIR'], audio_file.filename))
		return redirect(url_for('index'))

#creating dir to get recorded audio from 'audio'
@app.route('/audio/<filename>', methods = ['GET'])
def get_audio(filename):
	return send_from_directory(AUDIO_DIR, filename)

#creating new dir to change audio pitch
@app.route('/change_pitch/<filename>', methods = ['POST'])
def change_pitch(filename):
	if 'pitch_factor' not in f_request.form:
		return  "No Pitch Factor Provided"

	pitch_factor = float(f_request.form['pitch_factor'])

	audio_path = os.path.join(app.config['AUDIO_DIR'], filename)
	audio = AudioSegment.from_wav(audio_path)

	new_samp_rate = int(audio.frame_rate * (2.0 ** pitch_factor))
	pitch_shifted_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_samp_rate})
	pitch_shifted_audio = pitch_shifted_audio.set_frame_rate(audio.frame_rate)

	new_filename = f"pitch_shifted_{filename}"
	pitch_shifted_audio.export(os.path.join(app.config['AUDIO_DIR'], new_filename), format = "wav")

	return redirect(url_for('index'))

#creating dir to record an audio file
@app.route("/record", methods =['POST'])
def record_audio():
	#initialize PyAudio
	p_audio = pyaudio.PyAudio()
	data = f_request.get_json()
	filename = f_request.form["filename"] + ".wav"
	duration = int(f_request.form["duration"])
	sample_rate = 44100
	channels = 2
	chunk = 1024

	
	stream = p_audio.open(format=pyaudio.paInt16, channels=channels, rate=sample_rate, input=True, frames_per_buffer=chunk)
	frames = []

	print("* Recording audio... ")
	
	for i in range(0, int(sample_rate / chunk * duration)):
		data = stream.read(chunk)
		frames.append(data)

	stream.stop_stream()
	stream.close()
	p_audio.terminate()

	#save the WAV file
	wf = wave.open(os.path.join(AUDIO_DIR, filename), 'wb')
	wf.setnchannels(channels)
	wf.setsampwidth(p_audio.get_sample_size(pyaudio.paInt16))
	wf.setframerate(sample_rate)
	wf.writeframes(b''.join(frames))
	wf.close()

	print(f"* Done Recording: {filename}")
	print(f"* Audio saved as {filename}") 
	return redirect(url_for('index'))

#creating dir to play audio
@app.route('/play/<filename>')
def play_audio(filename):
	#sending file to screen
	return send_file(os.path.join(AUDIO_DIR, filename))

if __name__ == '__main__':
	if not os.path.exists(AUDIO_DIR):
	 	os.makedirs(AUDIO_DIR)
	app.run(debug=True, host="0.0.0.0", port=8080)

