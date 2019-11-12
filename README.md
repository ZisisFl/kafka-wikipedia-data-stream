# Real-time data stream with EventStreams and Kafka

This simple script is a demo of consuming an SSE protocol stream with Python and creating a Kafka Producer on a local Broker in order to create a stream of data with the structure of your choice that can later be used for real time analytics and visualisations using Druid and Superset.

In order to run this example you need to understand some basics of Apache Kafka and have it installed in your machine. You must also create a Kafka topic named wikipedia-streams-sse or change the topic name in the last line of the code. This script is also set to send data to a Kafka Producer at localhost:9092.

More info on how to start up Kafka Broker create a topic, produce messages and consume them can be found [here].

[here]: <https://kafka.apache.org/quickstart>
