import os
import logging
from slacker import Slacker
from redis import StrictRedis

log = logging.getLogger('slackn')
icon_url = 'https://slack.global.ssl.fastly.net/4324/img/services/nagios_48.png'

class Attachment(object):
    """ Nagios notification formatted as a Slack attachment """
    def __init__(self, title, fields):
        self.props = { 'mrkdwn_in': ['fields'],
                       'title': title,
                       'color': 'good',
                       'fields': [] }
        for f in fields:
            self.append_field(f)

    def append_field(self, text, bold=False):
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
    def __init__(self, slack_token, slack_channel):
        self.slack = Slacker(slack_token)
        self.channel = slack_channel
        self.attachments = []

    def send(self):
        attach = [ a.props for a in self.attachments ]

        if not attach:
            log.info('no notifications to send')
            return

        res = self.slack.chat.post_message(self.channel, '', 'nagios',
                attachments=attach, icon_url=icon_url)
        log.info('slack notification sent')
        if not res.successful:
#            log.error('slack notification failed:\n%s' % res.error)
            raise Exception('slack notification failed:\n%s' % res.error)

    def add_host(self, hostname, messages):
        self.attachments.append(Attachment(hostname, messages))

class Queue(object):
    def __init__(self, redis_host, redis_port):
        self.redis = StrictRedis(host=redis_host, port=int(redis_port),
                                 decode_responses=True)

    def submit(self, notify_args):
        key = 'slackn:%s' % notify_args['hostname']
        notify_msg = self._format(notify_args)

        self.redis.lpush(key, notify_msg)
        self.increment('queued', 1)
        log.debug('notification queued: %s' % notify_msg) 

    def dump(self):
        ret = {}
        for k in self.redis.keys(pattern='slackn:*'):
            hostname = k.replace('slackn:', '')
            ret[hostname]= self.redis.lrange(k, 0, -1)
            self.redis.delete(k)

        return ret

    def increment(self, field, count):
        self.redis.hincrby('slackn_stats', field, count)

    def _format(self, notify_args):
        if notify_args['nagiostype'] == 'ACKNOWLEDGEMENT':
            return self._format_ack(notify_args)

        msg = '{} is {}: {}'
        if notify_args['type'] == 'host':
            return msg.format(notify_args['hostname'],
                              notify_args['hoststate'],
                              notify_args['hostoutput'])
        elif notify_args['type'] == 'service':
            return msg.format(notify_args['servicedesc'],
                              notify_args['servicestate'],
                              notify_args['serviceoutput'])

    def _format_ack(self, notify_args):
        msg = 'ACKNOWLEDGED: {} is {}: {}'
        if notify_args['type'] == 'host':
            return msg.format(notify_args['hostname'])
        elif notify_args['type'] == 'service':
            return msg.format(notify_args['servicedesc'])
