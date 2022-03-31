import mlflow
import pandas as pd

def loadModelMLFlow():
    # Load from model name and stage
    model_name = "sk-learn-linear-reg-model"
    stage = 'Staging'
    loaded_model = mlflow.pyfunc.load_model(
        model_uri=f"models:/{model_name}/{stage}"
    )
    return loaded_model

def predictData(loaded_model):
    # Test input data
    data =  {
        "alcohol":[12.8], 
        "chlorides":[0.029], 
        "citric acid":[0.48], 
        "density":[0.98], 
        "fixed acidity":[6.3], 
        "free sulfur dioxide":[29], 
        "pH":[3.33], 
        "residual sugar":[1.2], 
        "sulphates":[0.39], 
        "total sulfur dioxide":[75], 
        "volatile acidity":[0.66]
        }
    return {
        "modelInfo" : str(loaded_model),
        "result" : str(loaded_model.predict(pd.DataFrame(data)))
    }

def predictEtlData(loaded_model, data):
    return {
        "modelInfo" : str(loaded_model),
        "result" : loaded_model.predict(pd.DataFrame(data, index=[0]))[0]
    }