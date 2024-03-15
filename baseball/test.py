import statsapi as api

print(api.boxscore_data(71783,timecode=None))




#from getStats import stats
#import pandas as pd
#import numpy as np
#import matplotlib as pl
#
#
#stats = stats.fillna(0)
#stats["homeTeam"] = stats["homeTeam"].map({
#    True: 1,
#    False: 0
#})
#
#x = stats.plot.scatter(
#    x="pitching_pitchesThrown", y="pitching_blownSaves", c="red",
#    alpha=.3, xlim=(0, 1.6), ylim=(0, 400)
#);
#
#x