from datetime import datetime, timedelta
import requests
import os
from pathlib import Path

#
# Removes previous days sent messages file.
#
def getToday():
    return datetime.now().strftime("%Y-%m-%d")

def manage_files():
    filename = "./txt/" + getToday() + ".txt"

    # Make sure today has a file
    if not os.path.exists(filename):
        Path(filename).touch()

    # Clean up old files
    yesterday = datetime.today() - timedelta(days=1)
    filename = "./txt/" + yesterday.strftime("%Y-%m-%d") + ".txt"

    try:
        os.remove(filename)
    except:
        pass
#
# Checks if a passed in text exists in the sent messages file.
#
def does_exist_in_sent_messages(whathappened):
    filename = "./txt/" + getToday() + ".txt"

    with open(filename,'r') as f:
        if whathappened in f.read():
            return True

    return False

#
# Updates the sent messages file.
#
def update_sent_messages(whathappened):
    filename = "./txt/" + getToday() + ".txt"

    with open(filename,'a+') as f:
        f.writelines(whathappened + "\n")

#
# Checks the API and sends any new transactions
#
def check_mlb_api(pushover_token, pushover_user_id):
    # Setup today's date0 as YYYY-MM-DD
    today = getToday()

    # Define the API endpoint
    mlb_api = "https://statsapi.mlb.com/api/v1/transactions?teamId=112&startDate=" + today + "&endDate=" + today
    pushover_api = "https://api.pushover.net/1/messages.json?token=" + pushover_token + "&user=" + pushover_user_id + "&message="

    # Call MLB API
    response = requests.get(mlb_api)

    # If the status code is sucess
    if (response.status_code == 200):
        # Parse the json
        json = response.json()

        # Pull out the transactions
        tranactions = json["transactions"]

        # Loop through the transactions
        for transaction in tranactions:
            whathappened = transaction["description"]

            # If we haven't sent this one before, send it
            if not does_exist_in_sent_messages(whathappened):
                pushover_response = requests.post(pushover_api + whathappened)

                if pushover_response.status_code == 200:
                    update_sent_messages(whathappened)

#
# Entry point
#
# Cleanup previous day's file.
manage_files()

# Get environment varibles.
pushover_token = os.getenv('PUSHOVER_TOKEN')
pushover_user_id = os.getenv('PUSHOVER_USER_ID')

# If the environment varibles are not set, show an error.
if pushover_token is not None and pushover_user_id is not None:
    check_mlb_api(pushover_token, pushover_user_id)
else:
    print("ERROR! Environment varibles are not set!")

