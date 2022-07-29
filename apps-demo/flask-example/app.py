# flask_web/app.py

import os
from logging import INFO, StreamHandler, getLogger
from logging.handlers import RotatingFileHandler
from random import random
from time import sleep

import requests
from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

logPath = "/python-docker/log"
fileName = "app_log"


fileHandler = RotatingFileHandler(
    "{0}/{1}.log".format(logPath, fileName),
    maxBytes=100, backupCount=10)
# fileHandler.setFormatter(jsonlogger.JsonFormatter())
fileHandler.setLevel(INFO)

consoleHandler = StreamHandler()
app.logger.addHandler(consoleHandler)
app.logger.addHandler(fileHandler)
# logging.getLogger('werkzeug').setLevel(logging.INFO)
getLogger('werkzeug').addHandler(fileHandler)
getLogger('werkzeug').addHandler(consoleHandler)
app.logger.setLevel(INFO)

otlp_exporter = OTLPSpanExporter(insecure=True)
trace.set_tracer_provider(TracerProvider(
    resource=Resource.create(
        {SERVICE_NAME: "demo1-flask-service"}
    )
))
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

FlaskInstrumentor().instrument_app(app, excluded_urls="client/.*/info,healthcheck")
RequestsInstrumentor().instrument()
tracer = trace.get_tracer(__name__)
# logFormatter = logging.Formatter(
#     json.dumps(
#         {"time": "%(asctime)s", "name": "%(name)s",
#          "level": "%(levelname)s", "message": '%(message)s'
#          }
#     )
# )


@ app.route('/')
def hello_world():
    app.logger.info("test")
    return 'Hey, we have Flask in a Docker container!'


@ app.route('/doc/generate')
def hello_world_generate():
    # with tracer.start_as_current_span("demo2-request", attributes={"endpoint": "/doc/generate"}):
    requests.get("http://demo.demo2.svc.cluster.local:5000/long-time")

    app.logger.info("generate")
    return 'Hey, trigger generate api call'


endpoints = ("one", "two", "three", "four", "five", "error")


@ app.route("/one")
def first_route():
    sleep(random() * 0.2)
    return "ok"


@ app.route("/two")
def the_second():
    sleep(random() * 0.4)
    return "ok"


@ app.route("/three")
def test_3rd():
    sleep(random() * 0.6)
    return "ok"


@ app.route("/four")
def fourth_one():
    sleep(random() * 0.8)
    return "ok"


@ app.route("/error")
def oops():
    return ":(", 500


if __name__ == "__main__":
    app.run("0.0.0.0", 5000, threaded=True)
