from collections import deque
import time
from datetime import datetime
import csv
import os
import statsapi as api

start_time = time.time()

mlbTeamIds = [
    133,
    134,
    135,
    136,
    137,
    138,
    139,
    140,
    141,
    142,
    143,
    144,
    145,
    146,
    147,
    158,
    108,
    109,
    110,
    111,
    112,
    113,
    114,
    115,
    116,
    117,
    118,
    119,
    120,
    121,
]

mlbTeamNames = [
    "Oakland Athletics",
    "Pittsburgh Pirates",
    "San Diego Padres",
    "Seattle Mariners",
    "San Franciso Giants",
    "St. Louis Cardinals",
    "Tampa Bay Rays",
    "Texas Rangers",
    "Toronto Blue Jays",
    "Minnesota Twins",
    "Philadelphia Phillies",
    "Atlanta Braves",
    "Chicago White Sox",
    "Miami Marlins",
    "New York Yankees",
    "Milwaukee Brewers",
    "Los Angeles Angels",
    "Arizona Diamondbacks",
    "Baltimore Orioles",
    "Boston Red Sox",
    "Chicago Cubs",
    "Cincinnati Reds",
    "Cleveland Guardians",
    "Colorado Rockies",
    "Detroit Tigers",
    "Houston Astros",
    "Kansas City Royals",
    "Los Angeles Dodgers",
    "Washington Nationals",
    "New York Mets",
]

array_of_deques = [deque() for _ in range(len(mlbTeamIds))]

for i in range(len(mlbTeamIds)):
    array_of_deques[i].append({"teamId": mlbTeamIds[i], "teamName": mlbTeamNames[i]})

endDate = datetime.now().strftime("%m/%d/%Y")

for i in range(len(array_of_deques)):
    idArr = []
    games = api.schedule(start_date="03/20/2023", end_date=endDate, team=mlbTeamIds[i])
    for j in range(len(array_of_deques[i])):
        for k in games:
            idArr.append(k["game_id"])
            array_of_deques[i][j].update({"gamesIds": idArr})
    idArr = []


for i in range(len(array_of_deques)):
    maxSize = 100
    start = len(array_of_deques[i][0]["gamesIds"]) - maxSize
    array_of_deques[i][0]["gamesIds"] = array_of_deques[i][0]["gamesIds"][
        start : len(array_of_deques[i][0]["gamesIds"])
    ]


class TeamStats(object):
    def __init__(self, teamId):
        self.teamId = teamId

    def getGameStats(self):
        totalStats = []
        stats = []
        gameids = []
        for i in range(len(array_of_deques)):
            if self.teamId == array_of_deques[i][0]["teamId"]:
                for j in range(len(array_of_deques[i][0]["gamesIds"])):
                    gameids.append(array_of_deques[i][0]["gamesIds"][j])
                    try:
                        stats.append(
                            api.boxscore_data(
                                array_of_deques[i][0]["gamesIds"][j], timecode=None
                            )
                        )
                    except:
                        print(
                            "No id found for game {}".format(
                                array_of_deques[i][0]["gamesIds"][j]
                            )
                        )

        for i in range(len(stats)):
            homeId = stats[i]["teamInfo"]["home"]["id"]
            awayId = stats[i]["teamInfo"]["away"]["id"]
            if self.teamId == homeId:
                for key in stats[i]["home"]["players"].keys():
                    totalStats.append(
                        {
                            "gameId": gameids[i],
                            "teamId": homeId,
                            "opponentId": awayId,
                            "homeTeam?": True,
                            "playerInfo": stats[i]["home"]["players"][key]["person"],
                            "playerStats": stats[i]["home"]["players"][key]["stats"],
                        }
                    )
            if self.teamId == awayId:
                for key in stats[i]["away"]["players"].keys():
                    totalStats.append(
                        {
                            "gameId": gameids[i],
                            "teamId": awayId,
                            "opponentId": homeId,
                            "homeTeam?": False,
                            "playerInfo": stats[i]["away"]["players"][key]["person"],
                            "playerStats": stats[i]["away"]["players"][key]["stats"],
                        }
                    )
        return totalStats

    def toCsv(self):
        data = self.getGameStats()
        filenames = [
            {"id": id, "name": name} for id, name in zip(mlbTeamIds, mlbTeamNames)
        ]

        fileName = None
        for i in range(len(filenames)):
            if self.teamId == filenames[i]["id"]:
                fileName = filenames[i]["name"] + ".csv"
                fileName = fileName.replace(" ", "")

        subfolder = "baseball/teamCsvFiles"
        filePath = os.path.join(subfolder, fileName)

        fieldnames = [
            "gameId",
            "teamId",
            "opponentId",
            "homeTeam?",
            "playerInfoId",
            "playerFullName",
            "battingRuns",
            "battingDoubles",
            "battingTriples",
            "battingHomeRuns",
            "battingStrikeOuts",
            "battingBaseOnBalls",
            "battingHits",
            "battingAtBats",
            "battingStolenBases",
            "battingRbi",
            "battingLeftOnBase",
            "pitchingRuns",
            "pitchingDoubles",
            "pitchingTriples",
            "pitchingHomeRuns",
            "pitchingStrikeOuts",
            "pitchingBaseOnBalls",
            "pitchingHits",
            "pitchingAtBats",
            "pitchingStolenBases",
            "pitchingNumberOfPitches",
            "pitchingInningsPitched",
            "pitchingWins",
            "pitchingLosses",
            "pitchingHolds",
            "pitchingBlownSaves",
            "pitchingEarnedRuns",
            "pitchingPitchesThrown",
        ]

        with open(filePath, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in data:
                writer.writerow(
                    {
                        "gameId": entry["gameId"],
                        "teamId": entry["teamId"],
                        "opponentId": entry["opponentId"],
                        "homeTeam?": entry["homeTeam?"],
                        "playerInfoId": entry["playerInfo"]["id"],
                        "playerFullName": entry["playerInfo"].get("fullName", ""),
                        "battingRuns": entry["playerStats"]["batting"].get("runs", ""),
                        "battingDoubles": entry["playerStats"]["batting"].get(
                            "doubles", ""
                        ),
                        "battingTriples": entry["playerStats"]["batting"].get(
                            "triples", ""
                        ),
                        "battingHomeRuns": entry["playerStats"]["batting"].get(
                            "homeRuns", ""
                        ),
                        "battingStrikeOuts": entry["playerStats"]["batting"].get(
                            "strikeOuts", ""
                        ),
                        "battingBaseOnBalls": entry["playerStats"]["batting"].get(
                            "baseOnBalls", ""
                        ),
                        "battingHits": entry["playerStats"]["batting"].get("hits", ""),
                        "battingAtBats": entry["playerStats"]["batting"].get(
                            "atBats", ""
                        ),
                        "battingStolenBases": entry["playerStats"]["batting"].get(
                            "stolenBases", ""
                        ),
                        "battingRbi": entry["playerStats"]["batting"].get("rbi", ""),
                        "battingLeftOnBase": entry["playerStats"]["batting"].get(
                            "leftOnBase", ""
                        ),
                        "pitchingRuns": entry["playerStats"]["pitching"].get(
                            "runs", ""
                        ),
                        "pitchingDoubles": entry["playerStats"]["pitching"].get(
                            "doubles", ""
                        ),
                        "pitchingTriples": entry["playerStats"]["pitching"].get(
                            "triples", ""
                        ),
                        "pitchingHomeRuns": entry["playerStats"]["pitching"].get(
                            "homeRuns", ""
                        ),
                        "pitchingStrikeOuts": entry["playerStats"]["pitching"].get(
                            "strikeOuts", ""
                        ),
                        "pitchingBaseOnBalls": entry["playerStats"]["pitching"].get(
                            "baseOnBalls", ""
                        ),
                        "pitchingHits": entry["playerStats"]["pitching"].get(
                            "hits", ""
                        ),
                        "pitchingAtBats": entry["playerStats"]["pitching"].get(
                            "atBats", ""
                        ),
                        "pitchingStolenBases": entry["playerStats"]["pitching"].get(
                            "stolenBases", ""
                        ),
                        "pitchingNumberOfPitches": entry["playerStats"]["pitching"].get(
                            "numberOfPitches", ""
                        ),
                        "pitchingInningsPitched": entry["playerStats"]["pitching"].get(
                            "inningsPitched", ""
                        ),
                        "pitchingWins": entry["playerStats"]["pitching"].get(
                            "wins", ""
                        ),
                        "pitchingLosses": entry["playerStats"]["pitching"].get(
                            "losses", ""
                        ),
                        "pitchingHolds": entry["playerStats"]["pitching"].get(
                            "holds", ""
                        ),
                        "pitchingBlownSaves": entry["playerStats"]["pitching"].get(
                            "blownSaves", ""
                        ),
                        "pitchingEarnedRuns": entry["playerStats"]["pitching"].get(
                            "earnedRuns", ""
                        ),
                        "pitchingPitchesThrown": entry["playerStats"]["pitching"].get(
                            "pitchesThrown", ""
                        ),
                    }
                )


for i in mlbTeamIds[10:]:
    team = TeamStats(i)
    team.toCsv()
    print("csv written")


end_time = time.time()
execution_time = end_time - start_time

print(f"Execution time: {execution_time} seconds")
