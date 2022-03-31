from flask import Flask, request, jsonify, Response
import numpy as np
from pydantic import ValidationError
from app.database import DB
from flask_apscheduler import APScheduler
from datetime import datetime
import os
import requests
import logging
from app.utils.logger import SetUpLogging
from app.utils.testTrainPythonAPI import *
from app.prometheus import PROM
from app.middleware import setup_metrics
import prometheus_client
import warnings
import time

warnings.simplefilter(action='ignore', category=FutureWarning)

class Config:
    """App configuration."""
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Utc" 

# LOGGER
SetUpLogging().setup_logging()

# APP
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
    return str("Flask Scheduler")

# Scheduler
@scheduler.task('interval', id='training', hours=1)
def trainingJob():
    try:
        start_time = time.time()
        trainModel()
        logging.info("SCHEDULED TRAINING SUCCESS " + str(scheduler.get_job('training')))
        r = requests.get(os.environ["LOADMODELAPI"])
        logging.info("LOAD LATEST MODEL SUCCESS " + str(scheduler.get_job('training')))
        prom.REQUEST_TRAINING_PROCESS_LATENCY_SECOND.labels('etl_process_latency_seconds', 'SCHEDULER').set(time.time()-start_time)
        prom.REQUEST_TRAINING_PROCESS_COUNTER.labels('etl_process_latency_seconds', 'SCHEDULER').inc()
        prom.REQUEST_TRAINING_PROCESS_ERROR.labels('etl_process_latency_seconds', 'SCHEDULER').set(0)
        return str("Success")
    except Exception as e:
        logging.warning("SCHEDULED TRAINING FAILED " + str(e))
        prom.REQUEST_TRAINING_PROCESS_LATENCY_SECOND.labels('etl_process_latency_seconds', 'SCHEDULER').set(0)
        prom.REQUEST_TRAINING_PROCESS_COUNTER.labels('etl_process_latency_seconds', 'SCHEDULER').inc()
        return str(e)

@app.route('/modifyTrainingJob/', methods=['GET','POST'])
def modifyTrainingJob():
    print(request.json)
    param = request.json
    try:
        scheduler.modify_job('training', **param)
        return str(scheduler.get_job('training'))
    except Exception as e:
        return str(e)

@app.route('/getTrainingJob/', methods=['GET'])
def getTrainingJob():
    return str(scheduler.get_job('training'))

@app.route('/pauseTrainingJob/', methods=['GET'])
def pauseTrainingJob():
    str(scheduler.pause_job('training'))
    return str(scheduler.get_job('training'))

@app.route('/resumeTrainingJob/', methods=['GET'])
def resumeTrainingJob():
    str(scheduler.resume_job('training'))
    return str(scheduler.get_job('training'))

@app.route('/manualTraining/', methods=['GET'])
def manualTraining():
    try:
        trainModel()
        logging.info("MANUAL TRAINING SUCCESS " + str(scheduler.get_job('training')))
        r = requests.get(os.environ["LOADMODELAPI"])
        logging.info("LOAD LATEST MODEL SUCCESS " + str(scheduler.get_job('training')))
        return str("Success")
    except Exception as e:
        logging.warning("MANUAL TRAINING FAILED " + str(e))
        return str(e)

@app.route('/dir/', methods=['GET'])
def dir():
    try:
        return str(os.getcwd())
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)