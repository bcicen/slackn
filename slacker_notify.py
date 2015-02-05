import os,json,logging,notify2,websocket,requests
from time import sleep

tokenfile = "~/.slacktoken"
token = open(os.path.expanduser(tokenfile), 'r').read().strip('\n')

logging.basicConfig(level=logging.WARN)
log = logging.getLogger()

def is_error(r):
    if not r['ok']:
        log.critical('error from slack api:\n %s' % r)

def get_current_user():
    """
    Return user id of current user
    """
    r = requests.get('https://slack.com/api/auth.test',
            params={ 'token': token })
    rj = r.json()
    is_error(rj)

    return rj['user_id']

def lookup_user_name(user_id):
    """
    Look up a user name from user ID
    """
    if user_id == 'USLACKBOT':
        return "slackbot"

    r = requests.get('https://slack.com/api/users.list',
            params={ 'token': token })
    rj = r.json()
    is_error(rj)

    for user in rj['members']:
        if user['id'] == user_id:
            return user['name']
    else:
        return "unknown"

def get_websocket_url():
    """
    retrieve a fresh websocket url from slack api
    """
    r = requests.get('https://slack.com/api/rtm.start',
                  params={ 'token': token })
    rj = r.json()
    is_error(rj)

    return rj['url']

def do_notify(user_name,msg):
    notifier = notify2.init('slack notify')
    if len(msg) >= 80:
        msg = msg[0:80] + "..."

    n = notify2.Notification("Slack Notify",
                             "<b>" + user_name + "</b>:\n" + msg,
                             "notification-message-im")
    n.show()

    log.info('notification performed')

def msg_recieved(ws,msg):
    msg = json.loads(msg)
    log.debug(msg)
    if msg['type'] == 'message':
        if msg['user'] != current_user:
            do_notify(lookup_user_name(msg['user']),msg['text'])

def on_error(ws, error):
    log.critical('websocket error:\n %s' % error)

def on_close(ws):
    raise Exception('websocket closed!')

def main():
    ws = websocket.WebSocketApp(get_websocket_url(),
                                on_message = msg_recieved,
                                on_error = on_error,
                                on_close = on_close)
    ws.run_forever()

if __name__ == '__main__':
    current_user = get_current_user()
    main()
