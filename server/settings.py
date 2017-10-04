import redis
import os

redisconfig = {
    #'host': 'xsim-redis.dvkmky.0001.apse1.cache.amazonaws.com',
    'host': 'localhost',    
    'port': 6379,
    'db': 0,
    'password':None,
    'socket_timeout':None
    
}
rq = redis.StrictRedis(**redisconfig)

serverConfig = {
    'port': 5000,
    'last_zmq_server_ping_rediskey' : 'last_zmq_ping',
    'subscribe_channel': 'cmd_robot',
    'ping_interval': 30.0,
    'heartbeat_interval': 1,
    'reg_data_event': '54',
    'reg_data_key': 'REG_DATA',
    'reg_data_reply_event': '154',
    'hb_receive_event':'3',
    'hb_send_event' : '4',
    'invalid_client_event': '6',
    'client_connect_event':'1',
    'client_connect_reply_event': '2',
    'valid_user_prefix_rediskey': 'user',
    'last_client_ping_rediskey':'last_client_ping'
}
