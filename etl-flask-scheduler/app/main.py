from tkinter import E
from flask import Flask, request, jsonify, Response
import numpy as np
from pydantic import ValidationError
from app.database import DB
from flask_apscheduler import APScheduler
import requests
import logging
from app.utils.logger import SetUpLogging
from app.utils.testETL import *
from app.prometheus import PROM
from app.middleware import setup_metrics
import prometheus_client
import json
import time
import os

class Config:
    """App configuration."""
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Utc" 

# LOGGER
SetUpLogging().setup_logging()

app = Flask(__name__)
app.config.from_object(Config())

# DB
dbext = DB(host=os.environ["HOSTDBEXT"],port=os.environ["PORTDBEXT"],username=os.environ["USERNAMEDBEXT"],password=os.environ["PASSWORDDBEXT"])

# SCHEDULER
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# PROM
prom = PROM()
setup_metrics(app)
@app.route('/metrics')
def metrics():
    CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')
    return Response(prometheus_client.generate_latest(), mimetype=CONTENT_TYPE_LATEST)

#RESTAPI
@app.route('/', methods=['GET', 'POST'])
def hello():
    return str("Flask ETL Scheduler")

# Scheduler
@scheduler.task('interval', id='etl', minutes=5)
def etlJob():
    try:
        start_time = time.time()
        dataInput = dummyETL(dbext)
        del dataInput["_id"]
        del dataInput["datetime_"]
        del dataInput["quality"]
        url = os.environ["PREDICTAPI"]
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(dataInput), headers=headers)
        logging.info("SCHEDULED ETL SUCCESS " + str(scheduler.get_job('etl')))
        prom.REQUEST_ETL_PROCESS_LATENCY_SECOND.labels('etl_process_latency_seconds', 'SCHEDULER').set(time.time()-start_time)
        prom.REQUEST_ETL_PROCESS_COUNTER.labels('etl_process_latency_seconds', 'SCHEDULER').inc()
        prom.REQUEST_ETL_PROCESS_ERROR.labels('etl_process_latency_seconds', 'SCHEDULER').set(0)
        return str(dataInput)
    except Exception as e:
        logging.warning("SCHEDULED ETL FAILED " + str(e))
        prom.REQUEST_ETL_PROCESS_LATENCY_SECOND.labels('etl_process_latency_seconds', 'SCHEDULER').set(0)
        prom.REQUEST_ETL_PROCESS_ERROR.labels('etl_process_latency_seconds', 'SCHEDULER').inc()
        return str(e)

# API Scheduler
@app.route('/modifyEtlJob/', methods=['GET','POST'])
def modifyEtlJob():
    print(request.json)
    param = request.json
    try:
        scheduler.modify_job('etl', **param)
        return str(scheduler.get_job('etl'))
    except Exception as e:
        return str(e)

@app.route('/getEtlJob/', methods=['GET'])
def getEtlJob():
    return str(scheduler.get_job('etl'))

@app.route('/pauseEtlJob/', methods=['GET'])
def pauseEtlJob():
    str(scheduler.pause_job('etl'))
    return str(scheduler.get_job('etl'))

@app.route('/resumeEtlJob/', methods=['GET'])
def resumeEtlJob():
    str(scheduler.resume_job('etl'))
    return str(scheduler.get_job('etl'))

@app.route('/manualEtl/', methods=['GET'])
def manualEtl():
    try:
        test = dummyETL(dbext)
        del test["_id"]
        del test["datetime_"]
        del test["quality"]
        url = os.environ["PREDICTAPI"]
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(test), headers=headers)
        logging.info("MANUAL ETL SUCCESS " + str(scheduler.get_job('etl')))
        return jsonify(test)
    except Exception as e:
        logging.warning("SCHEDULED ETL FAILED " + e)
        return str(e)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)