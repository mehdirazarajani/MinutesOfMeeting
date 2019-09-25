import speech_recognition as sr
import librosa as lb
import wavio as wv

def transcript_generator(file_names,technique):
	transcript={}
	for i in file_names:
		r = sr.Recognizer()
		filename=i+technique+".wav"
		y,s=lb.load(filename)
		wv.write(filename,y,s,sampwidth=2)
		with sr.AudioFile(filename) as source:
			audio_listened = r.listen(source)
		try:	 
			rec = r.recognize_google(audio_listened)
			transcript[i]=rec  
		
		# If google could not understand the audio 
		except sr.UnknownValueError: 
			print("Could not understand audio in "+filename) 

		# If the results cannot be requested from Google. 
		# Probably an internet connection error. 
		except sr.RequestError as e: 
			print("Could not request results.")
	fh=open("transcript"+technique+".txt","w+")
	for key in transcript:
		fh.write(transcript[key]+"\n")
	fh.close()
