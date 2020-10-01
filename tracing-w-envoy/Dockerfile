FROM python:alpine3.12

RUN pip install requests flask opentracing jaeger_client

COPY ./service.py /service.py


ENTRYPOINT [ "python", "/service.py" ]