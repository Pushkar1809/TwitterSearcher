import pymongo
import pandas as pd
import json

client = pymongo.MongoClient("mongodb://localhost:27017")

df = pd.read_csv(r'tweets.csv')

df_dict = df.to_dict(orient="records")

db = client["TwitterScrape"]

db.TechTweets.insert_many(df_dict)




