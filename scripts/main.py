import requests
import json
from datetime import datetime, timedelta
import schedule
import time
import textwrap


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
    index = 0
    # Compare abbreviations
    for current_obj in current_data:
        current_obj_abbrev = current_obj["Abbrev"]
        found = False

        for previous_obj in previous_data:
            previous_obj_abbrev = previous_obj["Abbrev"]
            if previous_obj_abbrev == current_obj_abbrev:
                found = True
                break

        if not found:
            current_bldg_info.append(current_obj)
            previous_bldg_info.append(previous_data[index])
        index += 1

    return current_bldg_info, previous_bldg_info


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
    filtered_list = []
    for obj in unfiltered_list:
        if obj["OBJECTID"] not in [c_obj["OBJECTID"] for c_obj in criteria_list]:
            filtered_list.append(obj)
    return filtered_list


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


def message_creation(added_bldgs, removed_bldgs, current_bldg_data, previous_bldg_data):
    added_building_text_blocks = ["Buildings added (%i):\n" % len(added_bldgs)]
    removed_building_text_blocks = ["Buildings removed (%i):\n" % len(removed_bldgs)]
    abbrev_change_text_blocks = [
        "Building abbreviations changed (%i):\n" % len(current_bldg_data)
    ]
    teams_msg = ""

    for obj in added_bldgs:
        text_block = textwrap.dedent(
            """\
        Name: %s
        Building number: %s
        Buidling abbreviation: %s
        Address: %s, %s, TX, %s

        """
            % (
                obj["BldgName"],
                obj["Number"],
                obj["Abbrev"],
                obj["Address"],
                obj["City"],
                obj["Zip"],
            )
        )
        added_building_text_blocks.append(text_block)

    for obj in removed_bldgs:
        text_block = textwrap.dedent(
            """\
        Name: %s
        Building number: %s
        Buidling abbreviation: %s
        Address: %s, %s, TX, %s

        """
            % (
                obj["BldgName"],
                obj["Number"],
                obj["Abbrev"],
                obj["Address"],
                obj["City"],
                obj["Zip"],
            )
        )
        removed_building_text_blocks.append(text_block)

    index = 0
    for obj in current_bldg_data:
        text_block = textwrap.dedent(
            """\
        Name: %s
        Building number: %s
        Old buidling abbreviation: %s
        New building abbreviation: %s
        Address: %s, %s, TX, %s

        """
            % (
                obj["BldgName"],
                obj["Number"],
                obj["Abbrev"],
                previous_bldg_data[index]["Abbrev"],
                obj["Address"],
                obj["City"],
                obj["Zip"],
            )
        )
        abbrev_change_text_blocks.append(text_block)
        index += 1

    if len(added_bldgs) > 0:
        teams_msg += "".join(added_building_text_blocks)

    if len(removed_bldgs) > 0:
        teams_msg += "".join(removed_building_text_blocks)

    if len(current_bldg_data) > 0:
        teams_msg += "".join(abbrev_change_text_blocks)

    print(teams_msg)


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
    filtered_previous_data = filter_list(added_bldgs, previous_data)
    filtered_current_data = filter_list(removed_bldgs, current_data)
    current_bldg_info, previous_bldg_info = compare_abbrevs(
        filtered_current_data, filtered_previous_data
    )

    message_creation(added_bldgs, removed_bldgs, current_bldg_info, previous_bldg_info)


# # Schedule the job to run every 24 hours
# schedule.every(24).hours.do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1)

job()
