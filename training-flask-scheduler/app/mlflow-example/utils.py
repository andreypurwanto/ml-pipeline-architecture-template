import mlflow
from datetime import datetime, timedelta
import time
from minio import Minio
from database import DB
import pandas as pd
import os

def getModelsInfo(mv,client):
    result = []
    count = 0
    for m in mv:
        result.append([])
        result[count] = {
            "version" : m.version,
            "run_id" : m.run_id,
            "current_stage" : m.current_stage,
            "mae" : client.get_metric_history(str(m.run_id),"mae")[0].value
        }
    return result

def compareModel():
    name = "sk-learn-linear-reg-model"
    client = mlflow.tracking.MlflowClient()
    models = client.get_latest_versions(name, stages=["None"])
    latestModelsResult = getModelsInfo(models,client)
    modelStaging = []
    modelProduction = []
    countStaging = 0
    countProduction = 0
    for mv in client.search_model_versions("name='sk-learn-linear-reg-model'"):
        if dict(mv)["current_stage"] == "Staging":
            modelStaging.append([])
            modelStaging[countStaging] = {
                "version" : dict(mv)["version"],
                "run_id" : dict(mv)["run_id"],
                "current_stage" : dict(mv)["current_stage"],
                "mae" : client.get_metric_history(str(dict(mv)["run_id"]),"mae")[0].value
            }
            countStaging+=0
        elif dict(mv)["current_stage"] == "Production":
            modelProduction.append([])
            modelProduction[countProduction] = {
                "version" : dict(mv)["version"],
                "run_id" : dict(mv)["run_id"],
                "current_stage" : dict(mv)["current_stage"],
                "mae" : client.get_metric_history(str(dict(mv)["run_id"]),"mae")[0].value
            }
            countProduction+=0
    
    if len(modelStaging) > 0:
        if latestModelsResult[0]["mae"] < modelStaging[0]["mae"]:
            client.transition_model_version_stage(
                name=name,
                version=latestModelsResult[0]["version"],
                stage="Staging"
            )
            client.transition_model_version_stage(
                name=name,
                version=modelStaging[0]["version"],
                stage="Archived"
            )
        else:
            client.transition_model_version_stage(
                name=name,
                version=latestModelsResult[0]["version"],
                stage="Archived"
            )
    else:
        client.transition_model_version_stage(
                name=name,
                version=latestModelsResult[0]["version"],
                stage="Staging"
            )

def deleteFolder(bucketname, folderName):
    minioClient = Minio(os.environ["MLFLOW_S3_ENDPOINT_URL"], access_key=os.environ["AWS_ACCESS_KEY_ID"], secret_key=os.environ["AWS_SECRET_ACCESS_KEY"], secure=False)
    objects_to_delete = minioClient.list_objects(bucketname, prefix=folderName, recursive=True)
    for obj in objects_to_delete:
        minioClient.remove_object(bucketname, obj.object_name)

def deleteModelWithinRange(client=mlflow.tracking.MlflowClient(),hours=12,modelName="sk-learn-linear-reg-model"):
    boundaryTime = datetime.now() - timedelta(0,0,0,0,0,hours)
    boundaryTimeEpoch = int(time.mktime(boundaryTime.timetuple())*1000)
    # Search Model
    for mv in client.search_model_versions("name='{}'".format(modelName)):
        if boundaryTimeEpoch > dict(mv)["creation_timestamp"]:
            try:
                client.delete_model_version(name=modelName, version=dict(mv)["version"])
                deleteFolder('mlflow', '0/{}'.format(dict(mv)['run_id']))
            except Exception as err:
                print(err)
            print("deleted version {}".format(dict(mv)["version"]))

def getData():
    dbext = DB(host=os.environ["HOSTDBEXT"],port=os.environ["PORTDBEXT"],username=os.environ["USERNAMEDBEXT"],password=os.environ["PASSWORDDBEXT"])
    data = pd.DataFrame(list(dbext.dummy_col.find()))
    data.drop(['_id','datetime_'], inplace=True, axis=1)
    return data
