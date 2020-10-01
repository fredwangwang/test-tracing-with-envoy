import logging
import os
import time
import socket
import urllib
import requests
from flask import Flask
from flask import request
from opentracing import Format
from jaeger_client import Config

# reference: https://opentracing.io/guides/python/

# using this library can simplify the code a bit: https://github.com/opentracing-contrib/python-flask

service_name = os.environ.get('SERVICE_NAME', default='checkAvailability')
port = int(os.environ.get('PORT', default='8080'))

app = Flask(__name__)


log_level = logging.DEBUG
logging.getLogger('').handlers = []
logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)

config = Config(
    config={  # usually read from some yaml config
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'local_agent': {
            'reporting_host': 'jaeger',
            'reporting_port': '6831',
        },
        'logging': True,
    },
    service_name=service_name,
    validate=True,
)
tracer = config.initialize_tracer()


def before_inbound(request, tracer):
    span_context = tracer.extract(
        format=Format.HTTP_HEADERS,
        carrier=request.headers,
    )
    span = tracer.start_span(
        operation_name=service_name,
        child_of=span_context
    )
    return span


@app.route('/proper/<service_number>')
def hello(service_number):
    span = before_inbound(request, tracer)
    with tracer.scope_manager.activate(span, True) as scope: # create the inbound span
        if service_name != 'checkStock':
            # create an outbound span for issuing request
            outbound_span = tracer.start_span(
                operation_name='checkStock', child_of=scope.span)
            http_header_carrier = {}
            # inject and pass the parent span as http headers to the outbound request
            tracer.inject(span_context=outbound_span, format=Format.HTTP_HEADERS, carrier=http_header_carrier)
            requests.get("http://service2:8000/proper/2", headers=http_header_carrier)
        return 'Hello from behind Envoy (service {})! hostname: {}\n'.format(service_name, socket.gethostname())

@app.route('/broken/<service_number>')
def hello1(service_number):
    span = before_inbound(request, tracer)
    with tracer.scope_manager.activate(span, True) as scope: # create the inbound span
        if service_name != 'checkStock':
            # create an outbound span for issuing request
            outbound_span = tracer.start_span(
                operation_name='checkStock', child_of=scope.span)
            http_header_carrier = {}
            # inject and pass the parent span as http headers to the outbound request
            # tracer.inject(span_context=outbound_span, format=Format.HTTP_HEADERS, carrier=http_header_carrier)
            requests.get("http://service2:8000/proper/2", headers=http_header_carrier)
        return 'Hello from behind Envoy (service {})! hostname: {}\n'.format(service_name, socket.gethostname())



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
