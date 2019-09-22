#Script to collect congressional data and save it into a file
#Data is saved as bill_data.csv
import sys
from typing import List

import requests
import json

def main():
    #Get legislator data
    print("Collecting legislator data...")
    senEndpoint = "https://api.propublica.org/congress/v1/116/senate/members.json"
    params = {}
    r = requests.get(url = senEndpoint, params = params, headers = {"X-API-Key":"e1apdjFwvkf43IgTLoJrOMnJVqG1G0QGHG8zyxhG"})
    senators = r.json()["results"][0]["members"]
    memberObj = []
    for senator in senators:
        sen = {
            "Name": senator["first_name"] + " " + senator["last_name"],
            "State": senator["state"]
        }
        memberObj.append(sen)
    print("Finished legislator bill data. Exporting.")
    with open("members.json", "w") as outfile:
        json.dump(memberObj, outfile)

main()
