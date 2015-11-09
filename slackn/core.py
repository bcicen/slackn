import os
import uuid
import logging
from redis import StrictRedis

class SlacknDB(object):
    def __init__(self, redis_host, redis_port):
        self.redis = StrictRedis(host=redis_host, port=int(redis_port),
                                 decode_responses=True)

    def _add_host(self, **kwargs):
        self.redis.hmset('hosts:' + uuid.uuid4(), kwargs)

    def _add_service(self, **kwargs):
        self.redis.hmset('services:' + uuid.uuid4(), kwargs)

    def _get_hosts(self):
        return [ self.redis.hgetall(k) for k in \
                 self.redis.keys(pattern='hosts:*') ] 

    def _get_services(self):
        return [ self.redis.hgetall(k) for k in \
                 self.redis.keys(pattern='services:*') ] 

    def _state_color(self, state):
        if state == 'CRITICAL':
            return 'red'
        elif state == 'WARNING':
            return 'yellow'
        else:
            return 'green'
        
