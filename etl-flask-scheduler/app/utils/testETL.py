from app.database import DB
from datetime import datetime
import pandas as pd
import random
import os

def dummyETL(db):
    multiplier = [0.98,0.96,0.94,0.92,0.9,1]
    df_wine = pd.read_csv(os.path.join("app","static","wine-quality.csv"))
    df_wine['datetime_'] = datetime.now()
    df_wine = df_wine.loc[[random.randint(0,len(df_wine)-1)]]
    dict_wine = df_wine.to_dict('records')
    dict_wine = dict_wine[0]
    dict_wine['fixed acidity'] = dict_wine['fixed acidity'] * multiplier[random.randint(0,len(multiplier)-1)]
    dict_wine['volatile acidity'] = dict_wine['volatile acidity'] * multiplier[random.randint(0,len(multiplier)-1)]
    dict_wine['citric acid'] = dict_wine['citric acid'] * multiplier[random.randint(0,len(multiplier)-1)]
    dict_wine['residual sugar'] = dict_wine['residual sugar'] * multiplier[random.randint(0,len(multiplier)-1)]
    dict_wine['chlorides'] = dict_wine['chlorides'] * multiplier[random.randint(0,len(multiplier)-1)]
    dict_wine['free sulfur dioxide'] = dict_wine['free sulfur dioxide'] * multiplier[random.randint(0,len(multiplier)-1)]
    dict_wine['total sulfur dioxide'] = dict_wine['total sulfur dioxide'] * multiplier[random.randint(0,len(multiplier)-1)]
    dict_wine['density'] = dict_wine['density'] * multiplier[random.randint(0,len(multiplier)-1)]
    dict_wine['pH'] = dict_wine['pH'] * multiplier[random.randint(0,len(multiplier)-1)]
    dict_wine['sulphates'] = dict_wine['sulphates'] * multiplier[random.randint(0,len(multiplier)-1)]
    dict_wine['alcohol'] = dict_wine['alcohol'] * multiplier[random.randint(0,len(multiplier)-1)]
    for item in dict_wine:
        if item != "datetime_":
            dict_wine[item] = round(dict_wine[item],4)
    db.dummy_col.insert_one(dict_wine)
    return dict_wine