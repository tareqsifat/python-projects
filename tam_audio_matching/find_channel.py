from dbConnection import get_matching_rawdata, update_row_entry, get_row_entry, update_send_status
from datetime import datetime, timedelta

from services import MakeApiCall


def get_time_difference(first_datetime, second_datetime):
    channel_datetime = datetime.strptime(first_datetime, '%Y-%m-%d %H:%M:%S.%f')
    device_time = datetime.strptime(second_datetime, '%Y-%m-%d %H:%M:%S.%f')

    if channel_datetime > device_time:
        return channel_datetime - device_time
    else:
        return device_time - channel_datetime


def find_channel():
    try:
        rawData = get_matching_rawdata()
        tempData = []
        api = MakeApiCall()
        for entry in rawData:
            device_datetime = entry[2].strftime('%Y-%m-%d %H:%M:%S.%f')
            household = entry[5]
            et = entry[3]
            params = {}

            if len(et) < 1:
                update_row_entry(device_datetime, entry[5])
                params = {"household_id": entry[5], "member_ids": entry[1], "date_time": device_datetime}
            elif len(et) == 1 and len(et[0].get('matching_datetime')) == 1:
                update_row_entry(device_datetime, entry[5], et[0].get('channel_name'), et[0].get('matching_datetime')[0])
                params = {"household_id": entry[5], "member_ids": entry[1], "date_time": et[0].get('matching_datetime')[0], "channel_title": et[0].get('channel_name')}
            else:
                for channel in et:
                    for match in channel.get('matching_datetime'):
                        tempData.append(
                            {
                                "channel_name": channel.get('channel_name'),
                                "channel_datetime": match,
                                "device_datetime": device_datetime,
                                "time_diff": get_time_difference(match, device_datetime)
                            }
                        )

                tempData.sort(key=lambda x: x['time_diff'])

                for tem in tempData:
                    is_set = False
                    prev_datetime = datetime.strptime(tem.get("device_datetime"), '%Y-%m-%d %H:%M:%S.%f') - timedelta(minutes=1)

                    pre_entry = get_row_entry(prev_datetime, household)
                    if pre_entry != None and pre_entry[0] and pre_entry[0] == tem.get("channel_name"):
                        update_row_entry(tem.get("device_datetime"), entry[5], tem.get("channel_name"), tem.get("channel_datetime"))
                        params = {"household_id": entry[5],
                                  "member_ids": entry[1],
                                  "date_time": tem.get("channel_datetime"),
                                  "channel_title": tem.get("channel_name"),
                                  }

                        is_set = True
                    elif pre_entry == None or not pre_entry[0] or len(pre_entry[1]) <= 0:

                        next_datetime = datetime.strptime(tem.get("device_datetime"), '%Y-%m-%d %H:%M:%S.%f') + timedelta(minutes=1)
                        next_entry = get_row_entry(next_datetime, household)

                        if next_entry == None or next_entry[0] or len(next_entry[1]) <= 0:
                            update_row_entry(tem.get("device_datetime"), entry[5], tem.get("channel_name"), tem.get("channel_datetime"))
                            params = {"household_id": entry[5],
                                      "member_ids": entry[1],
                                      "date_time": tem.get("channel_datetime"),
                                      "channel_title": tem.get("channel_name"),
                                      }
                            is_set = True
                        else:
                            next_temp = []
                            for channel in next_entry[1]:
                                for match in channel.get('matching_datetime'):

                                    next_temp.append(
                                        {
                                            "channel_name": channel.get('channel_name'),
                                            "channel_datetime": match,
                                            "device_datetime": device_datetime,
                                            "time_diff": get_time_difference(match, device_datetime)
                                        }
                                    )

                            if any(obj['channel_name'] == tem.get("channel_name") for obj in next_temp):
                                update_row_entry(tem.get("device_datetime"), entry[5], tem.get("channel_name"), tem.get("channel_datetime"))
                                params = {"household_id": entry[5],
                                          "member_ids": entry[1],
                                          "date_time": tem.get("channel_datetime"),
                                          "channel_title": tem.get("channel_name"),
                                          }
                                is_set = True

                    if is_set:
                        break
                tempData = []
            if api.post_matching_data("match_logs", params):
                update_send_status(device_datetime, params.get("household_id"))
    except Exception as e:
        print("exception => ", e)