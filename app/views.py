# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from operator import itemgetter
import pymongo
import pycountry


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

    def getMyTeam(self):
        return find["teamNumb"]

    def getCompetitors(self):
        return find["competitor1"], find["competitor2"], find["competitor3"]

    def getMatchesGoals(self):
        return find["matchesAverageGoal"], find["matchesRankGoal"], find["matchesTopScoreGoal"]

    def getSkillsGoals(self):
        return find["skillsDriverGoal"], find["skillsProgGoal"], find["skillsRankGoal"]


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

    def specialChars(self, myTeamAverage):
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
        averageGreater = mycolTeams.find(queryGreater).sort("average",-1).limit(2)
        averageLesser = mycolTeams.find(queryLesser).sort("average",-1).limit(2)
        return averageGreater, averageLesser


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

    def matchesFormatter(self):
        copyInput = self.input
        scoreList = []
        dateList = []
        elimScore = []
        elimDate = []
        elimRound = []
        elimSku = []
        for lt in copyInput:
            score = lt[0]
            date = lt[1]
            matchRound = lt[2]
            sku = lt[4]
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

    def skillsFormatter(self):
        copyInput = self.input
        bigList = []
        topScoreList = []
        total = 0
        for index, event in enumerate(copyInput):
            topScore = event["score"]
            attempts = event["attempts"]
            bigList.append({
                "x": index,
                "y":topScore,
                "r":attempts*5,
            })
            total+=topScore
            topScoreList.append(topScore)
        
        average = total/len(copyInput)
        return bigList, average, max(topScoreList)

class Matches():
    def __init__(self, username):
        self.username=username
        global errors
        errors = []
        global context
        context = {}
        myTeam = getUserInfo(self.username, "webDB_VEX")
        global myteam
        myteam = getTeam(myTeam.getMyTeam(), "webDB_VEX").get()
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
            
        myTeamDate, myTeamScore = formatter(myTeamMatches).matchesFormatter()
        completeList.append(myTeamScore)
        teamsList.append("My Team")

        goal=100
        percentage = round((myteam["average"]/goal)*100)

        competitor1Date, competitor1Score = formatter(competitor1Find["matches"]).matchesFormatter()
        competitor2Date, competitor2Score = formatter(competitor2Find["matches"]).matchesFormatter()
        competitor3Date, competitor3Score = formatter(competitor3Find["matches"]).matchesFormatter()


        completeList.append(competitor1Score)
        completeList.append(competitor2Score)
        completeList.append(competitor3Score)

        teamsList.append(competitor1Find["number"])
        teamsList.append(competitor2Find["number"])
        teamsList.append(competitor3Find["number"])


        top10 = mycolTeams.find().sort("average", -1).limit(10)
        bottom10 = mycolTeams.find().sort("average", 1).limit(10)
 
        for team in top10:
            top10Date, top10Score = formatter(team["matches"]).matchesFormatter()
            teamsList.append(team["number"])
            completeList.append(top10Score)

        for team in bottom10:
            try:
                bottom10Date, bottom10Score = formatter(team["matches"]).matchesFormatter()

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
        similarAveragesGreater, similarAveragesLesser = getTeam(None, "webDB_VEX").specialChars(myteam["average"])
        count = 1
        for teams in similarAveragesGreater:
            date, score = formatter(teams["matches"]).matchesFormatter()
            yAxisLength = len(score)
            teamDiff = round(myteam["average"]/teams["average"]*100)
            print(yAxisLength)
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
                date, score = formatter(teams["matches"]).matchesFormatter()
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
            print(myteam["average"])
            print(teams["average"])
            context.update({
                f"worseTeamNumber{count}":teams["number"],
                f"worseTeamAverage{count}":teams["average"],
                f"worseTeamDiff{count}":100-teamDiff,
                f"worseAverageTeam{count}":values,
            })
            count+=1
          
    def worldMap(self, mapInfo):
        print(mapInfo)
        top10 = mycolTeams.find().sort("average", -1).limit(10)
        bottom10 = mycolTeams.find().sort("average", 1).limit(10)
        if mapInfo == "myPosition":
            mypositionData = pycountry.countries.search_fuzzy(myteam["country"])[0].alpha_2
            context.update({
                "justCountry": [mypositionData],
                "allTeamData": [[myteam["country"], myteam["number"],
                                 myteam["average"], mypositionData.lower()]]
            })
        elif mapInfo == "myCompetitors":
            competitor1=pycountry.countries.search_fuzzy(competitor1Find["country"])[0].alpha_2
            competitor2=pycountry.countries.search_fuzzy(competitor2Find["country"])[0].alpha_2
            competitor3=pycountry.countries.search_fuzzy(competitor3Find["country"])[0].alpha_2
            context.update({
                "justCountry": [
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
                "justCountry": justCountry,
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
                "justCountry": justCountry,
                "allTeamData": fullTeamList,
            })

    def get(self):
        return context


class Skills():
    def __init__(self, username):
        self.username = username
        global errors
        errors = []
        global context
        context = {}
        global myTeam
        myTeam = getUserInfo(self.username, "webDB_VEX")
        global myteam
        myteam = getTeam(myTeam.getMyTeam(), "webDB_VEX").get()
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
        for combinedData in combined:
            Combinedtotal += combinedData["score"]
        context.update({
            "team_name": myteam["team_name"],
            "skillsDriverGoal":skillsDriverGoal,
            "skillsProgGoal": skillsProgGoal,
            "skillsCombinedGoal": skillsCombinedGoal,
            "DRIVERscore": Drivertotal/len(driver),
            "PROGscore": Programmingtotal/len(programming),
            "COMBINEDscore": Combinedtotal/len(combined),
            "skillsDriverGoalTotal":  round(
                ((Drivertotal/len(driver))/int(skillsDriverGoal))*100, 2),
            "skillsProgGoalTotal": round(
                ((Programmingtotal/len(programming))/int(skillsProgGoal))*100, 2),
            "skillsCombinedGoalTotal": round(
                ((Combinedtotal/len(combined))/int(skillsCombinedGoal))*100, 2),
        })

    def driverScatterPlot(self):
        AllDriver, average, topScore = formatter(driver).skillsFormatter()
        context.update({
            "driverBubblePlotData":AllDriver,
            "tableList": [[myteam["number"], topScore, average]],
        })

    def progScatterPlot(self):
        AllProgramming = formatter(programming).skillsFormatter()


    def combinedScatterPlot(self):
        AllCombined = formatter(combined).skillsFormatter()


    def get(self):
        return context


@login_required(login_url="/login/")
def index(request):
    return render(request, "index.html")

@login_required(login_url="/login/")
def pages(request):
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
        instance.worldMap(mapInfo)
        context=instance.get()
    elif load_template == "skills.html":
        curUser = request.user.username
        instance = Skills(curUser)
        instance.topBar()
        instance.driverScatterPlot()
        context=instance.get()
    elif load_template == "rankings.html":
        tableInfo = request.POST.getlist('tableInfo')
        mapInfo = request.POST.get('map')

        curUser = request.user.username
        instance = Matches(curUser)
        instance.lineGraphData()
        instance.table(tableInfo)
        instance.SimilarTeams()
        instance.worldMap(mapInfo)
        context = instance.get()

    elif load_template == "settings.html":
        if request.method == "POST":
            myclient = pymongo.MongoClient('mongodb://localhost:27017/')
            mydb = myclient["webDB_VEX"]
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


            user = request.user.username
            mycolUserInfo = mydb["userInfo"]
            if teamNumber and competitor1 and competitor2 and competitor3:
                query = {
                    "username":user
                }
                data = {
                    "username":user,
                    "teamNumb":teamNumber,
                    "competitor1":competitor1,
                    "competitor2":competitor2,
                    "competitor3":competitor3
                }
                response = mycolUserInfo.find(query)
             
                if list(response):

                    mycolUserInfo.update_one(query,{
                            "$set": data
                        })
                else:
                    print("created")
                    mycolUserInfo.insert_one(data)



            if skillsProgGoal and skillsDriverGoal and skillsRankGoal and matchesAverageGoal and matchesTopScoreGoal and matchesRankGoal:
                query = {
                    "username":user
                }
                data = {
                    "skillsProgGoal":skillsProgGoal,
                    "skillsDriverGoal":skillsDriverGoal,
                    "skillsRankGoal":skillsRankGoal,
                    "matchesAverageGoal":matchesAverageGoal,
                    "matchesTopScoreGoal":matchesTopScoreGoal,
                    "matchesRankGoal":matchesRankGoal
                }
                response = mycolUserInfo.find(query)
             
                if list(response):
                    mycolUserInfo.update_one(query,{
                            "$set": data
                        })
                else:
                    mycolUserInfo.insert_one(data)

                

            print(teamNumber, competitor1, competitor2, competitor3, skillsProgGoal, skillsDriverGoal, matchesAverageGoal, matchesTopScoreGoal, matchesRankGoal)

    try:
        template = loader.get_template('pages/' + load_template)
        return HttpResponse(template.render(context, request))

    except:

        template = loader.get_template( 'pages/error-404.html' )
        return HttpResponse(template.render(context, request))
