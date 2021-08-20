FROM python:3.8-alpine
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY wikipedia_events_kafka_producer.py wikipedia_events_kafka_producer.py
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python3", "wikipedia_events_kafka_producer.py"]