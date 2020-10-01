import logging
import os
import time
import socket
import urllib
import requests
from flask import Flask
from flask import request

service_name = os.environ.get('SERVICE_NAME', default='checkAvailability')
port = int(os.environ.get('PORT', default='8080'))

app = Flask(__name__)

TRACE_HEADERS_TO_PROPAGATE = [
    'X-Ot-Span-Context',
    'X-Request-Id',

    # Zipkin headers
    'X-B3-TraceId',
    'X-B3-SpanId',
    'X-B3-ParentSpanId',
    'X-B3-Sampled',
    'X-B3-Flags',

    # Jaeger header (for native client)
    "uber-trace-id"
]


@app.route('/proper/<service_number>')
def hello(service_number):
    if service_name != 'checkStock':
        http_header_carrier = {}
        for header in TRACE_HEADERS_TO_PROPAGATE:
            if header in request.headers:
                http_header_carrier[header] = request.headers[header]
        requests.get("http://localhost:9000/proper/2", headers=http_header_carrier)
    return 'Hello from behind Envoy (service {})! hostname: {}\n'.format(service_name, socket.gethostname())


@app.route('/broken/<service_number>')
def hello1(service_number):
    if service_name != 'checkStock':
        requests.get("http://localhost:9000/proper/2")
    return 'Hello from behind Envoy (service {})! hostname: {}\n'.format(service_name, socket.gethostname())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
