from flask import Flask, request, jsonify, Response
import numpy as np
from pydantic import ValidationError
import prometheus_client
from app.middleware import setup_metrics
from app.database import DB
from app.prometheus import PROM
from app.utils.testLoadModel import *
from app.utils.logger import SetUpLogging
import logging
import os
from datetime import datetime, timedelta
import pandas as pd

# LOGGER
SetUpLogging().setup_logging()

# APP
app = Flask(__name__)
loaded_model = None

# DB
dbext = DB(host=os.environ["HOSTDBEXT"],port=os.environ["PORTDBEXT"],username=os.environ["MONGO_INITDB_ROOT_USERNAME"],password=os.environ["MONGO_INITDB_ROOT_PASSWORD"])

# PROM
prom = PROM()
setup_metrics(app)
@app.route('/metrics')
def metrics():
    CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')
    return Response(prometheus_client.generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# REST API
@app.route('/', methods=['GET'])
def testReturn():
    return str("Flask Serving")

@app.route('/getLatestData/', methods=['GET'])
def getLatestData():
    data = pd.DataFrame(list(dbext.dummy_col.find({},{'_id': False}))).tail().to_dict("index")
    return jsonify(data)

@app.route('/getLengthData/', methods=['GET'])
def getLengthData():
    return {"lengthData" : len(list(dbext.dummy_col.find()))}

# MLFLOW
@app.route('/loadModel/', methods=['GET'])
def loadModel():
    try:
        load_model()
        logging.info("LOAD MODEL MLFLOW : ",str(loaded_model))
        return str(loaded_model)
    except Exception as e:
        return str(e)

@app.route('/predictTestMLFlow/', methods=['GET'])
def predictTestMLFlow():
    try:
        logging.info(predictData(loaded_model))
        return jsonify(predictData(loaded_model))
    except Exception as e:
        return str(e)

@app.route('/getModelInfo/', methods=['GET'])
def getModelInfo():
    try:
        return str(loaded_model)
    except Exception as e:
        logging.info("MODEL INFO ERROR : ",str(e))
        return str(e)

@app.route('/predictDummy/', methods=['GET','POST'])
def predictDummy():
    if request.method == 'POST':
        try:
            resultTemp = predictEtlData(loaded_model,request.json)['result']
            logging.info("PREDICT DUMMY DATA : " + str(resultTemp))
            prom.REQUEST_PREDICTION_DUMMY.labels('prediction dummy', request.method, request.path).set(resultTemp)
            return jsonify(predictEtlData(loaded_model,request.json))
        except Exception as e:
            logging.info("PREDICT DUMMY DATA ERROR: " + str(e))
            return str(e)
    else:
        return None

# UTIL FUNC
def load_model():
    global loaded_model
    loaded_model = loadModelMLFlow()

def checkDB():
    if len(list(dbext.dummy_col.find())) == 0:
        df_wine = pd.read_csv(os.path.join("app","static", "wine-quality.csv"))
        df_wine['datetime_'] = datetime.now()
        len_df_wine = len(df_wine) + 1
        for i in df_wine.index:
            df_wine.loc[i,'datetime_'] = datetime.now() - timedelta(minutes = len_df_wine*5)
            len_df_wine-=1
        dict_wine = df_wine.to_dict('records')
        dbext.dummy_col.insert_many(dict_wine)


@app.before_first_request
def before_first_request():
    load_model()
    logging.info("LOAD MODEL MLFLOW : ",str(loaded_model))
    checkDB()

if __name__ == "__main__":
    load_model()
    app.run(host="127.0.0.1",debug=True, use_reloader=False)