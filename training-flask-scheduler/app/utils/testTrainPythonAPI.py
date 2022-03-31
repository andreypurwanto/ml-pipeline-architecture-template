import mlflow
import os

def trainModel():
    project_uri = os.path.join("app","mlflow-example")
    params = {"alpha": 0.5, "l1_ratio": 0.01}
    mlflow.run(project_uri, parameters=params, use_conda=False)