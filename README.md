# Streaming of wikipedia events using Kafka #
This simple Python script makes use of the [EventStreams](https://wikitech.wikimedia.org/wiki/Event_Platform/EventStreams) web service which exposes a stream of structured events over HTTP following SSE protocol. Those events include information about the editing of wikipedia web pages, creation of new ones and more. For the sake of this project we filter out only the events related to the editing of existings pages. Those events are being parsed into an appropriate format and get sent back to a Kafka topic.

We construct events that are sent to Kafka with the following format:
```json
{
"id": 1426354584, 
"domain": "www.wikidata.org", 
"namespace": "main namespace", 
"title": "articles_title", 
"timestamp": "2021-03-14T21:55:14Z", 
"user_name": "a_user_name", 
"user_type": "human", 
"old_length": 6019, 
"new_length": 8687
}
```

## In order to reproduce this project ##
- Start a Kafka Broker at localhost:9092.
- Create a topic named **wikipedia-events**

More info on how to start up Kafka Broker create a topic, produce messages and consume them can be found [here](https://kafka.apache.org/quickstart).

### Run without Docker ###
Create a Python 3 virtual environment installing all needed libraries using requirements.txt file included in this project:

```sh
python3 -m venv kafka_venv
source kafka_venv/bin/activate
pip install -r requirements.txt
```

Εxecute the wikipedia_events_kafka_producer.py file
```sh
python wikipedia_events_kafka_producer.py 
```

You can pass arguments in order to change the limit of events to produce, host and port of kafka broker and destination topic, for more info:
```sh
python wikipedia_events_kafka_producer.py -h
```

### Run with Docker ###
Build docker image:
```sh
docker build -t wikipedia_events_kafka_producer .
```

Run docker app:
```sh
docker run --network="host" wikipedia_events_kafka_producer
```

You can provide your arguments like that:
```sh
docker run --network="host" wikipedia_events_kafka_producer --events_to_produce=10000
```

**Note:** It is important to use `--network="host"` option in order to point the container to the docker host.


## Medium article ##
You can find the complete tutorial [in this Medium article](https://towardsdatascience.com/introduction-to-apache-kafka-with-wikipedias-eventstreams-service-d06d4628e8d9).