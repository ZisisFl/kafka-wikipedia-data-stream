import json
import argparse
from sseclient import SSEClient as EventSource
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable


# https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html
def create_kafka_producer(bootstrap_server):
    try:
        producer = KafkaProducer(bootstrap_servers=bootstrap_server,
                                 value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    except NoBrokersAvailable:
        print('No broker found at {}'.format(bootstrap_server))
        raise
    
    
    if producer.bootstrap_connected():
        print('Kafka producer connected!')
        return producer
    else:
        print('Failed to establish connection!')
        exit(1)


def construct_event(event_data, user_types):
    # use dictionary to change assign namespace value and catch any unknown namespaces (like ns 104)
    try:
        event_data['namespace'] = namespace_dict[event_data['namespace']]
    except KeyError:
        event_data['namespace'] = 'unknown'

    # assign user type value to either bot or human
    user_type = user_types[event_data['bot']]

    # define the structure of the json event that will be published to kafka topic
    event = {"id": event_data['id'],
             "domain": event_data['meta']['domain'],
             "namespace": event_data['namespace'],
             "title": event_data['title'],
             #"comment": event_data['comment'],
             "timestamp": event_data['meta']['dt'],#event_data['timestamp'],
             "user_name": event_data['user'],
             "user_type": user_type,
             #"minor": event_data['minor'],
             "old_length": event_data['length']['old'],
             "new_length": event_data['length']['new']}
    
    return event


def init_namespaces():
    # create a dictionary for the various known namespaces
    # more info https://en.wikipedia.org/wiki/Wikipedia:Namespace#Programming
    namespace_dict = {-2: 'Media', 
                      -1: 'Special', 
                      0: 'main namespace', 
                      1: 'Talk', 
                      2: 'User', 3: 'User Talk',
                      4: 'Wikipedia', 5: 'Wikipedia Talk', 
                      6: 'File', 7: 'File Talk',
                      8: 'MediaWiki', 9: 'MediaWiki Talk', 
                      10: 'Template', 11: 'Template Talk', 
                      12: 'Help', 13: 'Help Talk', 
                      14: 'Category', 15: 'Category Talk', 
                      100: 'Portal', 101: 'Portal Talk',
                      108: 'Book', 109: 'Book Talk', 
                      118: 'Draft', 119: 'Draft Talk', 
                      446: 'Education Program', 447: 'Education Program Talk', 
                      710: 'TimedText', 711: 'TimedText Talk', 
                      828: 'Module', 829: 'Module Talk', 
                      2300: 'Gadget', 2301: 'Gadget Talk', 
                      2302: 'Gadget definition', 2303: 'Gadget definition Talk'}

    return namespace_dict


def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description='EventStreams Kafka producer')

    parser.add_argument('--bootstrap_server', default='localhost:9092', help='Kafka bootstrap broker(s) (host[:port])', type=str)
    parser.add_argument('--topic_name', default='wikipedia-events', help='Destination topic name', type=str)
    parser.add_argument('--events_to_produce', help='Kill producer after n events have been produced', type=int, default=1000)

    return parser.parse_args()


if __name__ == "__main__":
    # parse command line arguments
    args = parse_command_line_arguments()

    # init producer
    producer = create_kafka_producer(args.bootstrap_server)

    # init dictionary of namespaces
    namespace_dict = init_namespaces()

    # used to parse user type
    user_types = {True: 'bot', False: 'human'}

    # consume websocket
    url = 'https://stream.wikimedia.org/v2/stream/recentchange'
    
    print('Messages are being published to Kafka topic')
    messages_count = 0
    
    for event in EventSource(url):
        if event.event == 'message':
            try:
                event_data = json.loads(event.data)
            except ValueError:
                pass
            else:
                # filter out events, keep only article edits (mediawiki.recentchange stream)
                if event_data['type'] == 'edit':
                    # construct valid json event
                    event_to_send = construct_event(event_data, user_types)

                    producer.send('wikipedia-events', value=event_to_send)

                    messages_count += 1
        
        if messages_count >= args.events_to_produce:
            print('Producer will be killed as {} events were producted'.format(args.events_to_produce))
            exit(0)