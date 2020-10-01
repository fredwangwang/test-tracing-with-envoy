FROM python:alpine3.12

RUN pip install requests flask opentracing jaeger_client

COPY ./service-jaeger.py /service-jaeger.py


ENTRYPOINT [ "python", "/service-jaeger.py" ]