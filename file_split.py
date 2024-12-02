# convert wav tot flac file
from pydub import AudioSegment
import math
import os
from natsort import natsorted
from collections import Counter

def get_duration(audio):
    return audio.duration_seconds



def single_split(audio, from_sec, to_sec, split_filename, destination_dir):
    if from_sec > to_sec:
        raise ValueError("from cannot be greater than to")
    
    t1 = from_sec * 1000
    t2 = to_sec   * 1000
    split_audio = audio[t1:t2]
    split_audio.export(destination_dir + '/' + split_filename, format="wav")
    
def single_split_file(filepath, from_sec, to_sec, new_filename, destination_dir):
    audio = AudioSegment.from_wav(filepath)
    duration = math.ceil(get_duration(audio))
    
    if (duration <= from_sec) or (duration <= to_sec):
        raise ValueError("the target clip exceeds the duration of the file")
    if from_sec > to_sec:
        raise ValueError("from cannot be greater than to")
    
    single_split(audio=audio, 
                 from_sec=from_sec,
                 to_sec=to_sec,
                 split_filename=new_filename,
                 destination_dir=destination_dir)


def multiple_split(filepath, sec_per_split, destination_dir):
    audio = AudioSegment.from_wav(filepath)
    total_secs = math.ceil(get_duration(audio))
    filename = filepath.split('/')[-1]
    # print("Splitting ", filename)

    for i in range(0, total_secs, sec_per_split):
        split_fname = filename.split('.')[0] + '_' + str(i) + '.wav'
        single_split(audio, i, i+sec_per_split, split_fname, destination_dir=destination_dir)

        print(split_fname + ' Done')
        if i == (total_secs - sec_per_split):
            # print('All splited successfully')
            break


'''
Yes, I can use the multiple_split function after obtaining the filepath.
But for some reason, I don't want to. :)
'''
def multiple_split_folder(source_dir, destination_dir, sec_per_split, file_format=None, p_file_count=1):
    filepaths = get_files(source_dir)
    audio_data = [AudioSegment.from_wav(filepath) for filepath in filepaths]
    duration_secs_per_file = [math.ceil(get_duration(audio)) for audio in audio_data]
    filenames = [filepath.split('/')[-1] for filepath in filepaths]
    
    file_count = p_file_count
    last_saved_file = ''
    for filename, audio, duration in zip(filenames, audio_data, duration_secs_per_file):
        # print("Splitting ", filename, '\n')
        for i in range(0, duration, sec_per_split):
            extension = '.' + filename.split('.')[1]
            
            if file_format is None:
                split_filename = filename.split('.')[0] + '_' + str(i) + extension
            else:
                split_filename = file_format + '{:03d}'.format(file_count) + extension
            
            single_split(audio=audio, 
                         from_sec=i, 
                         to_sec=i+sec_per_split, 
                         split_filename=split_filename, 
                         destination_dir=destination_dir)
            file_count += 1
            # print(split_filename + ' Done')
            last_saved_file = split_filename
            if i == (duration - sec_per_split):
                # print(f'\n{filename} chunked successfully\n\n')
                break
    
    print(last_saved_file)
        

def get_files(folder):
    files = os.listdir(folder)
    files = natsorted(files)
    files_path = [folder + '/' + f for f in files]
    return files_path
