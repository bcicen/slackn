import os
import logging
from uuid import uuid4
from slacker import Slacker
from redis import StrictRedis
from collections import defaultdict

log = logging.getLogger('slackn')

class Attachment(object):
    """ Nagios notification formatted as a Slack attachment """
    def __init__(self, title, fields):
        self.props = { 'mrkdwn_in': ['fields'],
                       'title': title,
                       'color': 'good',
                       'fields': [] }
        for f in fields:
            self.append_field(f)

    def append_field(self, text, bold=True):
        self._set_color(text)
        if bold:
            text = '*%s*' % text
        self.props['fields'].append({ 'short': False, 'value': text })

    def _set_color(self, text):
        if 'CRITICAL' in text:
            self.props['color'] = 'danger'
        if 'WARNING' in text:
            self.props['color'] = 'warning'

class Notifier(object):
    def __init__(self, slack_token):
        self.slack = Slacker(slack_token)
        self.attachments = []

    def send(self):
        pass

    def add_attachment(self, hostname, messages):
        self.attachments.append(Attachment(hostname, messages))

class Queue(object):
    def __init__(self, redis_host, redis_port):
        self.redis = StrictRedis(host=redis_host, port=int(redis_port),
                                 decode_responses=True)

    def submit(self, notify_args):
        key = 'slackn:%s' % notify_args['hostname']
        notify_msg = self._format(notify_args)

        self.redis.lpush(key, notify_msg)
        self.increment('queued')
        log.debug('notification queued: %s' % notify_msg) 

    def dump(self):
        ret = {}
        for k in self.redis.keys(pattern='slackn:*'):
            hostname = k.strip('slackn:')
            ret[hostname]= self.redis.lrange(k, 0, -1)
            self.redis.delete(k)

        return ret

    def increment(self, field):
        self.redis.hincrby('slackn_stats', field, 1)

    @staticmethod
    def _format(notify_args):
        msg = '{} is {}:\n{}'
        if notify_args['type'] == 'host':
            return msg.format(notify_args['hostname'],
                              notify_args['hoststate'],
                              notify_args['hostoutput'])
        elif notify_args['type'] == 'service':
            return msg.format(notify_args['servicedesc'],
                              notify_args['servicestate'],
                              notify_args['serviceoutput'])
