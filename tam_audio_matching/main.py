import datetime
import json
import os
from datetime import datetime, timedelta
from SFTP_Connection import Sftp
from settings import settings
from dbConnection import insert_matching_result
from services import MakeApiCall
from util_functions import get_master_folder_path, find_audio_offset, get_channel_name, get_device_folder_path
import glob
from find_channel import find_channel

call = MakeApiCall()


def match_audios_N_save():
    try:
        global sftp
        device_file_path = ""
        try:
            sftp = Sftp(settings.get("SFTP_HOST"), settings.get("SFTP_USERNAME"), settings.get("SFTP_PASSWORD"))
            sftp.connect()
        except:
            print("SFTP error")

        device_files, total_pages = call.get_data("audios", 1)

        for iterator in range(1, total_pages + 1):
            for device_file in device_files:
                sftp.connection.get(get_device_folder_path(device_file["file_path"]))
                try:
                    rows = []
                    device_start_datetime = datetime.strptime(device_file["start_time"], '%Y-%m-%dT%H:%M:%S.%fZ')
                    master_file_start_datetime, master_audios_folder_path = get_master_folder_path(device_start_datetime)
                    master_files = glob.glob(f"{master_audios_folder_path}*")
                    co_relation_matching_result = []
                    device_file_path = device_file["file_path"].split("/")[1]
                    for master_file in master_files:
                        try:
                            offset, similarity, max_c = find_audio_offset(master_file, device_file_path)
                            matching_datetime = []
                            for y in offset:
                                matching_datetime.append((master_file_start_datetime + timedelta(seconds=y)).strftime("%Y-%m-%d %H:%M:%S.%f"))
                            if len(offset):
                                co_relation_matching_result.append({"channel_name": get_channel_name(master_file), "matching_datetime": matching_datetime})
                        except Exception as e:
                            print("matching failed ", e)
                            pass

                    rows.append((device_file["household_id"], json.dumps(device_file["member_ids"]), device_start_datetime, json.dumps(co_relation_matching_result)))

                    if len(rows):
                        insert_matching_result(rows)

                    try:
                        os.remove(device_file_path)
                    except Exception as e:
                        print("error in removing ", e)
                        pass
                except Exception as e:
                    print("exception => ", e)
                    pass
            if iterator <= total_pages - 1:
                device_files, _ = call.get_data("audios", iterator+1)
    except Exception as e:
        print(f"Error in matching main file => {e}", )
        pass

match_audios_N_save()
find_channel()
