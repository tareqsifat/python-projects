import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
search_directory = os.getenv("SEARCH_DIRECTORY")


# Specify the directory where you want to search

def prev_hour_last_audio(file_name):

    partial_string = f"{search_string(file_name)}"
    file_path = last_hour_folder(file_name)

    # Get a list of all files in the directory that contain the partial string
    matching_files = [filename for filename in os.listdir(file_path) if partial_string in filename]
    # Extract just the filenames without the directory path
    matching_filenames = [os.path.basename(filename) for filename in matching_files]


    prev_hour_last_audio_object = {
        "file_path" : file_path,
        "file_name" : matching_filenames[0]
    }

    return prev_hour_last_audio_object

def last_hour_folder(file_name):
    file_name_split = file_name.split("-")

    date_obj = datetime.strptime(f"{file_name_split[0]} {file_name_split[1]}", '%Y%m%d %H') - timedelta(hours = 1)
    prev_date = date_obj.strftime('%Y%m%d')
    prev_hour = date_obj.strftime('%H')
    file_path = f"{search_directory}/{prev_date}-{prev_hour}"

    return file_path

def search_string(file_name):
    return f"split_{55}_{file_name.split('.')[0][12:]}"


# if __name__ == "__main__":

#     main_file_path = "20230618-20-Channel-24.mp3"
#     prev_hour_last_audio(main_file_path)