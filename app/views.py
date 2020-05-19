# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import default_storage, FileSystemStorage
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
from django.http import HttpResponse
from operator import itemgetter
import pymongo
import pycountry
from datetime import timedelta
import dateutil.parser as parser
import datetime
import operator
import random
import os

def page_validator(curuser):
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient["webDB_VEX"]
    mycolUserInfo = mydb["userInfo"]
    return mycolUserInfo.find_one({"username":curuser})


class getUserInfo():
    def __init__(self, curUser, db):
        self.db = db
        self.curUser = curUser
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        mydb = myclient[f"{self.db}"]
        global mycolUserInfo
        mycolUserInfo = mydb["userInfo"]
        query = {"username":self.curUser}
        global find
        find = mycolUserInfo.find_one(query)
    
    def get(self):
        return find
    def getProfilePic(self):
        return find["profilePic"]
    def getMyTeam(self):
        return find["teamNumb"]

    def getCompetitors(self):
        return find["competitor1"], find["competitor2"], find["competitor3"]

    def getMatchesGoals(self):
        return find["matchesAverageGoal"], find["matchesRankGoal"], find["matchesTopScoreGoal"]

    def getSkillsGoals(self):
        return find["skillsDriverGoal"], find["skillsProgGoal"], find["skillsRankGoal"]

    def getCalendar(self):
        try:
            return find["calendar"]
        except:
            return False





class getTeam():
    def __init__(self, team, db):
        self.team = team
        self.db = db
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        mydb = myclient[f"{self.db}"]
        global mycolTeams
        mycolTeams = mydb["Teams"]
    
    
    def get(self):
        query = {'number':self.team}
        result = {}
        query = mycolTeams.find_one(query)
        return query

    def specialChars1(self, myTeamAverage, limiter):
        queryGreater={
            "average": {
             "$gt":myTeamAverage
            }
         }
        queryLesser={
            "average": {
             "$lt":myTeamAverage
            }
         }
        averageGreater = mycolTeams.find(queryGreater).sort("average",1).limit(limiter)
        averageLesser = mycolTeams.find(queryLesser).sort("average",-1).limit(limiter)
        return averageGreater, averageLesser

    def specialChars2(self, myTeamAverage):
        queryGreater = {
            "driverAverage": {
                "$gt": myTeamAverage
            }
        }
        queryLesser = {
            "driverAverage": {
                "$lt": myTeamAverage
            }
        }
        averageGreater = mycolTeams.find(
            queryGreater).sort("driverAverage", 1).limit(2)
        averageLesser = mycolTeams.find(
            queryLesser).sort("driverAverage", -1).limit(2)
        return averageGreater, averageLesser

    def specialChars3(self, myTeamAverage):
        queryGreater = {
            "driverTopScore": {
                "$gt": myTeamAverage
            }
        }
        queryLesser = {
            "driverTopScore": {
                "$lt": myTeamAverage
            }
        }
        averageGreater = mycolTeams.find(
            queryGreater).sort("driverTopScore", 1).limit(2)
        averageLesser = mycolTeams.find(
            queryLesser).sort("driverTopScore", -1).limit(2)
        return averageGreater, averageLesser

    def specialChars4(self, myTeamAverage):
        queryGreater = {
            "programmingAverage": {
                "$gt": myTeamAverage
            }
        }
        queryLesser = {
            "programmingAverage": {
                "$lt": myTeamAverage
            }
        }
        averageGreater = mycolTeams.find(
            queryGreater).sort("programmingAverage", 1).limit(2)
        averageLesser = mycolTeams.find(
            queryLesser).sort("programmingAverage", -1).limit(2)
        return averageGreater, averageLesser

    def specialChars5(self, myTeamAverage):
        queryGreater = {
            "programmingTopScore": {
                "$gt": myTeamAverage
            }
        }
        queryLesser = {
            "programmingTopScore": {
                "$lt": myTeamAverage
            }
        }
        averageGreater = mycolTeams.find(
            queryGreater).sort("programmingTopScore", 1).limit(2)
        averageLesser = mycolTeams.find(
            queryLesser).sort("programmingTopScore", -1).limit(2)
        return averageGreater, averageLesser

    def specialChars6(self, myTeamAverage):
        queryGreater = {
            "combinedAverage": {
                "$gt": myTeamAverage
            }
        }
        queryLesser = {
            "combinedAverage": {
                "$lt": myTeamAverage
            }
        }
        averageGreater = mycolTeams.find(
            queryGreater).sort("combinedAverage", 1).limit(2)
        averageLesser = mycolTeams.find(
            queryLesser).sort("combinedAverage", -1).limit(2)
        return averageGreater, averageLesser

    def specialChars7(self, myTeamAverage):
        queryGreater = {
            "combinedTopScore": {
                "$gt": myTeamAverage
            }
        }
        queryLesser = {
            "combinedTopScore": {
                "$lt": myTeamAverage
            }
        }
        averageGreater = mycolTeams.find(
            queryGreater).sort("combinedTopScore", 1).limit(2)
        averageLesser = mycolTeams.find(
            queryLesser).sort("combinedTopScore", -1).limit(2)
        return averageGreater, averageLesser

    def specialChars8(self, sku):
        sortKey = f"rankings.{sku}.rank" 
        queryGreater = {
            sortKey: {
                "$gt": 10
            }
        }
        queryLesser = {
            sortKey: {
                "$lt": 10
            }
        }

        averageGreater = mycolTeams.find(
            queryGreater).sort(sortKey, -1).limit(10)
        averageLesser = mycolTeams.find(
            queryLesser).sort(sortKey, 1).limit(10)

        return averageLesser, averageGreater
    
    def specialChars9(self, sku, rank):
        sortKey = f"rankings.{sku}.rank"
        queryGreater = {
            sortKey: {
                "$gt": rank
            }
        }
        queryLesser = {
            sortKey: {
                "$lt": rank
            }
        }

        averageGreater = mycolTeams.find(
            queryGreater).sort(sortKey, 1).limit(2)
        averageLesser = mycolTeams.find(
            queryLesser).sort(sortKey, 1).limit(2)

        return averageLesser, averageGreater







class getEvent():
    def __init__(self, sku, db):
        self.sku = sku
        self.db = db
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        mydb = myclient[f"{self.db}"]
        global mycolEvents
        mycolEvents = mydb["Events"]
        global event
        event = mycolEvents.find_one({"sku":self.sku})
    
    def get_name(self):
        print(event)
        return event["name"]
    
    def get_timings(self):
        return event["start"], event["end"]

    def get_divisions(self):
        return event["divisions"]

    def get_location(self):
        return event["loc_venue"], event["loc_city"], event["loc_region"], event["loc_country"]





class formatter():
    def __init__(self, input):
        self.input = input

    def matchesFormatter(self, myteam):
        if self.input != []:
            copyInput = self.input
            scoreList = []
            dateList = []
            elimScore = []
            elimDate = []
            elimRound = []
            elimSku = []
            for lt in copyInput:
                if lt["blue1"] == myteam or lt["blue2"] == myteam or lt["blue3"] == myteam:
                    score = lt["bluescore"]
                else:
                    score = lt["redscore"]
                date = lt["scheduled"]
                matchRound = lt["round"]
                sku = lt["sku"]
                if matchRound > 2:
                    elimScore.append(score)
                    elimDate.append(date)
                    elimRound.append(matchRound)
                    elimSku.append(sku)
                else:
                    scoreList.append(score)
                    dateList.append(date)
            checkDict = {}
            index = 0
            for (sku, score, date, roundMatch) in zip(elimSku, elimScore, elimDate, elimRound):
                if date not in checkDict:
                    data = {
                        3:-1,
                        4:-1,
                        5:-1,
                    }
                    data[roundMatch] = index
                    checkDict[date] = data

                elif date in checkDict:
                    checkDict[date][roundMatch] = index
                index+=1
            print(checkDict)
            sortedElimScores = []
            sortedElimDates = []
            for key, value in checkDict.items():
                for key, val in value.items():
                    sortedElimScores.append(elimScore[val])
                    sortedElimDates.append(elimDate[val])

            dt, sc = (list(t) for t in zip(*sorted(zip(dateList, scoreList))))

            xAxis = []
            yAxis = []

            xAxis.extend(dt)
            yAxis.extend(sc)
            xAxis.extend(sortedElimDates)
            yAxis.extend(sortedElimScores)

            for index, date in enumerate(xAxis):
                xAxis[index] = index

            return xAxis, yAxis
        else:
            return [0], [0]
    def skillsFormatter(self):
        copyInput = self.input
        bigList = []
        for index, event in enumerate(copyInput):
            topScore = event["score"]
            attempts = event["attempts"]
            bigList.append({
                "x": index,
                "y":topScore,
                "r":attempts*2,
            })
        
        return bigList


class Matches():
    def __init__(self, myTeamName, username):
        self.myTeamName = myTeamName
        self.username = username
        global errors
        errors = []
        global context
        context = {}
        global myTeam
        myTeam = getUserInfo(self.username, "webDB_VEX")
        global myteam
        myteam = getTeam(self.myTeamName, "webDB_VEX").get()
        global competitor1, competitor2, competitor3
        competitor1, competitor2, competitor3 = myTeam.getCompetitors()
        competitor1Query = {"number":competitor1}
        competitor2Query = {"number":competitor2}
        competitor3Query = {"number":competitor3}
        global competitor1Find
        competitor1Find = mycolTeams.find_one(competitor1Query)
        global competitor2Find
        competitor2Find = mycolTeams.find_one(competitor2Query)
        global competitor3Find
        competitor3Find = mycolTeams.find_one(competitor3Query)
        

    def lineGraphData(self):
        completeList = []
        teamsList = []
        try:
            myTeamMatches = myteam["matches"]
        except Exception as error:
            print(error)
            errors.append(error)
            
        myTeamDate, myTeamScore = formatter(
            myTeamMatches).matchesFormatter(myteam["number"])
        completeList.append(myTeamScore)
        teamsList.append("My Team")

        goal=100
        percentage = round((myteam["average"]/goal)*100)

        competitor1Date, competitor1Score = formatter(competitor1Find["matches"]).matchesFormatter(competitor1Find["number"])
        competitor2Date, competitor2Score = formatter(competitor2Find["matches"]).matchesFormatter(competitor2Find["number"])
        competitor3Date, competitor3Score = formatter(competitor3Find["matches"]).matchesFormatter(competitor3Find["number"])


        completeList.append(competitor1Score)
        completeList.append(competitor2Score)
        completeList.append(competitor3Score)

        teamsList.append(competitor1Find["number"])
        teamsList.append(competitor2Find["number"])
        teamsList.append(competitor3Find["number"])


        top10 = mycolTeams.find().sort("average", -1).limit(10)
        bottom10 = mycolTeams.find().sort("average", 1).limit(10)
 
        for team in top10:
            top10Date, top10Score = formatter(team["matches"]).matchesFormatter(team["number"])
            teamsList.append(team["number"])
            completeList.append(top10Score)

        for team in bottom10:
            try:
                bottom10Date, bottom10Score = formatter(
                    team["matches"]).matchesFormatter(team["number"])

            except Exception as e:
                bottom10Date = [0]
                bottom10Score = [0]

            teamsList.append(team["number"])
            completeList.append(bottom10Score)
        
        context.update(myteam)
        context.update({
            "percentage":percentage,
            "goal":goal,
            "xAxis":myTeamDate,
            "yAxis":completeList,
            "teams":teamsList,
        })

    def table(self, tableInput):
        if tableInput == None:
            value = "myPosition"
        else:
            value = tableInput
        fullList = []
        top10 = mycolTeams.find().sort("average", -1).limit(10)
        bottom10 = mycolTeams.find().sort("average", 1).limit(10)
  
        if "myPosition" in value:
            myPositionList=[myteam["number"], myteam["average"], myteam["country"], myteam["grade"]]
            fullList.append(myPositionList)
        if "myCompetitors" in value:
            competitor1FindList = [competitor1Find["number"], competitor1Find["average"], competitor1Find["country"], competitor1Find["grade"]]
            competitor2FindList = [competitor2Find["number"], competitor2Find["average"], competitor2Find["country"], competitor2Find["grade"]]
            competitor3FindList = [competitor3Find["number"], competitor3Find["average"], competitor3Find["country"], competitor3Find["grade"]]
            fullList.append(competitor1FindList)
            fullList.append(competitor2FindList)
            fullList.append(competitor3FindList)
        if "top10" in value:
            for team in top10:
                teamList=[team["number"], team["average"], team["country"], team["grade"]]
                fullList.append(teamList)

        if "bottom10" in value:
            for team in bottom10:
                teamList=[team["number"], team["average"], team["country"], team["grade"]]
                fullList.append(teamList)

        sorted(fullList, key = lambda x: x[1])       
        context.update({
            "tableList":fullList,
        })

    def SimilarTeams(self):
        similarAveragesGreater, similarAveragesLesser = getTeam(None, "webDB_VEX").specialChars1(myteam["average"], 2)
        count = 1
        for teams in similarAveragesGreater:
            date, score = formatter(teams["matches"]).matchesFormatter(teams["number"])
            yAxisLength = len(score)
            teamDiff = round(myteam["average"]/teams["average"]*100)
            if yAxisLength > 8:
                values = []
                points = round(yAxisLength/8)
                for numb in range(1, 9):
                    if numb != 8:
                        values.append(score[numb*points])
                    else:
                        values.append(score[-1])
            else:
                values = score
            context.update({
                f"betterTeamNumber{count}": teams["number"],
                f"betterTeamAverage{count}": teams["average"],
                f"betterTeamDiff{count}": 100-teamDiff,
                f"betterAverageTeam{count}":values,
            })
            count+=1

        count = 1
        for teams in similarAveragesLesser:
            try:
                date, score = formatter(
                    teams["matches"]).matchesFormatter(teams["number"])
                yAxisLength = len(score)
                teamDiff = round(teams["average"]/myteam["average"]*100)
                if yAxisLength > 8:
                    values = []
                    points = round(yAxisLength/8)
                    for numb in range(1, 9):
                        if numb != 8:
                            values.append(score[numb*points])
                        else:
                            values.append(score[-1])

                else:
                    values = score
                print(values)
            except:
                values = ["No Data Could Be Found"]
            
            context.update({
                f"worseTeamNumber{count}":teams["number"],
                f"worseTeamAverage{count}":teams["average"],
                f"worseTeamDiff{count}":100-teamDiff,
                f"worseAverageTeam{count}":values,
            })
            count+=1
          
    def Allmatches(self):
        copyInput = myteam["matches"]
        eventList = []
        blueScoreList = []
        redScoreList = []
        matchList = []
        resultList = []
        dateList = []
        fieldList = []
        redList = []
        blueList = []

        for lt in copyInput:
            if lt["blue1"] == myteam or lt["blue2"] == myteam or lt["blue3"] == myteam:
                score = lt["bluescore"]
                color = "blue"

                if lt["redscore"] < lt["bluescore"]:
                    win = "win"
                elif lt["redscore"] == lt["bluescore"]:
                    win = "tie"
                else:
                    win = "loss"            
            else:
                score = lt["redscore"]
                color = "red"
                if lt["redscore"] > lt["bluescore"]:
                    win = "win"
                elif lt["redscore"] == lt["bluescore"]:
                    win = "tie"
                else:
                    win = "loss"

            date = lt["scheduled"]
            matchRound = lt["round"]
            sku = lt["sku"]
            print(lt)
            event = getEvent(sku, "webDB_VEX")
            if matchRound > 2:
                print(matchRound)
                start, end = event.get_timings()
                if matchRound == 3:
                    subtractionValue = timedelta(minutes=30)
                    matchValue = "QF {0}".format(lt["matchnum"])
                if matchRound == 4:
                    subtractionValue = timedelta(minutes=20)
                    matchValue = "SM {0}".format(lt["matchnum"])
                if matchRound == 5:
                    subtractionValue = timedelta(minutes=10)
                    matchValue = "F {0}".format(lt["matchnum"])
                if matchRound == 6:
                    subtractionValue = timedelta(minutes=0)
                    matchValue = "R {0}".format(lt["matchnum"])

                matchList.append(matchValue)
                dateList.append(str(parser.parse(end)-subtractionValue))
            else:
                if matchRound == 2:
                    matchValue = "Q {0}".format(lt["matchnum"])
                if matchRound == 1:
                    matchValue = "P {0}".format(lt["matchnum"])

                matchList.append(matchValue)
                dateList.append(date)

            eventList.append(event.get_name())
            redScoreList.append(lt["redscore"])
            blueScoreList.append(lt["bluescore"])
            fieldList.append(lt["field"])
            redList.append([lt["blue1"],lt["blue2"],lt["blue3"]])
            blueList.append([lt["red1"], lt["red2"], lt["red3"]])
            resultList.append(win)
        realDate, compScoreBlue, compScoreRed, compField, compRed, compBlue, compResult, compMatch, compEvent = (list(
            t) for t in zip(*sorted(zip(dateList, blueScoreList, redScoreList, fieldList, redList, blueList, resultList, matchList, eventList))))


        compDate = []
        for date in realDate:
            d1 = parser.parse(date).strftime('%b %d %Y')
            compDate.append(d1)


        print(compMatch)
        context.update({
            "allDataTable":zip(
                compDate,
                compScoreBlue,
                compScoreRed,
                compField,
                compRed,
                compBlue,
                compResult,
                compMatch,
                compEvent
            ),
        })


    def worldMap(self, mapInfo):
        print(mapInfo)
        top10 = mycolTeams.find().sort("average", -1).limit(10)
        bottom10 = mycolTeams.find().sort("average", 1).limit(10)
        if mapInfo == "myPosition":
            mypositionData = pycountry.countries.search_fuzzy(myteam["country"])[0].alpha_2
            context.update({
                "justCountryMatches": [mypositionData],
                "allTeamData": [[myteam["country"], myteam["number"],
                                 myteam["average"], mypositionData.lower()]]
            })
        elif mapInfo == "myCompetitors":
            competitor1=pycountry.countries.search_fuzzy(competitor1Find["country"])[0].alpha_2
            competitor2=pycountry.countries.search_fuzzy(competitor2Find["country"])[0].alpha_2
            competitor3=pycountry.countries.search_fuzzy(competitor3Find["country"])[0].alpha_2
            context.update({
                "justCountryMatches": [
                    competitor1,
                    competitor2,
                    competitor3    
                ],
                "allTeamData": [
                    [competitor1Find["country"], competitor1Find["number"],
                        competitor1Find["average"], competitor1.lower()],
                    [competitor2Find["country"], competitor2Find["number"],
                        competitor2Find["average"], competitor2.lower()],
                    [competitor3Find["country"], competitor3Find["number"],
                        competitor3Find["average"], competitor3.lower()],
                ]
            })
        elif mapInfo == "top10":
            justCountry = []
            fullTeamList = []
            for team in top10:
                print(team)
                teamList = []
                countryName = pycountry.countries.search_fuzzy(team["country"])[0].alpha_2
                if team["country"] not in justCountry:
                    justCountry.append(countryName)
                teamList.append(team["country"])
                teamList.append(team["number"])
                teamList.append(team["average"])
                teamList.append(countryName.lower())
                fullTeamList.append(teamList)
            context.update({
                "justCountryMatches": justCountry,
                "allTeamData": fullTeamList,
            })
        elif mapInfo == "bottom10":
            justCountry = []
            fullTeamList = []
            for team in bottom10:
                teamList = []
                countryName = pycountry.countries.search_fuzzy(team["country"])[0].alpha_2
                if team["country"] not in justCountry:
                    justCountry.append(countryName)
                teamList.append(team["country"])
                teamList.append(team["number"])
                teamList.append(team["average"])
                teamList.append(countryName.lower())
                fullTeamList.append(teamList)
            context.update({
                "justCountryMatches": justCountry,
                "allTeamData": fullTeamList,
            })

    def get(self):
        return context


class Skills():
    def __init__(self, myTeamName, username):
        self.username = username
        self.myTeamName = myTeamName
        global errors
        errors = []
        global context
        context = {}
        global myTeam
        myTeam = getUserInfo(self.username, "webDB_VEX")
        global myteam
        myteam = getTeam(self.myTeamName, "webDB_VEX").get()
        global competitor1, competitor2, competitor3
        competitor1, competitor2, competitor3 = myTeam.getCompetitors()
        competitor1Query = {"number": competitor1}
        competitor2Query = {"number": competitor2}
        competitor3Query = {"number": competitor3}
        global competitor1Find
        competitor1Find = mycolTeams.find_one(competitor1Query)
        global competitor2Find
        competitor2Find = mycolTeams.find_one(competitor2Query)
        global competitor3Find
        competitor3Find = mycolTeams.find_one(competitor3Query)
        global driver
        driver = myteam["DriverData"]
        global programming
        programming = myteam["ProgrammingData"]
        global combined
        combined = myteam["CombinedData"]

    def topBar(self):
        skillsDriverGoal, skillsProgGoal, skillsCombinedGoal = myTeam.getSkillsGoals()
        Drivertotal = 0
        for driverData in driver:
            Drivertotal += driverData["score"]

        Programmingtotal = 0
        for programmingData in programming:
            Programmingtotal += programmingData["score"]
        
        Combinedtotal = 0
        for CombinedData in combined:
            Combinedtotal += CombinedData["score"]
        context.update({
            "team_name": myteam["team_name"],
            "skillsDriverGoal":skillsDriverGoal,
            "skillsProgGoal": skillsProgGoal,
            "skillsCombinedGoal": skillsCombinedGoal,
            "DRIVERscore": Drivertotal/len(driver),
            "PROGscore": Programmingtotal/len(programming),
            "COMBINEDscore": Combinedtotal/len(combined),
            "skillsDriverGoalTotal":  round(
                ((Drivertotal/len(driver))/int(skillsDriverGoal))*100, 1),
            "skillsProgGoalTotal": round(
                ((Programmingtotal/len(programming))/int(skillsProgGoal))*100, 1),
            "skillsCombinedGoalTotal": round(
                ((Combinedtotal/len(combined))/int(skillsCombinedGoal))*100, 1),
        })

    def driverScatterPlot(self, driverGraphInput):
        if driverGraphInput == []:
            driverGraphInput.append("myPosition")
        if "myPosition" in driverGraphInput:
            AllDriver = formatter(driver).skillsFormatter()
            team_name = myteam["number"]
            context.update({
                "driverLinePlotData": [[team_name, AllDriver]],
                "driverBarPlotData": [[team_name, [myteam["driverTopScore"]]]],
                "tableList": [[myteam["number"], myteam["driverTopScore"], round(myteam["driverAverage"], 1)]],
            })

        if "myCompetitors" in driverGraphInput:
            Competitor1Driver = formatter(
                competitor1Find["DriverData"]).skillsFormatter()
            Competitor2Driver = formatter(
                competitor2Find["DriverData"]).skillsFormatter()
            Competitor3Driver = formatter(
                competitor3Find["DriverData"]).skillsFormatter()

            context.update({
                "driverLinePlotData": [
                    [competitor1Find["number"], Competitor1Driver],
                    [competitor2Find["number"], Competitor2Driver],
                    [competitor3Find["number"], Competitor3Driver],
                ],
                "tableList": [
                    [competitor1Find["number"],
                     competitor1Find["driverTopScore"], round(competitor1Find["driverAverage"], 1)],
                    [competitor2Find["number"],
                     competitor2Find["driverTopScore"], round(competitor2Find["driverAverage"], 1)],
                    [competitor3Find["number"],
                     competitor3Find["driverTopScore"], round(competitor3Find["driverAverage"], 1)],
                ],
                "driverBarPlotData": [
                    [competitor1Find["number"], [competitor1Find["driverTopScore"]]],
                    [competitor2Find["number"], [competitor2Find["driverTopScore"]]],
                    [competitor3Find["number"], [competitor3Find["driverTopScore"]]],
                ],
            })

           
        if "top10" in driverGraphInput:
            top10 = mycolTeams.find().sort("average", -1).limit(10)

            graphList = []
            tableList = []
            teamBarList = []
            for team in top10:
                teamDriver = formatter(
                team["DriverData"]).skillsFormatter()
                graphList.append([
                    team["number"], teamDriver
                ])
                tableList.append([
                    team["number"], team["driverTopScore"], round(team["driverAverage"], 1)
                ])
                teamBarList.append([
                    team["number"], [team["driverTopScore"]]
                ])

            context.update({
                "driverLinePlotData": graphList,
                "tableList":tableList,
                "driverBarPlotData": teamBarList,
            })

        if "bottom10" in driverGraphInput:
            bottom10 = mycolTeams.find().sort("average", 1).limit(10)
            graphList = []
            tableList = []
            teamBarList = []
            for team in bottom10:
                try:
                    teamDriver = formatter(
                team["DriverData"]).skillsFormatter()
                except:
                    teamDriver=0
                    teamAverage=0
                    teamtopScore=0
                graphList.append([
                    team["number"], teamDriver
                ])
                tableList.append([
                    team["number"], team["driverTopScore"], round(team["driverAverage"], 1)
                ])
                teamBarList.append([
                    team["number"], [team["driverTopScore"]]
                ])
            context.update({
                "driverLinePlotData": graphList,
                "tableList":tableList,
                "driverBarPlotData": teamBarList,
            })


        similarAveragesGreater, similarAveragesLesser = getTeam(None, "webDB_VEX").specialChars2(myteam["driverAverage"])
        count = 1
        for teams in similarAveragesGreater:
            teamDriver = formatter(teams["DriverData"]).skillsFormatter()
            yAxisLength = len(teamDriver)
            teamDiff = round(myteam["driverAverage"] /
                             teams["driverAverage"]*100)
            values = []
            if yAxisLength > 8:
                points = round(yAxisLength/8)
                for numb in range(1, 9):
                    if numb != 8:
                        values.append(score[numb*points])
                    else:
                        values.append(score[-1])
            else:
                for roundNumber in teamDriver:
                    values.append(roundNumber["y"])
                if yAxisLength == 1:
                    values.append(0)
                
            context.update({
                f"betterDriverTeamNumber{count}": teams["number"],
                f"betterDriverTeamAverage{count}": teams["driverAverage"],
                f"betterDriverTeamDiff{count}": 100-teamDiff,
                f"betterDriverAverageTeam{count}": values,
            })
            count += 1

        count = 1
        for teams in similarAveragesLesser:
            teamDriver = formatter(
                teams["DriverData"]).skillsFormatter()
            yAxisLength = len(teamDriver)
            teamDiff = round(teams["driverAverage"]/myteam["driverAverage"]*100)
            values = []
            if yAxisLength > 8:
                points = round(yAxisLength/8)
                for numb in range(1, 9):
                    if numb != 8:
                        values.append(score[numb*points])
                    else:
                        values.append(score[-1])
            else:
                for roundNumber in teamDriver:
                    values.append(roundNumber["y"])
                if yAxisLength == 1:
                    values.append(0)

            context.update({
                f"worseDriverTeamNumber{count}": teams["number"],
                f"worseDriverTeamAverage{count}": teams["driverAverage"],
                f"worseDriverTeamDiff{count}": 100-teamDiff,
                f"worseDriverAverageTeam{count}": values,
            })
            count += 1


        similarAveragesGreater, similarAveragesLesser = getTeam(
    None, "webDB_VEX").specialChars3(myteam["driverTopScore"])

        count = 1
        for teams in similarAveragesGreater:
            teamtopScore = teams["driverTopScore"]
            teamDiff = round(teams["driverTopScore"] /
                             myteam["driverTopScore"]*100)

            context.update({
                f"betterDriverTeamNumbertopScore{count}": teams["number"],
                f"betterDriverTeamtopScore{count}": teamtopScore,
                f"betterDriverTeamDifftopScore{count}": teamDiff-100,
                f"betterDriverAverageTeamtopScore{count}": [
                    [teams["number"], [teams["driverTopScore"]]],
                    [myteam["number"], [myteam["driverTopScore"]]]
                ],
            })
            count += 1

        count = 1
        for teams in similarAveragesLesser:
            teamtopScore = teams["driverTopScore"]
            teamDiff = round(myteam["driverTopScore"] /
                             teams["driverTopScore"]*100)

            context.update({
                f"worseDriverTeamNumbertopScore{count}": teams["number"],
                f"worseDriverTeamtopScore{count}": teamtopScore,
                f"worseDriverTeamDifftopScore{count}": teamDiff-100,
                f"worseDriverAverageTeamtopScore{count}": [
                    [teams["number"], [teams["driverTopScore"]]],
                    [myteam["number"], [myteam["driverTopScore"]]]
                ],
            })
            count += 1
            
        context.update({
            "myDriverTopScore": myteam["driverTopScore"],
            "myDriverAverage": myteam["driverAverage"]
        })
    #     print(Competitor1Driver)

    def programmingScatterPlot(self, programmingGraphInput):
        if programmingGraphInput == []:
            programmingGraphInput.append("myPosition")
        if "myPosition" in programmingGraphInput:
            Allprogramming = formatter(programming).skillsFormatter()
            team_name = myteam["number"]
            context.update({
                "programmingLinePlotData": [[team_name, Allprogramming]],
                "programmingBarPlotData": [[team_name, [myteam["programmingTopScore"]]]],
                "tableListProgramming": [[myteam["number"], myteam["programmingTopScore"], round(myteam["programmingAverage"], 1)]],
            })

        if "myCompetitors" in programmingGraphInput:
            Competitor1programming = formatter(
                competitor1Find["ProgrammingData"]).skillsFormatter()
            Competitor2programming = formatter(
                competitor2Find["ProgrammingData"]).skillsFormatter()
            Competitor3programming = formatter(
                competitor3Find["ProgrammingData"]).skillsFormatter()

            context.update({
                "programmingLinePlotData": [
                    [competitor1Find["number"], Competitor1programming],
                    [competitor2Find["number"], Competitor2programming],
                    [competitor3Find["number"], Competitor3programming],
                ],
                "tableListProgramming": [
                    [competitor1Find["number"],
                     competitor1Find["programmingTopScore"], round(competitor1Find["programmingAverage"], 1)],
                    [competitor2Find["number"],
                     competitor2Find["programmingTopScore"], round(competitor2Find["programmingAverage"], 1)],
                    [competitor3Find["number"],
                     competitor3Find["programmingTopScore"], round(competitor3Find["programmingAverage"], 1)],
                ],
                "programmingBarPlotData": [
                    [competitor1Find["number"], [
                        competitor1Find["programmingTopScore"]]],
                    [competitor2Find["number"], [
                        competitor2Find["programmingTopScore"]]],
                    [competitor3Find["number"], [
                        competitor3Find["programmingTopScore"]]],
                ],
            })

        if "top10" in programmingGraphInput:
            top10 = mycolTeams.find().sort("average", -1).limit(10)

            graphList = []
            tableList = []
            teamBarList = []
            for team in top10:
                teamprogramming = formatter(
                    team["ProgrammingData"]).skillsFormatter()
                graphList.append([
                    team["number"], teamprogramming
                ])
                tableList.append([
                    team["number"], team["programmingTopScore"], round(team["programmingAverage"], 1)
                ])
                teamBarList.append([
                    team["number"], [team["programmingTopScore"]]
                ])

            context.update({
                "programmingLinePlotData": graphList,
                "tableListProgramming": tableList,
                "programmingBarPlotData": teamBarList,
            })

        if "bottom10" in programmingGraphInput:
            bottom10 = mycolTeams.find().sort("average", 1).limit(10)

            graphList = []
            tableList = []
            teamBarList = []
            for team in bottom10:
                try:
                    teamprogramming = formatter(
                        team["ProgrammingData"]).skillsFormatter()
                except:
                    teamprogramming = 0
                    teamAverage = 0
                    teamtopScore = 0
                graphList.append([
                    team["number"], teamprogramming
                ])
                tableList.append([
                    team["number"], team["programmingTopScore"], round(teamAverage, 1)
                ])
                teamBarList.append([
                    team["number"], [team["programmingTopScore"]]
                ])
            context.update({
                "programmingLinePlotData": graphList,
                "tableListProgramming": tableList,
                "programmingBarPlotData": teamBarList,
            })
        similarAveragesGreater, similarAveragesLesser = getTeam(
            None, "webDB_VEX").specialChars4(myteam["programmingAverage"])

        count = 1
        for teams in similarAveragesGreater:
            teamProgramming = formatter(
            teams["ProgrammingData"]).skillsFormatter()
            yAxisLength = len(teamProgramming)
            teamDiff = round(myteam["programmingAverage"] /
                            teams["programmingAverage"]*100)
            values = []
            if yAxisLength > 8:
                points = round(yAxisLength/8)
                for numb in range(1, 9):
                    if numb != 8:
                        values.append(score[numb*points])
                    else:
                        values.append(score[-1])
            else:
                for roundNumber in teamProgramming:
                    values.append(roundNumber["y"])
                if yAxisLength == 1:
                    values.append(0)
            
            context.update({
                f"betterProgrammingTeamNumber{count}": teams["number"],
                f"betterProgrammingTeamAverage{count}": round(teams["programmingAverage"], 1),
                f"betterProgrammingTeamDiff{count}": 100-teamDiff,
                f"betterProgrammingAverageTeam{count}": values,
            })
            count += 1

        count = 1
        for teams in similarAveragesLesser:
            teamProgramming = formatter(
                teams["ProgrammingData"]).skillsFormatter()
            yAxisLength = len(teamProgramming)
            teamDiff = round(teams["programmingAverage"] /
                             myteam["programmingAverage"]*100)
            values = []
            if yAxisLength > 8:
                points = round(yAxisLength/8)
                for numb in range(1, 9):
                    if numb != 8:
                        values.append(teamProgramming[numb*points]["y"])
                    else:
                        values.append(teamProgramming[-1]["y"])
            else:
                for roundNumber in teamProgramming:
                    values.append(roundNumber["y"])
                if yAxisLength == 1:
                    values.append(0)
            
            context.update({
                f"worseProgrammingTeamNumber{count}": teams["number"],
                f"worseProgrammingTeamAverage{count}": round(teams["programmingAverage"], 1),
                f"worseProgrammingTeamDiff{count}": 100-teamDiff,
                f"worseProgrammingAverageTeam{count}": values,
            })
            count += 1


        similarAveragesGreater, similarAveragesLesser = getTeam(
            None, "webDB_VEX").specialChars5(myteam["programmingTopScore"])

        count = 1
        for teams in similarAveragesGreater:
            teamtopScore = teams["programmingTopScore"]
            teamDiff = round(teams["programmingTopScore"] /
                        myteam["programmingTopScore"]*100)

            context.update({
                f"betterProgrammingTeamNumbertopScore{count}": teams["number"],
                f"betterProgrammingTeamtopScore{count}": teamtopScore,
                f"betterProgrammingTeamDifftopScore{count}": teamDiff-100,
                f"betterProgrammingAverageTeamtopScore{count}": [
                    [teams["number"], [teams["programmingTopScore"]]],
                    [myteam["number"], [myteam["programmingTopScore"]]]
                ],
            })
            count += 1

        count = 1
        for teams in similarAveragesLesser:
            teamtopScore = teams["programmingTopScore"]
            teamDiff = round(myteam["programmingTopScore"] /
                            teams["programmingTopScore"]*100)

            context.update({
                f"worseProgrammingTeamNumbertopScore{count}": teams["number"],
                f"worseProgrammingTeamtopScore{count}": teamtopScore,
                f"worseProgrammingTeamDifftopScore{count}": teamDiff-100,
                f"worseProgrammingAverageTeamtopScore{count}": [
                    [teams["number"], [teams["programmingTopScore"]]],
                    [myteam["number"], [myteam["programmingTopScore"]]]
                ],
            })
            count += 1

        context.update({
            "myProgrammingTopScore": myteam["programmingTopScore"],
            "myProgrammingAverage": myteam["programmingAverage"]
        })

    def combinedScatterPlot(self, combinedGraphInput):
        if combinedGraphInput == []:
            combinedGraphInput.append("myPosition")
        if "myPosition" in combinedGraphInput:
            Allcombined = formatter(combined).skillsFormatter()
            team_name = myteam["number"]
            context.update({
                "combinedLinePlotData": [[team_name, Allcombined]],
                "combinedBarPlotData": [[team_name, [myteam["combinedTopScore"]]]],
                "tableListcombined": [[myteam["number"], myteam["combinedTopScore"], round(myteam["combinedAverage"], 1)]],
            })

        if "myCompetitors" in combinedGraphInput:
            Competitor1combined = formatter(
                competitor1Find["CombinedData"]).skillsFormatter()
            Competitor2combined = formatter(
                competitor2Find["CombinedData"]).skillsFormatter()
            Competitor3combined = formatter(
                competitor3Find["CombinedData"]).skillsFormatter()

            context.update({
                "combinedLinePlotData": [
                    [competitor1Find["number"], Competitor1combined],
                    [competitor2Find["number"], Competitor2combined],
                    [competitor3Find["number"], Competitor3combined],
                ],
                "tableListcombined": [
                    [competitor1Find["number"],
                    competitor1Find["combinedTopScore"], round(competitor1Find["combinedAverage"], 1)],
                    [competitor2Find["number"],
                    competitor2Find["combinedTopScore"], round(competitor2Find["combinedAverage"], 1)],
                    [competitor3Find["number"],
                    competitor3Find["combinedTopScore"], round(competitor3Find["combinedAverage"], 1)],
                ],
                "combinedBarPlotData": [
                    [competitor1Find["number"], [
                        competitor1Find["combinedTopScore"]]],
                    [competitor2Find["number"], [
                        competitor2Find["combinedTopScore"]]],
                    [competitor3Find["number"], [
                        competitor3Find["combinedTopScore"]]],
                ],
            })

        if "top10" in combinedGraphInput:
            top10 = mycolTeams.find().sort("average", -1).limit(10)

            graphList = []
            tableList = []
            teamBarList = []
            for team in top10:
                teamcombined = formatter(
                    team["CombinedData"]).skillsFormatter()
                graphList.append([
                    team["number"], teamcombined
                ])
                tableList.append([
                    team["number"], team["combinedTopScore"], round(team["combinedAverage"], 1)
                ])
                teamBarList.append([
                    team["number"], [team["combinedTopScore"]]
                ])

            context.update({
                "combinedLinePlotData": graphList,
                "tableListCombined": tableList,
                "combinedBarPlotData": teamBarList,
            })

        if "bottom10" in combinedGraphInput:
            bottom10 = mycolTeams.find().sort("average", 1).limit(10)

            graphList = []
            tableList = []
            teamBarList = []
            for team in bottom10:
                try:
                    teamcombined = formatter(
                    team["CombinedData"]).skillsFormatter()
                except:
                    teamcombined = 0
                    teamAverage = 0
                    teamtopScore = 0

                graphList.append([
                    team["number"], teamcombined
                ])
                tableList.append([
                    team["number"], team["combinedTopScore"], round(teamAverage, 1)
                ])
                teamBarList.append([
                    team["number"], [team["combinedTopScore"]]
                ])

            context.update({
                "combinedLinePlotData": graphList,
                "tableListCombined": tableList,
                "combinedBarPlotData": teamBarList,
            })
        similarAveragesGreater, similarAveragesLesser = getTeam(
            None, "webDB_VEX").specialChars6(myteam["combinedAverage"])


        count = 1
        for teams in similarAveragesGreater:
            teamCombined = formatter(
                teams["CombinedData"]).skillsFormatter()
            yAxisLength = len(teamCombined)
            teamDiff = round(myteam["combinedAverage"] /
                            teams["combinedAverage"]*100)
            values = []
            if yAxisLength > 8:
                points = round(yAxisLength/8)
                for numb in range(1, 9):
                    if numb != 8:
                        values.append(score[numb*points])
                    else:
                        values.append(score[-1])
            else:
                for roundNumber in teamCombined:
                    values.append(roundNumber["y"])
                if yAxisLength == 1:
                    values.append(0)

            context.update({
                f"betterCombinedTeamNumber{count}": teams["number"],
                f"betterCombinedTeamAverage{count}": round(teams["combinedAverage"], 1),
                f"betterCombinedTeamDiff{count}": 100-teamDiff,
                f"betterCombinedAverageTeam{count}": values,
            })
            count += 1

        count = 1
        for teams in similarAveragesLesser:
            teamCombined = formatter(
                teams["CombinedData"]).skillsFormatter()
            yAxisLength = len(teamCombined)
            teamDiff = round(teams["combinedAverage"] /
                            myteam["combinedAverage"]*100)
            values = []
            if yAxisLength > 8:
                points = round(yAxisLength/8)
                for numb in range(1, 9):
                    if numb != 8:
                        values.append(teamCombined[numb*points]["y"])
                    else:
                        values.append(teamCombined[-1]["y"])
            else:
                for roundNumber in teamCombined:
                    values.append(roundNumber["y"])
                if yAxisLength == 1:
                    values.append(0)

            context.update({
                f"worseCombinedTeamNumber{count}": teams["number"],
                f"worseCombinedTeamAverage{count}": round(teams["combinedAverage"], 1),
                f"worseCombinedTeamDiff{count}": 100-teamDiff,
                f"worseCombinedAverageTeam{count}": values,
            })
            count += 1


        similarAveragesGreater, similarAveragesLesser = getTeam(
            None, "webDB_VEX").specialChars7(myteam["combinedTopScore"])

        count = 1
        for teams in similarAveragesGreater:
            teamtopScore = teams["combinedTopScore"]
            teamDiff = round(teams["combinedTopScore"] /
                            myteam["combinedTopScore"]*100)

            context.update({
                f"betterCombinedTeamNumbertopScore{count}": teams["number"],
                f"betterCombinedTeamtopScore{count}": teamtopScore,
                f"betterCombinedTeamDifftopScore{count}": teamDiff-100,
                f"betterCombinedAverageTeamtopScore{count}": [
                    [teams["number"], [teams["combinedTopScore"]]],
                    [myteam["number"], [myteam["combinedTopScore"]]]
                ],
            })
            count += 1

        count = 1
        for teams in similarAveragesLesser:
            teamtopScore = teams["combinedTopScore"]
            teamDiff = round(myteam["combinedTopScore"] /
                            teams["combinedTopScore"]*100)

            context.update({
                f"worseCombinedTeamNumbertopScore{count}": teams["number"],
                f"worseCombinedTeamtopScore{count}": teamtopScore,
                f"worseCombinedTeamDifftopScore{count}": teamDiff-100,
                f"worseCombinedAverageTeamtopScore{count}": [
                    [teams["number"], [teams["combinedTopScore"]]],
                    [myteam["number"], [myteam["combinedTopScore"]]]
                ],
            })
            count += 1

        context.update({
            "myCombinedTopScore": myteam["combinedTopScore"],
            "myCombinedAverage": myteam["combinedAverage"]
        })

    def worldMap(self, mapInfo, mapInfoType):
        if "driver" in mapInfoType:
            averageType = "driverAverage"
            topScoreType = "driverTopScore"
        elif "programming" in mapInfoType:
            averageType = "programmingAverage"
            topScoreType = "programmingTopScore"
        elif "combined" in mapInfoType:
            averageType = "combinedAverage"
            topScoreType = "combinedTopScore"
        else:
            averageType = "driverAverage"
            topScoreType = "driverTopScore"

        top10 = mycolTeams.find().sort(averageType, -1).limit(10) 
        bottom10 = mycolTeams.find().sort(averageType, 1).limit(10)
        if mapInfo == []:
            mapInfo.append("myPosition")
        if mapInfo == "myPosition":
            mypositionData = pycountry.countries.search_fuzzy(myteam["country"])[
                0].alpha_2
            context.update({
                "justCountrySkills": [mypositionData],
                "allTeamData": [[myteam["country"], myteam["number"],
                                 round(myteam[averageType], 1), mypositionData.lower(), myteam[topScoreType]]]
            })
        elif "myCompetitors" in mapInfo:
            competitor1 = pycountry.countries.search_fuzzy(
                competitor1Find["country"])[0].alpha_2
            competitor2 = pycountry.countries.search_fuzzy(
                competitor2Find["country"])[0].alpha_2
            competitor3 = pycountry.countries.search_fuzzy(
                competitor3Find["country"])[0].alpha_2
            context.update({
                "justCountrySkills": [
                    competitor1,
                    competitor2,
                    competitor3
                ],
                "allTeamData": [
                    [competitor1Find["country"], competitor1Find["number"],
                        round(competitor1Find[averageType], 1), competitor1.lower(), competitor1Find[topScoreType]],
                    [competitor2Find["country"], competitor2Find["number"],
                        round(competitor2Find[averageType], 1), competitor2.lower(), competitor2Find[topScoreType]],
                    [competitor3Find["country"], competitor3Find["number"],
                        round(competitor3Find[averageType], 1), competitor3.lower(), competitor3Find[topScoreType]],
                ]
            })

        elif "top10" in mapInfo:
            justCountry = []
            fullTeamList = []
            for team in top10:
                teamList = []
                countryName = pycountry.countries.search_fuzzy(team["country"])[
                    0].alpha_2
                if team["country"] not in justCountry:
                    justCountry.append(countryName)
                teamList.append(team["country"])
                teamList.append(team["number"])
                teamList.append(round(team[averageType], 1))
                teamList.append(countryName.lower())
                teamList.append(team[topScoreType])
                fullTeamList.append(teamList)
            context.update({
                "justCountrySkills": justCountry,
                "allTeamData": fullTeamList,
            })
        elif "bottom10" in mapInfo:
            justCountry = []
            fullTeamList = []
            for team in bottom10:
                teamList = []
                countryName = pycountry.countries.search_fuzzy(team["country"])[
                    0].alpha_2
                if team["country"] not in justCountry:
                    justCountry.append(countryName)
                teamList.append(team["country"])
                teamList.append(team["number"])
                teamList.append(round(team[averageType], 1))
                teamList.append(countryName.lower())
                teamList.append(team[topScoreType])
                fullTeamList.append(teamList)

            context.update({
                "justCountrySkills": justCountry,
                "allTeamData": fullTeamList,
            })

    def get(self):
        return context



class Rankings():
    def __init__(self, myTeamName, username):
        self.username=username
        self.myTeamName=myTeamName
        global errors
        errors = []
        global context
        context = {}
        global myTeam
        myTeam = getUserInfo(self.username, "webDB_VEX")
        global myteam
        myteam = getTeam(self.myTeamName, "webDB_VEX").get()
        global competitor1, competitor2, competitor3
        competitor1, competitor2, competitor3 = myTeam.getCompetitors()
        competitor1Query = {"number":competitor1}
        competitor2Query = {"number":competitor2}
        competitor3Query = {"number":competitor3}
        global competitor1Find
        competitor1Find = mycolTeams.find_one(competitor1Query)
        global competitor2Find
        competitor2Find = mycolTeams.find_one(competitor2Query)
        global competitor3Find
        competitor3Find = mycolTeams.find_one(competitor3Query)
        

    def navigator(self):
        navListName=[]
        navListSku=[]
        for key, value in myteam["rankings"].items():
            event = getEvent(key, "webDB_VEX").get_name()
            navListName.append(event)
            navListSku.append(key)
        context.update({
            "team_name": myteam["team_name"],
            "topBarList":zip(navListName, navListSku)
        })

    def showGraphs(self, sku, inputData):
        top10, bottom10 = getTeam(None, "webDB_VEX").specialChars8(sku)
        rankingsData = myteam["rankings"][sku]
        if "myPosition" in inputData:
            data = [
                rankingsData["wins"],
                rankingsData["losses"],
                rankingsData["ties"],
                rankingsData["ap"],
                rankingsData["wp"],
                rankingsData["sp"],
                rankingsData["max_score"],
                rankingsData["opr"],
                rankingsData["dpr"],
                rankingsData["trsp"],
                rankingsData["ccwm"],
                rankingsData["rank"],
            ]
            tableData = [myteam["number"], rankingsData["rank"],rankingsData["wins"],rankingsData["losses"],rankingsData["ties"],rankingsData["ap"],rankingsData["wp"],rankingsData["sp"],rankingsData["max_score"],rankingsData["opr"],rankingsData["dpr"],rankingsData["trsp"],rankingsData["ccwm"]]
            context.update({
                "barGraphData":[[myteam["number"], data]],
                "tableData":tableData,
            })
        elif "top10" in inputData:
            allData = []
            tableData = []
            for team in top10:
                teamer = team["rankings"][sku]
                data = [
                    teamer["wins"],
                    teamer["losses"],
                    teamer["ties"],
                    teamer["ap"],
                    teamer["wp"],
                    teamer["sp"],
                    teamer["max_score"],
                    teamer["opr"],
                    teamer["dpr"],
                    teamer["trsp"],
                    teamer["ccwm"],
                    teamer["rank"],
                ]
                allData.append([team["number"], data])
                tableData.append([team["number"], teamer["rank"],teamer["wins"],teamer["losses"],teamer["ties"],teamer["ap"],teamer["wp"],teamer["sp"],teamer["max_score"],teamer["opr"],teamer["dpr"],teamer["trsp"],teamer["ccwm"]])

            context.update({
                "barGraphData":allData,
                "tableData":tableData,
            })
        elif "bottom10" in inputData: 
            tableData = []
            allData = []
            for team in bottom10:
                teamer = team["rankings"][sku]
                data = [
                    teamer["wins"],
                    teamer["losses"],
                    teamer["ties"],
                    teamer["ap"],
                    teamer["wp"],
                    teamer["sp"],
                    teamer["max_score"],
                    teamer["opr"],
                    teamer["dpr"],
                    teamer["trsp"],
                    teamer["ccwm"],
                    teamer["rank"],
                ]
                allData.append([team["number"], data])
                tableData.append([team["number"], teamer["rank"],teamer["wins"],teamer["losses"],teamer["ties"],teamer["ap"],teamer["wp"],teamer["sp"],teamer["max_score"],teamer["opr"],teamer["dpr"],teamer["trsp"],teamer["ccwm"],teamer["rank"]])

            context.update({
                "barGraphData": allData,
                "tableData":tableData,
            })
        
        betterTeams, worseTeams = getTeam(
            None, "webDB_VEX").specialChars9(sku, rankingsData["rank"])

        betterTeamsFullData = []
        worseTeamsFullData = []
        for better in betterTeams:
            betterInstance = better["rankings"][sku]
            betterTeamsFullData.append([
                better["number"],
                [
                    betterInstance["wins"],
                    betterInstance["losses"],
                    betterInstance["ties"],
                    betterInstance["ap"],
                    betterInstance["wp"],
                    betterInstance["sp"],
                    betterInstance["max_score"],
                    betterInstance["opr"],
                    betterInstance["dpr"],
                    betterInstance["trsp"],
                    betterInstance["ccwm"],
                    betterInstance["rank"],
                ]
            ])
      
        for worse in worseTeams:
            worseInstance = worse["rankings"][sku]
            worseTeamsFullData.append([
                worse["number"],
                [
                    worseInstance["wins"],
                    worseInstance["losses"],
                    worseInstance["ties"],
                    worseInstance["ap"],
                    worseInstance["wp"],
                    worseInstance["sp"],
                    worseInstance["max_score"],
                    worseInstance["opr"],
                    worseInstance["dpr"],
                    worseInstance["trsp"],
                    worseInstance["ccwm"],
                    worseInstance["rank"],
                ]
            ])
        
        
        
        context.update({
            "barLabels":["wins","losses","ties","ap","wp","sp","max_score","opr","dpr","trsp","ccwm","rank"],
            "betterTeamData1": [betterTeamsFullData[0]] if betterTeamsFullData != [] else [],
            "betterTeamData2": [betterTeamsFullData[1]] if betterTeamsFullData != [] else [],
            "worseTeamData1": [worseTeamsFullData[0]] if worseTeamsFullData != [] else [],
            "worseTeamData2": [worseTeamsFullData[1]] if worseTeamsFullData != [] else [],
            "betterTeamData":betterTeamsFullData,
            "worseTeamData":worseTeamsFullData,
        })


    def worldMap(self, sku):
        venue, city, region, country = getEvent(sku, "webDB_VEX").get_location()
        act_location = pycountry.countries.search_fuzzy(str(country))[0].alpha_2
        context.update({
            "justCountryRankings":[act_location]
        })
    def get(self):
        return context


class teamSearchMain():
    def __init__(self, myTeamName, username):
        self.username=username
        self.myTeamName=myTeamName
        global errors
        errors = []
        global context
        context = {}
        global myTeam
        myTeam = getUserInfo(self.username, "webDB_VEX")
        global myteam
        myteam = getTeam(self.myTeamName, "webDB_VEX").get()
        
    def first(self):        
        betterTeams, worseTeams = getTeam(self.myTeamName, "webDB_VEX").specialChars1(myteam["average"], 7)
        betterTeamList = []
        worseTeamList = []
        mixTeamList = []
        for count, team in enumerate(betterTeams):
            listAppend = [
                    team["number"],
                    True,
                    team["average"],
                    team["driverTopScore"],
                    team["programmingTopScore"],
                    team["country"],
                    team["grade"],
                    team["team_name"]
                ]
            if count < 2:
                mixTeamList.append(listAppend)
            else:
                betterTeamList.append(listAppend)

        for count, team in enumerate(worseTeams):
            listAppend = [
                team["number"],
                False,
                team["average"],
                team["driverTopScore"],
                team["programmingTopScore"],
                team["country"],
                team["grade"],
                team["team_name"]
            ]
            if count < 2:
                mixTeamList.append(listAppend)
            else:
                worseTeamList.append(listAppend)

        mixTeamList.append([
            myteam["number"],
            "1",
            myteam["average"],
            myteam["driverTopScore"],
            myteam["programmingTopScore"],
            myteam["country"],
            myteam["grade"],
            myteam["team_name"]
        ])

        mixTeamList.sort(key=operator.itemgetter(2), reverse=True)
        worseList = reversed(worseTeamList)
      
        context.update({
            "betterList":betterTeamList,
            "worseList":list(worseList),
            "mixedList":list(reversed(mixTeamList)),
        })

    def get(self):
        return context




class chat():
    def __init__(self, username):
        self.username = username
        global myTeam
        myTeam = getUserInfo(self.username, "webDB_VEX")
        global context
        context={}
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        mydb = myclient[f"webDB_VEX"]
        global mycolchat
        mycolchat = mydb["Chat"]
        global mycolAuthUser
        mycolAuthUser = mydb["auth_user"]



    def create(self):
        randomID = get_random_string(6).lower()
        mycolchat.insert_one({
            "chatId":randomID,
            "contacts": [self.username]
        })

    def join(self, val):
        query = {"chatId":val}
        contacts = mycolchat.find_one(query)
        try:
            if self.username not in contacts['contacts']:
                mycolchat.update_one(query,  {'$push': {'contacts': self.username}})
        except:
            pass

    def sendMessage(self, message, person):
        if person == "":
            allChat = mycolchat.find({ "contacts": { "$in" : [self.username]} })
            for chat in allChat:
                person = chat["chatId"]
                break
        mycolchat.update_one({"chatId":person},{'$push': {'messages': {
            "user":self.username,
            "content": [
                datetime.datetime.today(),
                message
            ]
        }}})

    def invite(self, member, code):
        print(code)
        if member != self.username:
            email = mycolAuthUser.find_one({"username":member})
            if email:
                actEmail = email["email"]
                send_mail(
                    'Vex Dashboard',
                    f'{self.username} has invited you to a chat. Here is the code: {code}',
                    'dashboardvex@gmail.com',
                    [actEmail],
                    fail_silently=True,
                )

    def load(self):
        allChat = mycolchat.find({ "contacts": { "$in" : [self.username]} })
        chatIDList = []
        contactsList = []
        messageList = []
        profileList = []
        lastMessageList = []
        for chat in allChat:
            copyInput=chat["contacts"]
            chatIDList.append(chat["chatId"])
            contactsList.append(chat["contacts"])
            try:
                messageList.append(chat["messages"])
            except:
                messageList.append([])
            try:
                myplace = copyInput.index(self.username)
                diff = 0
                if myplace == 1:
                    diff=0
                elif myplace == 0:
                    diff=1
                profilePic=mycolUserInfo.find_one({"username":copyInput[diff]})['profilePic']
                status = mycolAuthUser.find_one(
                    {"username": copyInput[0]})['is_active']
                profileList.append([profilePic, status])
                lastMessageContent=chat["messages"][-1]['content'][1]
                lastMessageList.append([lastMessageContent])
            except:
                profileList.append([])
                lastMessageList.append([])
        myProfile =             profilePic=mycolUserInfo.find_one({"username":self.username})['profilePic']
        
        print(contactsList)
        context.update({
            "zippedData":list(zip(chatIDList,contactsList,messageList, profileList, lastMessageList)),
            "myProfile":myProfile,
            "allContacts": chatIDList,
        })

    def get(self):
        return context
            
        
class calendar():
    def __init__(self, username, db):
        self.username = username
        self.db = db
        global context
        context = {}
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        mydb = myclient[f"{self.db}"]
        global mycolUserInfo
        mycolUserInfo = mydb["userInfo"]
        global myTeam
        myTeam = getUserInfo(self.username, "webDB_VEX")   
                 

    def insert(self, data):
        mycolUserInfo.update_one({"username":self.username},{
            "$set": {"calendar": []}
        })
            
    def add(self, data):
        mycolUserInfo.update_one({"username": self.username}, {
            "$push": {"calendar": data}
        })
    def load(self):
        print("load")
        if myTeam.getCalendar() != False:
            context.update({
                "events":mycolUserInfo.find_one({"username":self.username})["calendar"]
            })
        else:
            context.update({
                "events": []
            })
    
    def get(self):
        return context


class homePage():
    def __init__(self, myTeamName, username):
        self.username = username
        self.myTeamName = myTeamName
        global errors
        errors = []
        global context
        context = {}
        global myTeam
        myTeam = getUserInfo(self.username, "webDB_VEX")
        global myteam
        myteam = getTeam(self.myTeamName, "webDB_VEX").get()
        global competitor1, competitor2, competitor3
        competitor1, competitor2, competitor3 = myTeam.getCompetitors()
        competitor1Query = {"number": competitor1}
        competitor2Query = {"number": competitor2}
        competitor3Query = {"number": competitor3}
        global competitor1Find
        competitor1Find = mycolTeams.find_one(competitor1Query)
        global competitor2Find
        competitor2Find = mycolTeams.find_one(competitor2Query)
        global competitor3Find
        competitor3Find = mycolTeams.find_one(competitor3Query)
        global driver
        driver = myteam["DriverData"]
        global programming
        programming = myteam["ProgrammingData"]
        global combined
        combined = myteam["CombinedData"]
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        mydb = myclient["webDB_VEX"]
        global mycolEvents
        mycolEvents = mydb["Events"]
        global mycolUserInfo
        mycolUserInfo = mydb["userInfo"]
        global mycolchat
        mycolchat = mydb["Chat"]
        global mycolAuthUser
        mycolAuthUser = mydb["auth_user"]
       

    def topBar(self):
        matchGoals = myTeam.getMatchesGoals()
        skillsGoals = myTeam.getSkillsGoals()

        matchesAverage = round(myteam["average"]/int(matchGoals[0])*100, 2)
        skillsDriver = round(myteam["driverAverage"]/int(skillsGoals[0])*100, 2)
        skillsProgramming = round(myteam["programmingAverage"]/int(skillsGoals[1])*100, 2)
        profilePic = myTeam.getProfilePic()
        print(profilePic)
        def Average(lst): 
            return round(sum(lst) / len(lst), 1) 

        wins = []
        losses = []
        ties = []
        ap = []
        wp = []
        sp = []
        maxScore = []
        opr = []
        dpr = []
        trsp = []
        ccwm = []
        rank = []
        for eventer in myteam["rankings"]:
            event=myteam["rankings"][eventer]
            wins.append(event["wins"])
            losses.append(event["losses"])
            ap.append(event["ap"])
            wp.append(event["wp"])
            sp.append(event["sp"])
            maxScore.append(event["max_score"])
            opr.append(event["opr"])
            dpr.append(event["dpr"])
            trsp.append(event["trsp"])
            ccwm.append(event["ccwm"])
            rank.append(event["rank"])

        averageList = [Average(wins),Average(losses),Average(ap),Average(wp),Average(sp),Average(maxScore),Average(opr),Average(dpr),Average(trsp),Average(ccwm),Average(rank)]

        context.update({
            "matchesAverage":matchesAverage,
            "skillsDriver":skillsDriver,
            "skillsProgramming":skillsProgramming,
            "matchesAverageStatic":round(myteam["average"], 0),
            "skillsDriverStatic":round(myteam["driverAverage"], 0),
            "skillsProgrammingStatic":round(myteam["programmingAverage"], 0),
            "goal1":int(matchGoals[0]),
            "goal2":int(skillsGoals[0]),
            "goal3":int(skillsGoals[1]),
            "averageDataSkills":averageList,
            "profilePic": profilePic,
            "barLabels":["wins","losses","ties","ap","wp","sp","max_score","opr","dpr","trsp","ccwm","rank"],
        })
    
    def main(self, option):
        label = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        print("optionasdkfjsa", option)
        if option == None:
            option='match'
        if option == 'match':
            copyInput = myteam["matches"]
            dateDict = {}
            for lt in copyInput:
                if lt["blue1"] == myteam or lt["blue2"] == myteam or lt["blue3"] == myteam:
                    color="blue"
                else:
                    color="red"
                date = lt["scheduled"]
                matchRound = lt["round"]
                sku = lt["sku"]
                event = getEvent(sku, "webDB_VEX")
                score = lt[f"{color}score"]
                if matchRound > 2:
                    start, end = event.get_timings()
                    if matchRound == 3:
                        subtractionValue = timedelta(minutes=30)
                    if matchRound == 4:
                        subtractionValue = timedelta(minutes=20)
                    if matchRound == 5:
                        subtractionValue = timedelta(minutes=10)
                    if matchRound == 6:
                        subtractionValue = timedelta(minutes=0)

                    date = parser.parse(end)-subtractionValue
                    if date.month not in dateDict.keys():
                        dateDict.update({
                            date.month:[score]
                        })
                    else:
                        dateDict[date.month].append(score)
                else:
                    date = parser.parse(date)
                    if date.month not in dateDict.keys():
                        dateDict.update({
                            date.month:[score]
                        })
                    else:
                        dateDict[date.month].append(score)

            actDate = []
            actScore = []
            for key, value in dateDict.items():
                actDate.append(label[key-1])
                actScore.append(max(value))

            realDate = actDate[::-1]
            realScore = actScore[::-1]
            context.update({
                "xAxis":realDate,
                "data":[['My Team',realScore]]
            })
        elif option=="skills":
            copyInputDriver = myteam["DriverData"]
            driverDict = {}
            for event in copyInputDriver:
                start, end = getEvent(event["sku"], "webDB_VEX").get_timings()
                date=parser.parse(start)
                score=event["score"]
                if date.month not in driverDict.keys():
                    driverDict.update({
                        date.month:[score]
                    })
                else:
                    driverDict[date.month].append(score)
            actDriverScore = []
            actDriverDate = []
            for key, value in driverDict.items():
                actDriverScore.append(max(value))
                actDriverDate.append(label[key-1])
            
            realDriverScore = actDriverScore[::-1]

            copyInputProgramming = myteam["ProgrammingData"]
            ProgrammingDict = {}
            for event in copyInputProgramming:
                start, end = getEvent(event["sku"], "webDB_VEX").get_timings()
                date=parser.parse(start)
                score=event["score"]
                if date.month not in ProgrammingDict.keys():
                    ProgrammingDict.update({
                        date.month:[score]
                    })
                else:
                    ProgrammingDict[date.month].append(score)
            actProgrammingScore = []
            actProgrammingDate = []
            for key, value in ProgrammingDict.items():
                actProgrammingScore.append(max(value))
                actProgrammingDate.append(label[key-1])

            realProgrammingScore = actProgrammingScore[::-1]

            copyInputCombined = myteam["CombinedData"]
            CombinedDict = {}
            for event in copyInputCombined:
                start, end = getEvent(event["sku"], "webDB_VEX").get_timings()
                date=parser.parse(start)
                score=event["score"]
                if date.month not in CombinedDict.keys():
                    CombinedDict.update({
                        date.month:[score]
                    })
                else:
                    CombinedDict[date.month].append(score)
            actCombinedScore = []
            actCombinedDate = []
            for key, value in CombinedDict.items():
                actCombinedScore.append(max(value))
                actCombinedDate.append(label[key-1])

            realCombinedDate = actCombinedDate[::-1]
            realCombinedScore = actCombinedScore[::-1]

            context.update({
                "xAxis": realCombinedDate,
                "data":[
                    ["Driver", realDriverScore],
                    ["Programming", realProgrammingScore],
                    ["Combined", realCombinedScore]
                ]
            })

    def sideGraphs(self):
        allMatches = myteam["matches"]
        label = ["January", "Febuary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        dateList = []
        scoreList = []
        for lt in allMatches:
            if lt["blue1"] == myteam or lt["blue2"] == myteam or lt["blue3"] == myteam:
                color = "blue"
            else:
                color = "red"
            date = lt["scheduled"]
            matchRound = lt["round"]
            sku = lt["sku"]
            event = getEvent(sku, "webDB_VEX")
            score = lt[f"{color}score"]
            if matchRound > 2:
                start, end = event.get_timings()
                if matchRound == 3:
                    subtractionValue = timedelta(minutes=30)
                if matchRound == 4:
                    subtractionValue = timedelta(minutes=20)
                if matchRound == 5:
                    subtractionValue = timedelta(minutes=10)
                if matchRound == 6:
                    subtractionValue = timedelta(minutes=0)

                date = parser.parse(end)-subtractionValue
                dateList.append(date)
                
            else:
                date = parser.parse(date)
                dateList.append(date)
            scoreList.append(score)

        dt, sc = (list(t) for t in zip(*sorted(zip(dateList, scoreList))))
        dateDict = {}
        for date, score in zip(dt, sc):
            month=label[date.month-1]
            if month not in dateDict.keys():
                dateDict.update({month:[score]})
            else:
                dateDict[month].append(score)
        
        copyInputevent = myteam["rankings"]

        eventDict = {}
        for event, values in copyInputevent.items():
            start, end = getEvent(event, "webDB_VEX").get_timings()
            date = parser.parse(start)
            eventDict.update({date: values})
            
        lastCompVals = sorted(eventDict.items(), reverse=True)[0]
        lastObjectValues = list(dateDict.keys())[-1]
        lastMonthScores = dateDict[lastObjectValues]

        context.update({
            "lastMonthValues":lastMonthScores,
            "lastMonthDate":lastObjectValues,
            "lastMonthLabels": list(range(0, len(lastMonthScores))),
            "lastCompRankings":list(lastCompVals[1].values()),
        })

        
    def worldMap(self):
        top10 = mycolTeams.find().sort("average", -1).limit(5)
        justCountry = []
        fullTeamList = []
        for team in top10:
            teamList = []
            countryName = pycountry.countries.search_fuzzy(team["country"])[0].alpha_2
            if team["country"] not in justCountry:
                justCountry.append(countryName)
            teamList.append(team["country"])
            teamList.append(team["number"])
            teamList.append(team["average"])
            teamList.append(countryName.lower())
            fullTeamList.append(teamList)
        context.update({
            "justCountry": justCountry,
            "allTeamData": fullTeamList,
        })       

    def teamSelection(self):
        betterTeams, worseTeams = getTeam(
            self.myTeamName, "webDB_VEX").specialChars1(myteam["average"], 4)
        betterTeamList = []
        worseTeamList = []
        mixTeamList = []
        for count, team in enumerate(betterTeams):
            listAppend = [
                team["number"],
                True,
                team["average"],
                team["driverTopScore"],
                team["programmingTopScore"],
                team["country"],
                team["grade"],
                team["team_name"]
            ]
            if count < 1:
                mixTeamList.append(listAppend)
            else:
                betterTeamList.append(listAppend)

        for count, team in enumerate(worseTeams):
            listAppend = [
                team["number"],
                False,
                team["average"],
                team["driverTopScore"],
                team["programmingTopScore"],
                team["country"],
                team["grade"],
                team["team_name"]
            ]
            if count < 1:
                mixTeamList.append(listAppend)
            else:
                worseTeamList.append(listAppend)

        mixTeamList.append([
            "My Team",
            "1",
            myteam["average"],
            myteam["driverTopScore"],
            myteam["programmingTopScore"],
            myteam["country"],
            myteam["grade"],
            myteam["team_name"]
        ])

        mixTeamList.sort(key=operator.itemgetter(2), reverse=True)
        worseList = reversed(worseTeamList)

        context.update({
            "betterList": betterTeamList,
            "worseList": list(worseList),
            "mixedList": list(reversed(mixTeamList)),
        })

    def calendar(self):
        calendarBool = getUserInfo(self.username,"webDB_VEX").getCalendar()
        is_validVar=False
        if calendarBool:
            is_validVar=True
            fullList = []
            for index, action in enumerate(calendarBool[::-1]):
                if index != 5:
                    fullList.append([
                        action['title'],
                        parser.parse(action["start"]).strftime('%Y-%m-%d'),
                        parser.parse(action["start"]).strftime('%#m-%d'),
                        "danger"
                    ])

                else:
                    break
        else:
            is_validVar=False
            fullList = []
        
        print(fullList)
        print(is_validVar)
        context.update({
            "fullActivityList":fullList,
            "is_validVar":is_validVar
        })

    def messaging(self):
        allChats = mycolchat.find({ "contacts": { "$in" : [self.username]} })
        chatList = []
        for index, chat in enumerate(allChats):
            if index <= 3:
                try:
                    copyInput=chat["contacts"]
                    lastMessageContent=chat["messages"][-1]['content'][1]
                    lastMessageTimings="{0}".format(chat["messages"][-1]['content'][0])
                    timings=f"{parser.parse(lastMessageTimings).strftime('%b %d %Y')}"
                    copyInput.remove(self.username)
                    profilePic=mycolUserInfo.find_one({"username":copyInput[0]})['profilePic']
                    status=mycolAuthUser.find_one({"username":copyInput[0]})['is_active']
                    user=chat["messages"][-1]['user']
                except:
                    lastMessageContent=""
                    lastMessageTimings=""
                    profilePic=""
                    status=""
                    timings=""
                    user="You Are The Only One"
                chatList.append([
                    lastMessageContent, 
                    timings,
                    profilePic,
                    status,
                    user
                ])
            else:
                break
        print(chatList)
        context.update({
            "textMessageList":chatList
        })
    def get(self):
        return context








@login_required(login_url="/login/")
def index(request):
    if page_validator(request.user.username):
        mainRadio=request.POST.get('mainRadio')
        curUser = request.user.username
        myTeam = getUserInfo(curUser, "webDB_VEX").getMyTeam()
        instance = homePage(myTeam, curUser)
        instance.topBar()
        instance.main(mainRadio)
        instance.worldMap()
        instance.sideGraphs()
        instance.teamSelection()
        instance.calendar()
        instance.messaging()

        context = instance.get()
        return render(request, "index.html", context=context)
    else:
        return render(request, "backup.html")

@login_required(login_url="/login/")
def teams(request, slug):
    if page_validator(request.user.username):
        context={}
        curUser = request.user.username

        myTeamInfo = getTeam(slug, "webDB_VEX").get()
        graphInfoDriver = request.POST.getlist('driverLineGraph')
        graphInfoProgramming = request.POST.getlist('programmingLineGraph')
        graphInfoCombined = request.POST.getlist('combinedLineGraph')
        mapInfoTeam = request.POST.getlist('map')
        mapInfoType = request.POST.getlist('type')

        instance = Skills(slug, curUser)
        instance.topBar()
        instance.driverScatterPlot(graphInfoDriver)
        instance.programmingScatterPlot(graphInfoProgramming)
        instance.combinedScatterPlot(graphInfoCombined)
        instance.worldMap(mapInfoTeam, mapInfoType)
        contextSkills = instance.get()
        context.update(contextSkills)

        tableInfo = request.POST.getlist('tableInfo')
        mapInfo = request.POST.get('map')

        instance = Matches(slug, curUser)
        instance.lineGraphData()
        instance.table(tableInfo)
        instance.SimilarTeams()
        instance.Allmatches()
        instance.worldMap(mapInfo)
        contextMatches = instance.get()
        context.update(contextMatches)

        tableInfo = request.POST.getlist('tableInfo')
        instance = Rankings(slug, curUser)
        instance.navigator()
        for key, value in request.POST.items():
            if key == "listInput":
                instance.showGraphs(value, tableInfo)
                instance.worldMap(value)

        contextRankings = instance.get()
        context.update(contextRankings)

        context.update({
            "robot_name":myTeamInfo["robot_name"],
            "organisation": myTeamInfo["organisation"],
            "city":myTeamInfo["city"],
            "region":myTeamInfo["region"],
            "grade":myTeamInfo["grade"],
            "average": myTeamInfo["average"],
        })
        return render(request, "teams.html", context=context)
    else:
        return render(request, "backup.html")

@login_required(login_url="/login/")
def settings(request):
    print("hello")
    def checkData(data):
        myTeam = data["teamNumb"]
        comp1 = data["competitor1"]
        comp2 = data["competitor2"]
        comp3 = data["competitor3"]
        checkList = []
        if getTeam(myTeam, "webDB_VEX").get() != None:
            checkList.append(True)
        else:
            checkList.append(False)
        if getTeam(comp1, "webDB_VEX").get() != None:
            checkList.append(True)
        else:
            checkList.append(False)
        if getTeam(comp2, "webDB_VEX").get() != None:
            checkList.append(True)
        else:
            checkList.append(False)
        if getTeam(comp3, "webDB_VEX").get() != None:
            checkList.append(True)
        else:
            checkList.append(False)
        print(checkList)
        return False if False in checkList else True
    def uploadFile(file):
        file_name = default_storage.save(file.name, file)
        #  Reading file from storage
        file = default_storage.open(file_name)
        file_url = default_storage.url(file_name)

    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient["webDB_VEX"]
    user = request.user.username
    mycolUserInfo = mydb["userInfo"]
    teamNumber=request.POST.get('myTeam')
    competitor1=request.POST.get('mainCompetitor1')
    competitor2=request.POST.get('mainCompetitor2')
    competitor3=request.POST.get('mainCompetitor3')
    skillsProgGoal=request.POST.get('skillsProgrammingGoal')
    skillsDriverGoal=request.POST.get('skillsDriverGoal')
    skillsRankGoal=request.POST.get('skillsRankGoal')
    matchesAverageGoal=request.POST.get('matchesAvgGoal')
    matchesTopScoreGoal=request.POST.get('matchesTopGoal')
    matchesRankGoal=request.POST.get('matchesRankGoal')
    try:
        actProfile = request.FILES['profilePhoto']
    except:
        actProfile = None
    data = {
        "username":user,
        "teamNumb":teamNumber,
        "competitor1":competitor1,
        "competitor2":competitor2,
        "competitor3":competitor3,
        "skillsProgGoal":skillsProgGoal,
        "skillsDriverGoal":skillsDriverGoal,
        "skillsRankGoal":skillsRankGoal,
        "matchesAverageGoal":matchesAverageGoal,
        "matchesTopScoreGoal":matchesTopScoreGoal,
        "matchesRankGoal":matchesRankGoal,
    }
    message=""
    try:
        print(user)
        findUser = getUserInfo(user, "webDB_VEX").getMyTeam()
        checker = checkData(data)
        if checker:
            mycolUserInfo.update_one({"username":user}, {'$set':data})
            mycolUserInfo.update_one(
                    {"profilePic": actProfile}, {'$set': data})
            print("hello")
            uploadFile(actProfile)
            return redirect('/')
        else:
            if None not in data.values():
                message+="One Of your teams is NOT supported by us. We apologize for the inconvenience."
            
    except Exception as e:
        print(e)
        if None not in data.values():
            print(data)
            checker = checkData(data)
            print(checker)
            if checker:
                mycolUserInfo = mydb["userInfo"]
                mycolUserInfo.insert_one(data)
                uploadFile(actProfile)
            else:
                message+="One Of your teams is NOT supported by us. We apologize for the inconvenience."

    contextVar={}
    try:
        findUser=getUserInfo(user, "webDB_VEX").getMyTeam()
        findUser=getUserInfo(user, "webDB_VEX").get()
        contextVar.update({
            "username":findUser["username"],
            "teamNumb":findUser["teamNumb"],
            "competitor1":findUser["competitor1"],
            "competitor2":findUser["competitor2"],
            "competitor3":findUser["competitor3"],
            "skillsProgGoal":findUser["skillsProgGoal"],
            "skillsDriverGoal":findUser["skillsDriverGoal"],
            "skillsRankGoal": findUser["skillsRankGoal"],
            "matchesAverageGoal":findUser["matchesAverageGoal"],
            "matchesTopScoreGoal":findUser["matchesTopScoreGoal"],
            "matchesRankGoal": findUser["matchesRankGoal"],
        })
    except:
        contextVar.update({
            "username": "",
            "teamNumb": "",
            "competitor1": "",
            "competitor2": "",
            "competitor3": "",
            "skillsProgGoal": "",
            "skillsDriverGoal": "",
            "skillsRankGoal": "",
            "matchesAverageGoal": "",
            "matchesTopScoreGoal": "",
            "matchesRankGoal": "",
        })
    contextVar.update({"message":message})
    context=contextVar
    template = loader.get_template('pages/settings.html')
    return HttpResponse(template.render(context, request))






@login_required(login_url="/login/")
def pages(request):
    if page_validator(request.user.username):
        context = {}
        # All resource paths end in .html.
        # Pick out the html file name from the url. And load that template.
        load_template = request.path.split('/')[-1]
        if load_template == "matches.html":
            tableInfo=request.POST.getlist('tableInfo')
            mapInfo=request.POST.get('map')

            curUser = request.user.username
            instance = Matches(curUser)
            instance.lineGraphData()
            instance.table(tableInfo)
            instance.SimilarTeams()
            instance.Allmatches()
            instance.worldMap(mapInfo)
            context=instance.get()
        elif load_template == "skills.html":
            graphInfoDriver=request.POST.getlist('driverLineGraph')
            graphInfoProgramming=request.POST.getlist('programmingLineGraph')
            graphInfoCombined=request.POST.getlist('combinedLineGraph')
            mapInfoTeam=request.POST.getlist('map')
            mapInfoType=request.POST.getlist('type')
            curUser = request.user.username

            instance = Skills(curUser)
            instance.topBar()
            instance.driverScatterPlot(graphInfoDriver)
            instance.programmingScatterPlot(graphInfoProgramming)
            instance.combinedScatterPlot(graphInfoCombined)
            instance.worldMap(mapInfoTeam, mapInfoType)
            context=instance.get()
        elif load_template == "rankings.html":
            curUser = request.user.username
            tableInfo=request.POST.getlist('tableInfo')
            instance = Rankings(curUser)
            instance.navigator()
            for key, value in request.POST.items():
                if key == "listInput":
                    instance.showGraphs(value, tableInfo)
                    instance.worldMap(value)

            context = instance.get()
        elif load_template == "text_message.html":
            key = request.POST.get("keyInput")
            create = request.POST.get("create")
            message = request.POST.get("message")
            person = request.POST.get("person")
            invite = request.POST.get("invite")
            curUser=request.user.username
            instance=chat(curUser)
            if key != "undefined":
                instance.join(key)
            if create == "on":
                instance.create()
            if invite:
                person1 = request.POST.get("person1")
                instance.invite(invite, person1)
            if message != None:
                instance.sendMessage(message, person)

            instance.load()
            context=instance.get()
            # keyInput
        elif load_template == "team_search.html":
            searchInfo = request.POST.get('search')
            curUser = request.user.username
            instance = teamSearchMain("BLRS", curUser)
            instance.first()
            if searchInfo != None:
                return redirect(f"team/{searchInfo}")
            context = instance.get()
        elif load_template == "calendar.html":
            curUser = request.user.username
            instance = calendar(curUser, "webDB_VEX")
            myTeam = getUserInfo(curUser, "webDB_VEX")   
            try:
                listOfEvents=eval(request.POST.get("eventData"))
                if listOfEvents != "" and myTeam.getCalendar() != False:
                    instance.add(listOfEvents)
                elif listOfEvents != "" and myTeam.getCalendar() == False:
                    instance.insert(listOfEvents)
            except:
                pass    
            instance.load()
            context=instance.get()
            

        try:
            template = loader.get_template('pages/' + load_template)
            return HttpResponse(template.render(context, request))

        except:

            template = loader.get_template( 'pages/error-404.html' )
            return HttpResponse(template.render(context, request))

    else:
        return render(request, "backup.html")
