# Modified from Stuck_In_The_Matrix and OSRSBox
import requests
import json
import re
import time
import pandas as pd

PUSHSHIFT_REDDIT_URL = "http://api.pushshift.io/reddit"

def fetchObjects(**kwargs):
    # Default paramaters for API query
    params = {
        "sort_type":"created_utc",
        "sort":"asc",
        "size":1000
    }

    # Add additional paramters based on function arguments
    for key,value in kwargs.items():
        params[key] = value

    # Print API query paramaters
    print(params)

    # Set the type variable based on function input
    # The type can be "comment" or "submission", default is "comment"
    type = "comment"
    if 'type' in kwargs and kwargs['type'].lower() == "submission":
        type = "submission"

    # Perform an API request
    r = requests.get(PUSHSHIFT_REDDIT_URL + "/" + type + "/search/", params=params, timeout=30)

    # Check the status code, if successful, process the data
    if r.status_code == 200:
        response = json.loads(r.text)
        data = response['data']
        sorted_data_by_id = sorted(data, key=lambda x: int(x['id'],36))
        return sorted_data_by_id

def extract_reddit_data(**kwargs):
    # Speficify the start timestamp
    max_created_utc = 1356998400  # 01/01/2013 @ 12:00am (UTC)
    max_id = 0

    # Open a file for JSON output
    file = open("submissions.json","a")

    # While loop for recursive function
    while 1:
        nothing_processed = True
        # Call the recursive function
        objects = fetchObjects(**kwargs,after=max_created_utc)

        # Loop the returned data, ordered by date
        for object in objects:
            id = int(object['id'],36)
            if id > max_id:
                nothing_processed = False
                created_utc = object['created_utc']
                max_id = id
                if created_utc > max_created_utc: max_created_utc = created_utc
                # Output JSON data to the opened file
                print(json.dumps(object,sort_keys=True,ensure_ascii=True),file=file)

        # Exit if nothing happened
        if nothing_processed: return
        max_created_utc -= 1

        # Pause before the next recursive function call
        time.sleep(.5)

# Start program by calling function with:
# 1) Subreddit specified
# 2) The type of data required (comment or submission)
extract_reddit_data(subreddit="upliftingnews",type="submission")

f = open("submissions.json", "r")
keys = ['title','created_utc','domain','url','num_comments','over_18','score']
submissions_list = []
for line in f:

    submissions_list += [[json.loads(line).get(key) for key in keys]]

pd.DataFrame(submissions_list, columns=keys).to_csv('upliftingnews_submissions.csv')
