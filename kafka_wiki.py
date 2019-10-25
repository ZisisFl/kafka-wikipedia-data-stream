import json
from sseclient import SSEClient as EventSource
from time import sleep
from json import dumps
from kafka import KafkaProducer

# init producer
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x:
                         dumps(x).encode('utf-8'))

# create a dictionary for the various known namespaces
# https://en.wikipedia.org/wiki/Wikipedia:Namespace#Programming
namespace_dict = {-2: 'Media', -1: 'Special', 0: 'main namespace', 1: 'Talk', 2: 'User', 3: 'User Talk',
                  4: 'Wikipedia', 5: 'Wikipedia Talk', 6: 'File', 7: 'File Talk',
                  8: 'MediaWiki', 9: 'MediaWiki Talk', 10: 'Template', 11: 'Template Talk', 12: 'Help',
                  13: 'Help Talk', 14: 'Category', 15: 'Category Talk', 100: 'Portal', 101: 'Portal Talk',
                  108: 'Book', 109: 'Book Talk', 118: 'Draft', 119: 'Draft Talk', 446: 'Education Program',
                  447: 'Education Program Talk', 710: 'TimedText', 711: 'TimedText Talk', 828: 'Module',
                  829: 'Module Talk', 2300: 'Gadget', 2301: 'Gadget Talk', 2302: 'Gadget definition',
                  2303: 'Gadget definition Talk'}

data = ''
# sse reader
url = 'https://stream.wikimedia.org/v2/stream/recentchange'
for event in EventSource(url):
    if event.event == 'message':
        try:
            change = json.loads(event.data)
        except ValueError:
            pass
        else:
            # keep only the article edits
            if change['type'] == 'edit':
                # use dictionary to change namespace value and catch any unknown namespaces (like ns 104)
                try:
                    change['namespace'] = namespace_dict[change['namespace']]
                except KeyError:
                    change['namespace'] = 'unknown'
                # define the data structure of the json to put in kafka topic
                data = {"id": change['id'],
                        "namespace": change['namespace'],
                        "title": change['title'],
                        "comment": change['comment'],
                        "timestamp": change['timestamp'],
                        "user": change['user'],
                        "bot": change['bot'],
                        "minor": change['minor'],
                        "old_length": change['length']['old'],
                        "new_length": change['length']['new']}
                print(data)
                producer.send('wikipedia-stream-sse', value=data)
