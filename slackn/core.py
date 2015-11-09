import os
import logging
from uuid import uuid4
from redis import StrictRedis

class SlacknDB(object):
    def __init__(self, redis_host, redis_port):
        self.redis = StrictRedis(host=redis_host, port=int(redis_port),
                                 decode_responses=True)

    def notify_host(self, notify_args):
        self.redis.hmset('hosts:' + str(uuid4()), notify_args)

    def notify_service(self, notify_args):
        self.redis.hmset('services:' + str(uuid4()), notify_args)

    def get_hosts(self):
        return [ self.redis.hgetall(k) for k in \
                 self.redis.keys(pattern='hosts:*') ] 

    def get_services(self):
        return [ self.redis.hgetall(k) for k in \
                 self.redis.keys(pattern='services:*') ] 

    def _state_color(self, state):
        if state == 'CRITICAL':
            return 'red'
        elif state == 'WARNING':
            return 'yellow'
        else:
            return 'green'
