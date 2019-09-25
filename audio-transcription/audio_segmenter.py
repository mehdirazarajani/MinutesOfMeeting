from pydub import AudioSegment
def audio_segmenter(file_name):
	audio = AudioSegment.from_wav(file_name) 
	n = len(audio) 
	interval = 60 * 1000
	overlap = 1.5 * 1000
	start = 0
	end = 0
	flag = 0
	counter = 1
	for i in range(0, 2 * n, interval): 
		
		# During first iteration, 
		# start is 0, end is the interval 
		if i == 0: 
			start = 0
			end = interval 

		# All other iterations, 
		# start is the previous end - overlap 
		# end becomes end + interval 
		else: 
			start = end - overlap 
			end = start + interval 

		# When end becomes greater than the file length, 
		# end is set to the file length 
		# flag is set to 1 to indicate break. 
		if end >= n: 
			end = n 
			flag = 1

		# Storing audio file from the defined start to end 
		chunk = audio[start:end] 

		# Filename / Path to store the sliced audio 
		filename = str(counter)+'.wav'

		# Store the sliced audio file to the defined path 
		chunk.export(filename, format ="wav") 
		# Print information about the current chunk 
		print("Processing chunk "+str(counter)+". Start = "
							+str(start)+" end = "+str(end)) 

		# Increment counter for the next chunk 
		counter = counter + 1
		if flag == 1:
			break
	return counter-1