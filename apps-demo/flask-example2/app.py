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
    maxBytes=1000, backupCount=10)
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
        {SERVICE_NAME: "demo2-flask-service"}
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
    return 'Hey, we have Flask in a Docker container2!'


@ app.route("/long-time")
def long_time():
    sleep(2)
    sleep_verify()
    return "ok"


def sleep_verify():
    with tracer.start_as_current_span("sleep_verify", attributes={"inner_def_call": "sleep_verify"}):
        sleep(1)
    return


if __name__ == "__main__":
    app.run("0.0.0.0", 5000, threaded=True)
