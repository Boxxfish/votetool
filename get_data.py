#Script to collect congressional data and save it into a file
#Data is saved as bill_data.json
import sys
from typing import List

import requests
import json

def main():
    #Get legislator data
    print("Collecting legislator data...")
    senEndpoint = "https://api.propublica.org/congress/v1/116/senate/members.json"
    repEndpoint = "https://api.propublica.org/congress/v1/116/house/members.json"
    params = {}
    r = requests.get(url = senEndpoint, params = params, headers = {"X-API-Key":"e1apdjFwvkf43IgTLoJrOMnJVqG1G0QGHG8zyxhG"})
    senators = r.json()["results"][0]["members"]
    r = requests.get(url = repEndpoint, params = params, headers = {"X-API-Key":"e1apdjFwvkf43IgTLoJrOMnJVqG1G0QGHG8zyxhG"})
    reps = r.json()["results"][0]["members"]
    #Collect positions for each member
    senPositions = []
    for senator in senators:
        senPosEndpoint = "https://api.propublica.org/congress/v1/members/" + senator["id"] + "/votes.json"
        r = requests.get(url = senPosEndpoint, params = params, headers = {"X-API-Key":"e1apdjFwvkf43IgTLoJrOMnJVqG1G0QGHG8zyxhG"})
        votes = r.json()["results"][0]["votes"]
        voteData = {}
        for vote in votes:
            voteData[vote["bill"]["bill_id"]] = 1 if vote["position"] == "Yes" else 0
        senPositions.append(voteData)
    repPositions = []
    for rep in reps:
        repPosEndpoint = "https://api.propublica.org/congress/v1/members/" + rep["id"] + "/votes.json"
        r = requests.get(url = repPosEndpoint, params = params, headers = {"X-API-Key":"e1apdjFwvkf43IgTLoJrOMnJVqG1G0QGHG8zyxhG"})
        votes = []
        if "results" in r.json():
            votes = r.json()["results"][0]["votes"]
        voteData = {}
        for vote in votes:
            voteData[vote["bill"]["bill_id"]] = 1 if vote["position"] == "Yes" else 0
        repPositions.append(voteData)
    print("Finished legislator bill data.")
    #Get bill data
    print("Collecting bill data...")
    billEndpoint = "https://api.propublica.org/congress/v1/116/both/bills/passed.json"
    params = {}
    r = requests.get(url = billEndpoint, params = params, headers = {"X-API-Key":"e1apdjFwvkf43IgTLoJrOMnJVqG1G0QGHG8zyxhG"})
    print("Finished collecting bill data.")
    #Iterate over bills
    bills = r.json()["results"][0]["bills"]
    billOutput = []
    for bill in bills:
        print("Parsing bill " + bill["number"] + "...")
        summary = bill["summary"]
        #See how every member votes
        #If a member didn't vote and was supposed to, mark it as if they voted no
        voteResults = []
        billID = bill["bill_id"]
        if(bill["bill_type"] == "hr"):
            for repPosition in repPositions:
                if billID in repPosition:
                    voteResults.append(repPosition[billID])
                else:
                    voteResults.append(0)
        else:
            for senPosition in senPositions:
                if billID in senPosition:
                    voteResults.append(senPosition[billID])
                else:
                    voteResults.append(0)
        #Get rid of dataset if no one voted on it
        #if 1 in voteResults:
        billOutput.append((summary, voteResults))
        print("Finished.")
    #Export bill output to file
    with open("bill_data.json", "w") as outfile:
        j = json.dumps(dict(billOutput))
        outfile.write(j)

main()
