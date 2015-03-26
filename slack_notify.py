import os,notify2
from slacksocket import SlackSocket

tokenfile = "~/.slacktoken"

def do_notify(user_name,msg):
    notifier = notify2.init('slack notify')
    if len(msg) >= 80:
        msg = msg[0:80] + "..."

    n = notify2.Notification("Slack Notify",
                             "<b>" + user_name + "</b>:\n" + msg,
                             "notification-message-im")
    n.show()
    print('notification performed')

def main():
    token = open(os.path.expanduser(tokenfile), 'r').read().strip('\n')
    s = SlackSocket(token)
    current_user = s.user
    while True:
        event = s.get_event(event_filter=['message'])
        print('got event')
        if event.event['user'] != current_user:
            do_notify(event.event['user'],event.event['text'])

if __name__ == '__main__':
    main()
