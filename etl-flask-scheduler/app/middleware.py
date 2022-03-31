from flask import request
from prometheus_client import Counter, Histogram, Gauge
import time

REQUEST_ETL_COUNT = Counter(
    'request_etl_count', 'ETL Request Count',
    ['app_name', 'method', 'endpoint', 'http_status']
)
REQUEST_ETL_LATENCY = Histogram('request_etl_latency', 'ETL Request latency',
    ['app_name', 'endpoint']
)
REQUEST_ETL_LATENCY_SECONDS = Gauge('request_etl_latency_seconds', 'ETL Request latency seconds',
    ['app_name', 'endpoint']
)

def start_timer():
    request.start_time = time.time()
    global start_time
    start_time = time.time()

def stop_timer(response):
    resp_time = time.time() - request.start_time
    resp_time_seconds = time.time() - start_time
    REQUEST_ETL_LATENCY.labels('ETL', request.path).observe(resp_time)
    REQUEST_ETL_LATENCY_SECONDS.labels('ETL', request.path).set(resp_time_seconds)
    return response

def record_request_data(response):
    REQUEST_ETL_COUNT.labels('ETL', request.method, request.path,
            response.status_code).inc()
    return response

def setup_metrics(app):
    app.before_request(start_timer)
    app.after_request(record_request_data)
    app.after_request(stop_timer)