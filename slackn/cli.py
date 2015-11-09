import sys
import logging
from argparse import ArgumentParser

from slackn.core import SlacknDB
from slackn.version import version

log = logging.getLogger('slackn')

def setup_db(s):
    if ':' in s:
        host,port = s.split(':')
    else:
        host,port = (s, 6379)
    return SlacknDB(host,port)

def process():
    parser = ArgumentParser(description='slackn_process v%s' % version)
    parser.add_argument('--slack-channel',
                        help='channel to send notifications')
    parser.add_argument('--redis',
                        default='127.0.0.1:6379',
                        help='redis host:port to connect to')

    args = parser.parse_args()

    db = setup_db(args.redis)

def notify():
    common_parser = ArgumentParser(add_help=False)
    common_parser.add_argument('--redis',
                        help='redis host to connect to (127.0.0.1:6379)',
                        default='127.0.0.1:6379')

    parser = ArgumentParser(description='slackn-notify %s' % version,
                            parents=[common_parser])
    subparsers = parser.add_subparsers(description='notification type',
                                       dest='subcommand')

    parser_host = subparsers.add_parser('host')
    parser_host.add_argument('hostname')
    parser_host.add_argument('hoststate')
    parser_host.add_argument('hostoutput')

    parser_service = subparsers.add_parser('service')
    parser_service.add_argument('hostname')
    parser_service.add_argument('servicedesc')
    parser_service.add_argument('servicestate')
    parser_service.add_argument('serviceoutput')

    args = parser.parse_args()

    db = setup_db(args.redis)

    notify_args = { k:v for k,v in args.__dict__.items() }
    for k in ('redis','subcommand'):
        del notify_args[k]

    db.add_notification(args.subcommand, notify_args)
