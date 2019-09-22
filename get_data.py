#Script to collect congressional data and save it into a file
#Data is saved as bill_data.csv
import sys
from typing import List

import requests
import csv
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

def main():
    #Init google machine client
    client = language.LanguageServiceClient()
    #Get legislator data
    print("Collecting legislator data...")
    senEndpoint = "https://api.propublica.org/congress/v1/116/senate/members.json"
    #repEndpoint = "https://api.propublica.org/congress/v1/116/house/members.json"
    params = {}
    r = requests.get(url = senEndpoint, params = params, headers = {"X-API-Key":"e1apdjFwvkf43IgTLoJrOMnJVqG1G0QGHG8zyxhG"})
    senators = r.json()["results"][0]["members"]
    senDict = {}
    for i in range(len(senators)):
        senDict[senators[i]["id"]] = i
    #r = requests.get(url = repEndpoint, params = params, headers = {"X-API-Key":"e1apdjFwvkf43IgTLoJrOMnJVqG1G0QGHG8zyxhG"})
    #reps = r.json()["results"][0]["members"]
    #Collect positions for each member
    print("Finished legislator bill data.")
    #Get bill data
    print("Collecting bill data...")
    validBills = []
    validVotes = []
    currOffset = 0
    while len(validBills) <= 50:
        voteEndpoint = "https://api.propublica.org/congress/v1/senate/votes/recent.json?offset=" + str(currOffset)
        params = {}
        r = requests.get(url = voteEndpoint, params = params, headers = {"X-API-Key":"e1apdjFwvkf43IgTLoJrOMnJVqG1G0QGHG8zyxhG"})
        votes = r.json()["results"]["votes"]
        for vote in votes:
            #Query bill that's being voted on
            if "api_uri" not in vote["bill"] or vote["bill"]["api_uri"] == None:
                continue
            billEndpoint = vote["bill"]["api_uri"]
            params = {}
            r = requests.get(url=billEndpoint, params=params, headers={"X-API-Key": "e1apdjFwvkf43IgTLoJrOMnJVqG1G0QGHG8zyxhG"})
            if r.json()["status"] == "OK":
                bill = r.json()["results"][0]
                validBills.append(bill)
                validVotes.append(vote)
        currOffset += 20
    print("Finished collecting bill data.")
    #Iterate over bills
    print("Parsing bills...")
    billOutput = []
    for i in range(len(validVotes)):
        bill = validBills[i]
        vote = validVotes[i]
        #Extract keywords from summary
        summary = bill["summary"]
        document = types.Document(content = summary, type = enums.Document.Type.PLAIN_TEXT)
        entities = client.analyze_entities(document = document).entities
        entityCount = len(entities) if len(entities) < 5 else 5
        keywords = ""
        for i in range(entityCount):
            keywords = keywords + " " + entities[i].name
        #See how every member votes
        #If a member didn't vote and was supposed to, mark it as if they voted no
        voteResults = []
        billID = bill["bill_id"]
        if(bill["bill_type"] == "hr"):
            continue
            """for repPosition in repPositions:
                if billID in repPosition:
                    voteResults.append(repPosition[billID])
                else:
                    voteResults.append(0)"""
        else:
            #Load voting data
            rollCallEndpoint = "https://api.propublica.org/congress/v1/116/senate/sessions/" + str(vote["session"]) + "/votes/" + str(vote["roll_call"]) + ".json"
            params = {}
            r = requests.get(url=rollCallEndpoint, params=params, headers={"X-API-Key": "e1apdjFwvkf43IgTLoJrOMnJVqG1G0QGHG8zyxhG"})
            positions = r.json()["results"]["votes"]["vote"]["positions"]
            for i in range(len(senators)):
                voteResults.append(0)
            for position in positions:
                voteResults[senDict[position["member_id"]]] = 1 if position["vote_position"] == "Yes" else 0
        #Get rid of dataset if no one voted on it
        billOutput.append((keywords, voteResults))
    print("Finished parsing bills. Outputting to bill_data.csv")
    #Export bill output to file
    with open("bill_data.csv", "w", newline="") as csvfile:
        datawriter = csv.writer(csvfile, delimiter=",", quotechar = "|", quoting = csv.QUOTE_MINIMAL)
        datawriter.writerows(zip(dict(billOutput).keys(), list(dict(billOutput).values())))

main()
