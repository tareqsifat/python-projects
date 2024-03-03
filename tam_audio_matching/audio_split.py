from pydub import AudioSegment
from datetime import date
from datetime import datetime
from prev_hour_audio import *
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ftp_save = os.getenv("FTP_DIRECTORY")
master_audios_directory = os.getenv("MASTER_AUDIO_DIRECTORY")
search_directory = os.getenv("SEARCH_DIRECTORY")

def concat_audio_files(audio_one_normal, audio_two_segmented, file_name):
    try:
        audio_one_segmented = AudioSegment.from_mp3(audio_one_normal['file_path'] + '/' + audio_one_normal['file_name'])
        combined = audio_one_segmented + audio_two_segmented[:300000]
        file_rename = audio_one_normal['file_name'].replace(f"{search_string(file_name)}-", '')


        folder_info = create_folder_return(3300000, file_rename)

        replaced_name = f"{folder_info['date']}-{folder_info['time']}-{file_rename[12:]}"
        split_audio = f"{folder_info['path']}/{replaced_name}"
        combined.export(split_audio, format="mp3")
        os.remove(f"{audio_one_normal['file_path']}/{audio_one_normal['file_name']}")
        delete_empty_directory(audio_one_normal['file_path'])
    except Exception as e: 
        print("concat->", e)
        pass


def split_master_audio(main_file_path):
    audios = []
    try:
        song = AudioSegment.from_mp3(main_file_path)
        i = 0
        j = 60000 * 10
        for _ in range(11):
            if i == 0:
               try:
                   file_name = main_file_path.split("/").pop()
                   prev_hour_last_audio_file = prev_hour_last_audio(file_name)
                   concat_audio_files(prev_hour_last_audio_file, song, file_name)
               except Exception as e:
                    print(e)
                    pass

            segment = song[i:j]
            file_name = main_file_path.split("/").pop()
            folder_name = create_folder_return(i,file_name)
            rename =  f"{folder_name['date']}-{folder_name['time']}-{file_name[12:]}"
            split_audio = f"{folder_name['path']}/{rename}"
            segment.export(split_audio, format='mp3')

            #save last 5 min of the hour in separate file
            if(i == 3000000):
                segment = song[3300000:3600000]
                split_audio = f"{create_search_directory(file_name)}/{search_string(file_name)}-{file_name}"
                segment.export(split_audio, format='mp3')
            i = i + 60000 * 5
            j = i + 60000 * 10
    except Exception as e:
        print('Error occur', e)
        pass

def create_folder_return(i, file_name):
    file_name_split = file_name.split("-")
    integer_number =  int(i/60000)
    formatted_integer = "{:02d}".format(integer_number)
    today = file_name_split[0]
    hour = file_name_split[1]
    path_to_store = f"{master_audios_directory}/{today}/{hour}{formatted_integer}"
    if not os.path.exists(path_to_store):
        os.makedirs(path_to_store)
    return {
            "path": path_to_store,
            "date": today,
            "time": f"{hour}{formatted_integer}"
            }

def create_search_directory(filename):
    file_name_split = filename.split("-")
    return_search_directory = f"{search_directory}/{file_name_split[0]}-{file_name_split[1]}"

    if not os.path.exists(return_search_directory):
        os.makedirs(return_search_directory)

    return return_search_directory

def is_empty_directory_with_files(directory):
    files = []
    directories = []

    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isfile(full_path):
            files.append(entry)
        elif os.path.isdir(full_path):
            directories.append(entry)

    return not (bool(files) or bool(directories))

def delete_empty_directory(directory):

    if is_empty_directory_with_files(directory):
        os.rmdir(directory)


if __name__ == "__main__":
    file = "/home/sifat/ftp_output/ftp_save/20230914-15-ATN Bangla.mp3"
    split_master_audio(file)

