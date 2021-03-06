import os
import logging
import datetime
from datetime import datetime
from slacker import Slacker
from redis import StrictRedis

log = logging.getLogger('slackn')
icon_url = 'https://slack.global.ssl.fastly.net/4324/img/services/nagios_48.png'

stats_key = 'slackn_stats'

class Attachment(object):
    """ Nagios notification formatted as a Slack attachment """
    def __init__(self, title, fields):
        self.props = { 'mrkdwn_in': ['fields'],
                       'title': title,
                       'color': '#eee',
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
        if 'OK' in text:
            self.props['color'] = 'good'

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

    def add_attachment(self, title, messages):
        self.attachments.append(Attachment(title, messages))

class Queue(object):
    def __init__(self, redis_host, redis_port):
        self.redis = StrictRedis(host=redis_host, port=int(redis_port),
                                 decode_responses=True)

    def submit(self, notify_args):
        key = 'slackn:%s' % notify_args['hostname']
        notify_msg = self._format(notify_args)

        self.redis.lpush(key, notify_msg)

        self._stats(notify_args)

        log.debug('notification queued: %s' % notify_msg) 

    def dump(self):
        ret = {}
        for k in self.redis.keys(pattern='slackn:*'):
            hostname = k.replace('slackn:', '')
            ret[hostname]= self.redis.lrange(k, 0, -1)
            self.redis.delete(k)

        return ret

    def dump_stats(self):
        ret = { k.replace('host:', ''):v for k,v in \
                self.redis.hgetall(stats_key).items() }
        
        return ret

    def _stats(self, notify_args):
        """ Record attributes of the notification to Redis """
        now = str(datetime.utcnow())
        self._increment('notifications', 1)
        self._increment('host:' + notify_args['hostname'], 1)
        self.redis.hset(stats_key, 'last_notification', now)

    def _increment(self, field, count):
        self.redis.hincrby(stats_key, field, count)

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
        msg = 'ACKNOWLEDGED: {}'
        if notify_args['type'] == 'host':
            return msg.format(notify_args['hostname'])
        elif notify_args['type'] == 'service':
            return msg.format(notify_args['servicedesc'])
