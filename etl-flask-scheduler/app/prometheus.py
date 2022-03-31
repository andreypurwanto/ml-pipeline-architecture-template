from prometheus_client import Gauge, Counter

class PROM():
    def __init__(self):
        self.REQUEST_ETL_PROCESS_LATENCY_SECOND = Gauge(
            'request_etl_process_latency_second', 'ETL Process Latency Seconds',
            ['app_name', 'method']
        )
        self.REQUEST_ETL_PROCESS_COUNTER = Counter(
            'request_etl_process_counter', 'ETL Process Counter',
            ['app_name', 'method']
        )
        self.REQUEST_ETL_PROCESS_ERROR = Gauge(
            'request_etl_process_error', 'ETL Process Error',
            ['app_name', 'method']
        )