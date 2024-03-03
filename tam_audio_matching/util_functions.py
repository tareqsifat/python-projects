import datetime
import matplotlib
import numpy as np
import librosa
import skimage
from matplotlib import pyplot as plt
from scipy import signal
from datetime import datetime, timedelta
import cv2
import noisereduce as nr
from settings import settings

matplotlib.use('Agg')


def find_audio_offset(master_file, device_file):
    long, sr_long = librosa.load(master_file, sr=22050)
    short, _ = librosa.load(device_file, sr=22050)
    if librosa.get_duration(y=short, sr=sr_long) < 59:
        return [], 0, "< 59s"
    if short.std() == 0.0:
        return [], 0, "Empty"
    
    long = (long - np.mean(long)) / long.std()
    short = (short - np.mean(short)) / short.std()

    long = nr.reduce_noise(y=long, sr=22050)
    short = nr.reduce_noise(y=short, sr=22050)

    c = signal.correlate(long, short, mode='valid', method='fft')

    if np.max(c) < 1000:
        return [], 0, " < 1000"
    c_max_index = np.argmax(c)
    long_file_similar_to_short = long[c_max_index: c_max_index + sr_long * 60]

    long_amplitude_db = librosa.amplitude_to_db(np.abs(librosa.stft(long_file_similar_to_short, hop_length=1024)), ref=np.max)
    fig = plt.figure(figsize=(14, 5))
    long_specshow = librosa.display.specshow(long_amplitude_db, sr=sr_long, y_axis='log', hop_length=1024, x_axis='time')
    plt.colorbar()
    canvas = plt.gca().figure.canvas
    canvas.draw()
    data = np.frombuffer(canvas.tostring_rgb(), dtype=np.uint8)
    long_img = data.reshape(canvas.get_width_height()[::-1] + (3,))
    long_specshow.remove()

    short_amplitude_db = librosa.amplitude_to_db(np.abs(librosa.stft(short, hop_length=1024)), ref=np.max)
    short_specshow = librosa.display.specshow(short_amplitude_db, sr=sr_long, y_axis='log', hop_length=1024, x_axis='time')
    canvas = plt.gca().figure.canvas
    canvas.draw()
    data = np.frombuffer(canvas.tostring_rgb(), dtype=np.uint8)
    short_img = data.reshape(canvas.get_width_height()[::-1] + (3,))
    short_specshow.remove()

    plt.clf()
    plt.cla()
    plt.close(fig)

    img1 = cv2.cvtColor(long_img, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(short_img, cv2.COLOR_BGR2GRAY)
    similarity = skimage.metrics.structural_similarity(img1, img2)

    if similarity < 0.70:
        return [], similarity, np.max(c)

    return [round(c_max_index / sr_long, 2)], similarity, np.max(c)


def master_offset(device_start_datetime, master_start_datetime):
    device_datetime = datetime.strptime(device_start_datetime, '%Y-%m-%d %H:%M:%S.%f')
    device_minute = divmod((device_datetime.minute + 60 - 2), 60)[1]
    master_datetime = datetime.strptime(master_start_datetime, '%Y-%m-%d %H:%M:%S.%f')
    master_minute = divmod((master_datetime.minute + 60), 60)[1]

    return np.abs(master_minute - device_minute)


def get_master_folder_path(device_start_datetime):
    try:
        picking_datetime = device_start_datetime

        picking_datetime -= timedelta(minutes=2)
        minute = divmod(picking_datetime.minute, 5)[0] * 5
        picking_datetime = datetime(picking_datetime.year, picking_datetime.month, picking_datetime.day, picking_datetime.hour,
                                   minute)
        master_files_path = settings.get('MASTER_AUDIOS_PATH')
        remote_directory_path = f"{master_files_path}/{picking_datetime.strftime('%Y%m%d')}/{picking_datetime.strftime('%H%M')}/"
        return picking_datetime, remote_directory_path
    except Exception as e:
        print("error =>", e)
        pass


def get_device_folder_path(file_path):
    return f"{settings.get('DEVICE_AUDIOS_PATH')}/{file_path}"


def get_channel_name(master_audio_path):
    try:
        split_paths = master_audio_path.split("/")

        if len(split_paths) > 0:
            master_file_name = split_paths[-1:][0]
            master_file_name = master_file_name.replace(".mp3", "")
            return master_file_name[14:]
        return None
    except Exception as e:
        print("error =>", e)
        pass

