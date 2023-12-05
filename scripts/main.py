import requests
import json
from datetime import datetime, timedelta
import schedule
import time


# Function to query the API
def query_api():
    with open("./data/api_url.txt") as file:
        api_url = file.read().rstrip()
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        # Handle API error
        print(f"Error: {response.status_code}")
        return None


# Function that loads in JSON data
def load_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


# Function to compare data and send email if changes detected
def compare_abbrevs(current_data, previous_data):
    if "Abbrev" in current_data and current_data["abbrev"] != previous_data["abbrev"]:
        matching_attributes = current_data
        print(matching_attributes)
        return matching_attributes


# Function that strips unnecessary data and returns a list of building objects
def strip_excess_info(json_data):
    bldg_list = []

    for feature in json_data["features"]:
        bldg_list.append(feature["attributes"])

    # print(json.dumps(bldg_list, indent=2))
    return bldg_list


# Function that checks if any buildings were added or removed
def check_building_count(current_data, previous_data):
    print()


# # Function to send a Teams notification via webhooks
# def teams_notification(webhook_url, message):
#     headers = {"Content-Type": "application/json"}
#     payload = {"text": message}

#     response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)

#     if response.status_code == 200:
#         print("Teams notification sent successfully")
#     else:
#         print(f"Error sending Teams notification. Status code: {response.status_code}")


# Job to run every 24 hours
def job():
    # Get current and previous data
    current_data = query_api()
    previous_data = load_json("./data/previous_data.json")
    # Check to make sure any buildings were removed or added
    compare_abbrevs(current_data, previous_data)


# # Schedule the job to run every 24 hours
# schedule.every(24).hours.do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1)

job()
