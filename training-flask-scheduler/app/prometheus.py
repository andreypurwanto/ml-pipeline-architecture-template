from prometheus_client import Gauge, Counter

class PROM():
    def __init__(self):
        self.REQUEST_TRAINING_PROCESS_LATENCY_SECOND = Gauge(
            'request_training_process_latency_second', 'Training Process Latency Seconds',
            ['app_name', 'method']
        )
        self.REQUEST_TRAINING_PROCESS_COUNTER = Counter(
            'request_training_process_counter', 'Training Process Counter',
            ['app_name', 'method']
        )
        self.REQUEST_TRAINING_PROCESS_ERROR = Gauge(
            'request_training_process_error', 'Training Process Error',
            ['app_name', 'method']
        )