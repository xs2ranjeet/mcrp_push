import zmq
import logging
import redis
import time
from . import util
from .settings import rq, serverConfig
#from settings
from .RedisListener import Listener
from collections import OrderedDict

HEARTBEAT_LIVENESS = 3     # 3..5 is reasonable

#class Worker(object):
    #def __init__(self, address):
        #self.address = address
        #self.expiry = time.time() + serverConfig['heartbeat_interval'] * HEARTBEAT_LIVENESS

#class WorkerQueue(object):
    #def __init__(self):
        #self.queue = OrderedDict()

    #def ready(self, worker):
        #self.queue.pop(worker.address, None)
        #self.queue[worker.address] = worker
    #def next(self):
        #address, worker = self.queue.popitem(False)
        #print(address)
        #print(worker)
        #return address
def send_message(address, event, data, backend):
    if data == None:
        msg = [address, event]
    else:
        msg = [address, event, data]
    backend.send_multipart(msg)
def isValidaAddress(address):
    if len(address) < 5 or len(address) > 10:
        return False
    #if address.find("+") or address.find("000"):
        #return False
    rq.sadd(serverConfig['valid_user_prefix_rediskey']+util.getCurrentTimeStampKey(), address)
    return True
    
def ProcessClientRequest(frames, backend):
    if not frames:
        return
    logging.info(frames)
    address = frames[0]
    #workers.ready(Worker(address))
    #print(frames[1])
    #for f in frames:
        #print(f)
    #print(address)
    if isValidaAddress(address) ==  False:
        send_message(address,  bytes(serverConfig['invalid_client_event'], encoding='ascii'), b'1', backend)
        return
    rq.set(serverConfig['last_client_ping_rediskey'],util.getCurrentTimeStamp())
    if frames[1]==serverConfig['client_connect_event']:
        send_message(address, bytes(serverConfig['client_connect_reply_event'], encoding='ascii'), None, backend)
    elif frames[1]==serverConfig['hb_receive_event']:
        send_message(address, bytes(serverConfig['hb_send_event'], encoding='ascii'), None, backend)
    elif frames[1]==serverConfig['reg_data_event']:
        rq.hset(serverConfig['reg_data_key'], address, frames[2].decode())
        send_message(address, bytes(serverConfig['reg_data_reply_event'], encoding='ascii'), None, backend)
    
def StartServer():
    logging.info("Server Start")
    context = zmq.Context(1)
    backend = context.socket(zmq.ROUTER)  # ROUTER

    backend.bind(str("tcp://*:"+str(serverConfig['port'])))  # For workers
    #workers = WorkerQueue()
    client = Listener(rq, [serverConfig['subscribe_channel']],backend)
    client.start()    
    
    poll_workers = zmq.Poller()
    poll_workers.register(backend, zmq.POLLIN)
    ping_at = time.time() + serverConfig['ping_interval']
    try:
        while True:
            poller = poll_workers
            socks = dict(poller.poll(serverConfig['heartbeat_interval'] * 1000))
        
            # Handle worker activity on backend
            if socks.get(backend) == zmq.POLLIN:
                # Use worker address for LRU routing
                frames = backend.recv_multipart()
                ProcessClientRequest(frames, backend)
            if time.time() >= ping_at:
                ping_at = time.time() + serverConfig['ping_interval']
                rq.set(serverConfig['last_zmq_server_ping_rediskey'],util.getCurrentTimeStamp())
    except:
        logging.info('ZMQ Polling Exception caught')
    logging.info('Exiting the Server')
    client.stop()
    