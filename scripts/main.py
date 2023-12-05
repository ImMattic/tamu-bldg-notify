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
    previous_bldg_info = []
    current_bldg_info = []
    # Compare abbreviations
    for current_obj in current_data:
        current_obj_abbrev = current_obj["Abbrev"]
        found = False

        for previous_obj in previous_data:
            previous_obj_abbrev = previous_obj["Abbrev"]
            if previous_obj_abbrev != current_obj_abbrev:
                found = True
                break

        if not found:
            current_bldg_info.append(current_obj)
            previous_bldg_info.append(previous_obj)


# Function that strips unnecessary data and returns a list of building objects
def strip_excess_info(json_data):
    bldg_list = []

    for feature in json_data["features"]:
        bldg_list.append(feature["attributes"])

    # print(json.dumps(bldg_list, indent=2))
    return bldg_list


# Function that returns a filtered list given two list and based on OBJECTID
# First list: list of objects to be filtered out of the main list
# Second list: the unfiltered list that is to be filtered based on the criteria
def filter_list(criteria_list, unfiltered_list):
    criteria_to_match = [obj["OBJECTID"] for obj in criteria_list]
    filtered_data = [
        item for item in unfiltered_list if item["OBJECTID"] not in criteria_to_match
    ]
    return filtered_data


# Function that checks if any buildings were added or removed
def check_building_count(current_data, previous_data):
    added_bldgs = []
    removed_bldgs = []

    # Check for removed objects in current_data compared to previous_data
    for current_obj in current_data:
        current_obj_id = current_obj["OBJECTID"]
        found = False

        for previous_obj in previous_data:
            previous_obj_id = previous_obj["OBJECTID"]
            if previous_obj_id == current_obj_id:
                found = True
                break

        if not found:
            removed_bldgs.append(current_obj)

    # Check for added buildings in current_data comapred to previous_data
    for previous_obj in previous_data:
        previous_obj_id = previous_obj["OBJECTID"]
        found = False

        for current_obj in current_data:
            current_obj_id = current_obj["OBJECTID"]
            if current_obj_id == previous_obj_id:
                found = True
                break

        if not found:
            added_bldgs.append(previous_obj)

    return added_bldgs, removed_bldgs


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
    current_data = strip_excess_info(query_api())
    # current_data = strip_excess_info(load_json("./data/previous_data.json"))
    previous_data = strip_excess_info(load_json("./data/current_data.json"))

    # print(json.dumps(previous_data, indent=2))

    # Check to make sure any buildings were removed or added
    added_bldgs, removed_bldgs = check_building_count(current_data, previous_data)

    # Filter out any added or removed buildings from their respective lists so
    # they are ignored by the abbreviation check
    filtered_previous_data = filter_list(removed_bldgs, previous_data)
    filtered_current_data = filter_list(added_bldgs, current_data)


# # Schedule the job to run every 24 hours
# schedule.every(24).hours.do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1)

job()
