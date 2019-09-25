import sys
import os
import time
 
 
def video_to_mp3(file_name):
    try:
        file, extension = os.path.splitext(file_name)
        # Convert video into .wav file
        os.system('ffmpeg -i {file}{ext} {file}.wav'.format(file=file, ext=extension))
        print('"{}" successfully converted into WAV!'.format(file_name))
    except OSError as err:
        print(err.reason)
        exit(1)