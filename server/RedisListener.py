# RedisListener.py

import redis
#import settings
from . import settings
import threading
import logging
import json
#import McrpType

#Redis = lambda name:McrpType.typedproperty(name, redis)
#Redis = lambda name:McrpType.typedproperty(name, redis)
#Redis = lambda name:McrpType.typedproperty(name, redis)
#Redis = lambda name:McrpType.typedproperty(name, redis)
#Redis = lambda name:McrpType.typedproperty(name, redis)

class Listener(threading.Thread):
    def __init__(self, r, channels, backend):
        threading.Thread.__init__(self)
        self.redis = r
        self.backend = backend
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)
    def stop(self):
        #print ("unsubscribed and finished")
        self.pubsub.unsubscribe()   
        logging.info("Thread is going to stop, gracefully")
        #break
    def work(self, item):
        #print(item['channel'], ":", item['data'])
        if type(item['data']) == int:
            return
        try:
            data = json.loads(item['data'].decode('utf-8'))
            if data.get('cid'):
                cids = data['cid']
            else:
                cids = []
            if data.get('gid'):
                gid = data['gid']
            else:
                gid = []
            if data.get('cid'):
                data.pop('cid')
            if data.get('gid'):
                data.pop('gid')
            for cid in cids:
                msg = [bytes(cid, 'UTF-8'), b'7', bytes(json.dumps(data), 'UTF-8')]
                logging.info('Send To: {0} {1}'.format(cid, data))
                self.backend.send_multipart(msg)  
            if len(gid) > 0:
                cidlist = self.redis.get(gid)
                if len(cidlist) > 0:
                    for cid in cidlist:
                        msg = [bytes(cid, 'UTF-8'), b'7',bytes(json.dumps(data), 'UTF-8')]
                        logging.info('Send To: {0} {1}'.format(cid, data))
                        self.backend.send_multipart(msg)                 
        except ValueError as err:
            logging.error('Invalid json: {}'.format(err))
    def run(self):
        for item in self.pubsub.listen():
            print (item)
            if item['data'] == b'KILL':
                logging.info("unsubscribed and finished, gracefully exit")
                self.pubsub.unsubscribe()   
                break
            else:
                self.work(item)
    