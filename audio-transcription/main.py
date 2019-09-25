from audio_extracter import video_to_mp3
from silence_remover import remove_silence
from noise_remover import noise_remover
from transcript_generator import transcript_generator
from audio_segmenter import audio_segmenter
import glob

def main():
	video_file="final.mp4"
	video_to_mp3(video_file)
	chunks=audio_segmenter(video_file.split(".")[0]+".wav")

	file_names=[]
	for i in range(1,chunks+1):
		file_name=str(i)
		file_names.append(file_name)
		remove_silence(file_name)
		noise_remover(file_name)

	techniques=["_ctr_mb","_ctr_s","_median","_mfcc_down","_mfcc_up","_org","_pwr"]
	print("Generating Transcripts")
	for i in techniques:
		transcript_generator(file_names,i)
		


main()