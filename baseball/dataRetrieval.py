import array
from collections import deque
import time
import itertools
from multiprocessing import Pool
from datetime import datetime
import csv
import asyncio
import queue
import statsapi as api

start_time = time.time()

mlbTeamIds = [133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 158, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121]

mlbTeamNames = ["Oakland Athletics","Pittsburgh Pirates","San Diego Padres","Seattle Mariners","San Franciso Giants","St. Louis Cardinals",
                "Tampa Bay Rays","Texas Rangers","Toronto Blue Jays", "Minnesota Twins","Philadelphia Phillies","Atlanta Braves","Chicago White Sox","Miami Marlins","New York Yankees","Milwaukee Brewers","Los Angeles Angels","Arizons Diamondbacks","Baltimore Orioles","Boston Red Sox","Chicago Cubs","Cincinnati Reds","Cleveland Guardians","Colorado Rockies","Detroit Tigers","Houston Astros",
                "Kansas City Royals","Los Angeles Dodgers","Washington Nationals","New York Mets"]

array_of_deques = [deque() for _ in range(len(mlbTeamIds))]

for i in range(len(mlbTeamIds)):
    array_of_deques[i].append({"teamId":mlbTeamIds[i], "teamName": mlbTeamNames[i]})

endDate = datetime.now().strftime("%m/%d/%Y")

for i in range(len(array_of_deques)):
    idArr = []
    games = api.schedule(start_date='03/20/2023',end_date=endDate,team=mlbTeamIds[i])
    for j in range(len(array_of_deques[i])):
        for k in games:
            idArr.append(k["game_id"])
            array_of_deques[i][j].update({"gamesIds":idArr})
    idArr= []


for i in range(len(array_of_deques)):
    maxSize = 100
    start = len(array_of_deques[i][0]["gamesIds"]) - maxSize 
    array_of_deques[i][0]["gamesIds"] = array_of_deques[i][0]["gamesIds"][start:len(array_of_deques[i][0]["gamesIds"])]

class TeamStats(object):
    def __init__(self,teamId):
        self.teamId = teamId

    def getGameStats(self):
        totalStats = []
        stats = []
        gameids = []
        for i in range(len(array_of_deques)):
            if self.teamId == array_of_deques[i][0]["teamId"]:
                for j in range(len(array_of_deques[i][0]["gamesIds"])):
                   gameids.append(array_of_deques[i][0]["gamesIds"][j])
                   stats.append(api.boxscore_data(array_of_deques[i][0]["gamesIds"][j],timecode=None))

        for i in range(len(stats)):
            homeId = stats[i]["teamInfo"]["home"]["id"]
            awayId = stats[i]["teamInfo"]["away"]["id"]
            if self.teamId == homeId:
                for key in stats[i]["home"]["players"].keys():
                    totalStats.append({"gameId": gameids[i],"teamId": homeId,"opponentId":awayId,"homeTeam?": True,"playerInfo":stats[i]["home"]["players"][key]["person"],"playerStats":stats[i]["home"]["players"][key]["stats"]})
            if self.teamId == awayId:
                for key in stats[i]["away"]["players"].keys():
                    totalStats.append({"gameId": gameids[i],"teamId": awayId,"opponentId":homeId,"homeTeam?": False,"playerInfo":stats[i]["away"]["players"][key]["person"],"playerStats":stats[i]["away"]["players"][key]["stats"]})
        return totalStats
    
    def toCsv(self):
        data = self.getGameStats()
        filenames = [
                        {"id": id, "name": name}
                        for id, name in zip(mlbTeamIds, mlbTeamNames)
                    ]
        
        fileName = None
        for i in range(len(filenames)):
            if self.teamId == filenames[i]["id"]:
                fileName = filenames[i]["name"] + ".csv"
                fileName = fileName.replace(" ","")

    
        fieldnames = [
                        'gameId', 'teamId', 'opponentId', 'homeTeam?', 
                        'playerInfo_id', 'playerInfo_fullName', 
                        'playerStats_batting_runs', 'playerStats_batting_doubles', 'playerStats_batting_triples',
                        'playerStats_batting_homeRuns', 'playerStats_batting_strikeOuts', 'playerStats_batting_baseOnBalls',
                        'playerStats_batting_hits', 'playerStats_batting_atBats', 'playerStats_batting_stolenBases',
                        'playerStats_batting_rbi', 'playerStats_batting_leftOnBase',
                        'playerStats_pitching_runs', 'playerStats_pitching_doubles', 'playerStats_pitching_triples',
                        'playerStats_pitching_homeRuns', 'playerStats_pitching_strikeOuts', 'playerStats_pitching_baseOnBalls',
                        'playerStats_pitching_hits', 'playerStats_pitching_atBats', 'playerStats_pitching_stolenBases',
                        'playerStats_pitching_numberOfPitches', 'playerStats_pitching_inningsPitched',
                        'playerStats_pitching_wins', 'playerStats_pitching_losses', 'playerStats_pitching_holds',
                        'playerStats_pitching_blownSaves', 'playerStats_pitching_earnedRuns', 'playerStats_pitching_pitchesThrown'
                    ]


        with open(fileName, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in data:
                writer.writerow({
                    'gameId': entry['gameId'],
                    'teamId': entry['teamId'],
                    'opponentId': entry['opponentId'],
                    'homeTeam?': entry['homeTeam?'],
                    'playerInfo_id': entry['playerInfo']['id'],
                    'playerInfo_fullName': entry['playerInfo']['fullName'],
                    'playerStats_batting_runs': entry['playerStats']['batting'].get('runs', ''),
                    'playerStats_batting_doubles': entry['playerStats']['batting'].get('doubles', ''),
                    'playerStats_batting_triples': entry['playerStats']['batting'].get('triples', ''),
                    'playerStats_batting_homeRuns': entry['playerStats']['batting'].get('homeRuns', ''),
                    'playerStats_batting_strikeOuts': entry['playerStats']['batting'].get('strikeOuts', ''),
                    'playerStats_batting_baseOnBalls': entry['playerStats']['batting'].get('baseOnBalls', ''),
                    'playerStats_batting_hits': entry['playerStats']['batting'].get('hits', ''),
                    'playerStats_batting_atBats': entry['playerStats']['batting'].get('atBats', ''),
                    'playerStats_batting_stolenBases': entry['playerStats']['batting'].get('stolenBases', ''),
                    'playerStats_batting_rbi': entry['playerStats']['batting'].get('rbi', ''),
                    'playerStats_batting_leftOnBase': entry['playerStats']['batting'].get('leftOnBase', ''),
                    'playerStats_pitching_runs': entry['playerStats']['pitching'].get('runs', ''),
                    'playerStats_pitching_doubles': entry['playerStats']['pitching'].get('doubles', ''),
                    'playerStats_pitching_triples': entry['playerStats']['pitching'].get('triples', ''),
                    'playerStats_pitching_homeRuns': entry['playerStats']['pitching'].get('homeRuns', ''),
                    'playerStats_pitching_strikeOuts': entry['playerStats']['pitching'].get('strikeOuts', ''),
                    'playerStats_pitching_baseOnBalls': entry['playerStats']['pitching'].get('baseOnBalls', ''),
                    'playerStats_pitching_hits': entry['playerStats']['pitching'].get('hits', ''),
                    'playerStats_pitching_atBats': entry['playerStats']['pitching'].get('atBats', ''),
                    'playerStats_pitching_stolenBases': entry['playerStats']['pitching'].get('stolenBases', ''),
                    'playerStats_pitching_numberOfPitches': entry['playerStats']['pitching'].get('numberOfPitches', ''),
                    'playerStats_pitching_inningsPitched': entry['playerStats']['pitching'].get('inningsPitched', ''),
                    'playerStats_pitching_wins': entry['playerStats']['pitching'].get('wins', ''),
                    'playerStats_pitching_losses': entry['playerStats']['pitching'].get('losses', ''),
                    'playerStats_pitching_holds': entry['playerStats']['pitching'].get('holds', ''),
                    'playerStats_pitching_blownSaves': entry['playerStats']['pitching'].get('blownSaves', ''),
                    'playerStats_pitching_earnedRuns': entry['playerStats']['pitching'].get('earnedRuns', ''),
                    'playerStats_pitching_pitchesThrown': entry['playerStats']['pitching'].get('pitchesThrown', ''),
                })
       
for i in mlbTeamIds:
    team = TeamStats(i)
    team.toCsv()
    print("csv written")



end_time = time.time()
execution_time = end_time - start_time

print(f"Execution time: {execution_time} seconds")



