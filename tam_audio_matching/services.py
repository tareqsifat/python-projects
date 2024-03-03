import json
from datetime import datetime, timezone, timedelta
import requests
from dotenv import load_dotenv
from settings import settings

# Load environment variables from .env file
load_dotenv()

class MakeApiCall:
    def __init__(self):
        self.baseUrl = settings.get("DEVICE_AUDIO_BASE_URL")

    def get_data(self, endpoint, current_page=1):
        try:
            token = settings.get('DEVICE_AUDIO_TOKEN')
            considering_days = settings.get('CONSIDERING_PREV_DAYS')
            params = {
                        "start_range": (datetime.now(timezone.utc)- timedelta(hours= considering_days * 24 - 6)).replace(microsecond=0, second=0, minute=0, hour=0).strftime('%Y-%m-%d %H:%M:%S'),
                        "end_range": (datetime.now(timezone.utc)- timedelta(hours= considering_days * 24 - 6)).replace(microsecond=999999, second=59, minute=59, hour=23).strftime('%Y-%m-%d %H:%M:%S'),
                        "page": current_page,
                        "per_page": 30 }
            response = requests.get(url=f"{self.baseUrl}/{endpoint}",
                                    params=params,
                                    headers={"Authorization": f"Bearer {token}"})
            if response.status_code == 200:
                json_obj_str =  self.formatted_json(response.json())
                return json.loads(json_obj_str).get('data'), int(response.headers.get('X-Total-Pages'))
            else:
                return [], 1
        except Exception as e:
            print(e)
            return [], 1

    def post_matching_data(self, endpoint, body):
        try:
            baseUrl = settings.get('REPORTING_BASE_URL')
            token = settings.get('REPORTING_TOKEN')
            response = requests.post(f"{baseUrl}/{endpoint}", headers={"Authorization": f"Bearer {token}"}, json=body)

            if response.status_code == 201:
                return True
            else:
                return False
        except Exception as e:
            print("exception in sending =>", e)
            return False

    def formatted_json(self, obj):
        return json.dumps(obj, sort_keys=True, indent=4)



#MakeApiCall().get_data("audios")
