import pandas as pd

stats = pd.read_csv("ArizonsDiamondbacks.csv", encoding='latin1')
print(stats.columns)