from prometheus_client import Gauge

class PROM():
    def __init__(self):
        self.REQUEST_PREDICTION_DUMMY = Gauge(
            'request_prediction_dummy', 'Prediction Dummy',
            ['app_name', 'method', 'endpoint']
        )