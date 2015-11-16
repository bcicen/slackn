# slackn

A better Slack notfication interface for nagios, conveying batch notifications without spamming a channel

# Install

```bash
git clone https://github.com/bcicen/slackn.git
cd slackn/
pip install -r requirements.txt
python setup.py install
```

Slackn also requires that a Redis instance be accessible. On Ubuntu, simply run:
```bash
sudo apt-get install redis-server
sudo service redis-server start
```

# Configuration

## Configuring Nagios

Create a contact definition in /etc/nagios/conf.d/slack_nagios.conf (or wherever your icinga/nagios config resides) with the below content:

```
define contact {
      contact_name                             slack
      alias                                    Slack
      service_notification_period              24x7
      host_notification_period                 24x7
      service_notification_options             u,r,c
      host_notification_options                d,r
      service_notification_commands            notify-service-by-slack
      host_notification_commands               notify-host-by-slack
}

define command {
      command_name     notify-service-by-slack
      command_line     /usr/bin/slackn-notify service "$HOSTNAME$" "$SERVICEDESC$" "$SERVICESTATE$" "$SERVICEOUTPUT$" "$NOTIFICATIONTYPE$"
}

define command {
      command_name     notify-host-by-slack
      command_line     /usr/bin/slackn-notify host "$HOSTNAME$" "$HOSTSTATE$" "$HOSTOUTPUT$" "$NOTIFICATIONTYPE$"
}
```

Edit your Nagios contacts.cfg file and add the new slack contact to your contact group(s) like so:
```
define contactgroup {
  contactgroup_name admins
  alias             Nagios Administrators
  members           root,slack
}
```

## Configuring Notifications

Add the following cronjob to /etc/cron.d/slackn:
```
*/5 * * * * /usr/bin/slackn-process --slack-channel my-channel --slack-token your-slack-token-here
```
This will aggregate host and service notifications every five minutes, creating a post in a given Slack channel
