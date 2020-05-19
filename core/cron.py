from django_cron import CronJobBase, Schedule
import requests
import json
import pymongo
import threading

class Initialize():
    def __init__(self, name):
        self.name = name
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        mydb = myclient[f"{self.name}"]
        global mycolTeams
        mycolTeams = mydb["Teams"]
        global mycolEvents
        mycolEvents = mydb["Events"]



class get_events():
    def __init__(self):
        Initialize("webDB_VEX")
        params = ["sku", "name", "start", "end", "divisions", "loc_venue", "loc_city", "loc_region", "loc_country"]
        response = requests.get(
                "https://api.vexdb.io/v1/get_events?season=Tower Takeover").text
        actResponse = json.loads(response)
        RealResponse = actResponse["result"]

        for numb in RealResponse:
            Event_Dict = {}
            for param in params:
                try:
                    Event_Dict[f"{param}"] = numb[f"{param}"]
                except Exception as e:
                    pass
            mycolEvents.insert_one(Event_Dict)
        



class team():
    def __init__(self, team):
        self.team = team
        global data
        data={}

    def get_teams(self):
        fields = ["team_name","number", "robot_name", "organisation","city","region","country","grade"]
        request = f"https://api.vexdb.io/v1/get_teams?team={self.team}&season=Tower Takeover"
        resp1 = requests.get(request).text
        resp2 = json.loads(resp1)
        response = resp2["result"][0]

        for field in fields:       
            data[field] = response[field]

    def get_matches(self):
        request = f"https://api.vexdb.io/v1/get_matches?team={self.team}&season=Tower Takeover"
        resp1 = requests.get(request).text
        resp2 = json.loads(resp1)
        response = resp2["result"]
        amt=len(response)
        curAverage=0
        for resp in response:
            if resp["blue1"] == self.team or resp["blue2"] == self.team or resp["blue3"] == self.team:
                curAverage+=resp["bluescore"]
            if resp["red1"] == self.team or resp["red2"] == self.team or resp["red3"] == self.team:
                curAverage += resp["redscore"]
        try:
            average=round(curAverage/amt, 2)
        except Exception as e:
            print(e)
            average = 0
        data["average"] = average
        data["total_matches"] = amt
        data["matches"] = response

    def get_rankings(self):
        fields = ["wins","losses","ties","ap","wp","sp","max_score","opr","dpr","trsp","ccwm","rank"]
        request = f"https://api.vexdb.io/v1/get_rankings?team={self.team}&season=Tower Takeover"
        resp1 = requests.get(request).text
        resp2 = json.loads(resp1)
        response = resp2["result"]
        allData = {}
        if response != []:
            index = 0
            for event in response:
                eventData = {}
                for field in fields:
                    eventData[field] = event[field]
                allData[event["sku"]] = eventData
        else:
            allDate=None       

        data["rankings"] = allData
    def get_skills(self):
        fields = ["rank","attempts", "score", "season_rank","season_attempts"]
        requestDriver = f"https://api.vexdb.io/v1/get_skills?team={self.team}&season=Tower Takeover&type=0"
        requestProgramming = f"https://api.vexdb.io/v1/get_skills?team={self.team}&season=Tower Takeover&type=1"
        requestCombined = f"https://api.vexdb.io/v1/get_skills?team={self.team}&season=Tower Takeover&type=2"

        resp1Driver = requests.get(requestDriver).text
        resp2Driver = json.loads(resp1Driver)
        responseDriver = resp2Driver["result"]

        if responseDriver != []:
            data["DriverData"] = responseDriver
            total = 0
            driverTopList = []
            for skillsDriverData in responseDriver:
                total += skillsDriverData["score"]
                driverTopList.append(skillsDriverData["score"])
            data["driverAverage"] = total/len(responseDriver)
            data["driverTopScore"] = max(driverTopList)
        else:
            data["driverTopScore"] = 0 
            data["DriverData"] = []
            data["driverAverage"] = 0


        resp1Programming = requests.get(requestProgramming).text
        resp2Programming = json.loads(resp1Programming)
        responseProgramming = resp2Programming["result"]

        if responseProgramming != []:
            data["ProgrammingData"] = responseProgramming
            total = 0
            programmingTopList = []
            for skillsProgrammingData in responseProgramming:
                total += skillsProgrammingData["score"]
                programmingTopList.append(skillsProgrammingData["score"])
            data["programmingAverage"] = total/len(responseProgramming)
            data["programmingTopScore"] = max(programmingTopList)
        else:
            data["programmingTopScore"] = 0
            data["ProgrammingData"] = []
            data["programmingAverage"] = 0


        resp1Combined = requests.get(requestCombined).text
        resp2Combined = json.loads(resp1Combined)
        responseCombined = resp2Combined["result"]

        if responseCombined != []:
            data["CombinedData"] = responseCombined
            total = 0
            combinedTopList = [] 
            for skillsCombinedData in responseCombined:
                total += skillsCombinedData["score"]
                combinedTopList.append(skillsCombinedData["score"])
            data["combinedAverage"] = total/len(responseCombined)
            data["combinedTopScore"] = max(combinedTopList)
        else:
            data["combinedTopScore"] = 0 
            data["CombinedData"] = []
            data["combinedAverage"] = 0

    def insert(self):
        mycolTeams.insert_one(data)





# class fillDB(CronJobBase):
#     RUN_EVERY_MINS = 20 # every 20 minutes

#     schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
#     code = 'core.fillDB'    # a unique code

def do(aTeam):                
    # MakeDB
    Initialize("webDB_VEX")
    # fillevents

    teamer = aTeam["number"]
    instance = team(teamer)
    threadTeams = threading.Thread(
        target=instance.get_teams())
    threadMatches = threading.Thread(
        target=instance.get_matches())
    threadRankings = threading.Thread(
        target=instance.get_rankings())
    threadSkills = threading.Thread(
        target=instance.get_skills())


    threadTeams.start()
    threadMatches.start()
    threadRankings.start()
    threadSkills.start()


    threadTeams.join()
    threadMatches.join()
    threadRankings.join()
    threadSkills.join()

    instance.insert()


# get_events()
request = f"https://api.vexdb.io/v1/get_teams?season=Tower Takeover"
resp1 = requests.get(request).text
resp2 = json.loads(resp1)
response = resp2["result"]
for aTeam in response:
    x=threading.Thread(target=do(aTeam))
    x.setDaemon(True)
    x.start()


