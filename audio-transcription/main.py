from audio_extracter import video_to_mp3
from silence_remover import remove_silence
from noise_remover import noise_remover
from transcript_generator import transcript_generator
import glob

def main():
	video_files=glob.glob("*.MOV")
	file_names=[]
	for i in video_files:
		video_to_mp3(i)
		file_name=i.split(".")[0]
		file_names.append(file_name)
		remove_silence(file_name)
		noise_remover(file_name)
	file_names.sort(key=int)	
	techniques=["_ctr_mb","_ctr_s","_median","_mfcc_down","_mfcc_up","_org","_pwr"]
	print("Generating Transcripts")
	for i in techniques:
		transcript_generator(file_names,i)
		


main()