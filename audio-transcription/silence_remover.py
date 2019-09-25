import librosa

def remove_silence(file_name):
	sample_file = file_name+'.wav'
	y, sr = librosa.load(sample_file)
	y_trimmed, index = librosa.effects.trim(y, top_db=12, frame_length=2)
	print(librosa.get_duration(y), librosa.get_duration(y_trimmed))
	destination = sample_file[:-4] + '.wav'
	librosa.output.write_wav(destination, y_trimmed, sr)