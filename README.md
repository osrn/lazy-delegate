# Lazy Delegate - Python Solar Node Monitoring with Discord Notification Facility

Solar Delegate Node monitoring script for running periodic health checks and reporting via Discord. Following facilities are monitored:

__**Host status**__
- last boot time and pending restart
- cpu load
- memory usage
- swap usage
- disk usage

__**Node processes**__
- SW Version
- Solar Relay
- Solar Forger
- [True Block Weight](https://github.com/osrn/core2_tbw) _forked from [original](https://github.com/galperins4/core2_tbw) by Solar Delegate Goose @galperins4_

__**Network status**__
- Relay sync status and lag
- Forger missed blocks
- Forger rank
- Delegate voters

<br>

Discord embed side colors indicate alert status and the probes causing alert are displayed as __**``bold underlined code style``**__.

<br>

> _Project and most of the probes were inspired by Solar Delegate @mtaylan 's [Solar Node Monitoring scripts](https://github.com/mtaylan/SOLAR_NODE_Monitor_Discord)_

<br>

## Requires
- Python3
- Python virtual environment
- Process Manager 2 (pm2)
- Webhook url associated with a Discord server & channel

<br>

## Update instructions for 0.55b
```bash
pm2 stop lazy-delegate
cd ~/lazy-delegate/ && git pull
. .venv/bin/activate
pip3 install -r requirements.txt && deactivate
```

add the following in `~/lazy-delegate/src/config/config`
```text
DEBUG=0
DISCORD_USER='<@your_userid_not_bots>'
```

start and check logs
```bash
pm2 start lazy-delegate && pm2 logs lazy-delegate
```

## Installation
Replace SUDO_USER with a username having sudo rights (i.e. having sudo group) and run command below
```bash
cd && bash <(curl -s https://raw.githubusercontent.com/osrn/lazy-delegate/main/install.sh) SUDO_USER
```

<br>

**move on to the configuration**
> Discord channel webhook creation is common knowledge hence not mentioned here.

<br>

## Configuration
### clone the sample config provided

`cd ~/lazy-delegate && cp src/config/config.sample src/config/config`

<br>

### config options

**PM2='path-to-pm2-executable'**

Path to pm2 executable

<br>

**CHK_FORGER=1**

Enable(1)/disable(0) monitoring PM2 Forger process. Relay process is always checked.

<br>

**CHK_TBW=1**

Enable(1)/disable(0) monitoring PM2 TBW-pool and TBW-pay processes

<br>

**CHK_POOL=1**

Enable(1)/disable(0) monitoring PM2 TBW-pool process

<br>

**NODE_IP=xx.xx.xx.xx**

IP address of the forger node to be monitored - as registered in PEER LIST

<br>

**DELEGATE_NAME='xxxx'**

Registered delegate name for the forger node

<br>

**RANKLIMIT=52**

Alert will be produced when rank > RANKLIMIT

<br>

**LOCAL_API='http://127.0.0.1:6003/api'**

Default is local node to query API. However, this can be set to any relay node with public API

<br>

**NET_API='https://sxp.mainnet.sh/api'**

Best to point to the public API for the network. Yet, it is ok to set to any relay node with public API, or even localhost. Remember to change, when Mainnet.

<br>

**PRERELEASE=0**

Set to 0 for Mainnet and 1 if Testnet

<br>

**PROBE_CYCLE = 120**

Probe execution (health check) interval in seconds. Notice that a value < 60 may suffer from github API rate limiting with a 403 Forbidden response.

<br>

**DEBUG = 0**

Set to 1 for verbose logging

<br>

**HEARTBEAT_CYCLE = 3600**

Interval in seconds for heartbeat messages sent to discord.

<br>

**DISCORD_HOOK='https://discord.com/api/webhooks/xxxxx/yyyyyyyyyy'**

Discord hook :)

<br>

**DISCORD_USER='your_userid_not_bots'**

Userid of the discord user to notify with a @mention for alert situation. User will not be mentioned if no alert or alert ceased.

<br>

## Run
start the app and monitor logs
```bash
cd ~/lazy-delegate && pm2 start package.json && pm2 logs lazy-delegate
```

<br>

to start the app at boot with pm2
```bash
cd && pm2 save
```

to start pm2 at boot;

Option 1) Have sudo privileges? `pm2 startup` and follow the instructions

Option 2) No sudo privileges like solar? `(crontab -l; echo "@reboot /bin/bash -lc \"source /home/solar/.solarrc; pm2 resurrect\"") | sort -u - | crontab -`

<br>

### Maintenance
to stop|start|restart the process on-the-fly
```bash
pm2 stop|start|restart lazy-delegate
```

<br>

Whenever the config file changes, app needs to be restarted
```bash
pm2 restart lazy-delegate
```

<br>

to remove the process for whatever reason:
```bash
pm2 stop lazy-delegate
pm2 delete lazy-delegate
# optionally, remove logs
rm ~/.pm2/logs/lazy-delegate*
```

<br>

## Inside the mind
Node is probed periodically for health checks and any issues raised or cleared during the rest period are reported to Discord instantly. Issues are reported only once, the first time. 

Probe class is responsible for keeping track of the values and governing the alarm raising and clearing logic.

A heartbeat status report is sent in regular intervals. Any missing report should indicate a problem with the host, node or lazy-delegate app itself.

## Change Log
**v0.62b**

Solar Core 3.3.0-next.3 API compatibility
- Adaptation for Solar Core 3.3.0-next.3 API change for use of block id in delegate attribute
<br>

**v0.61b**

fix: testnet release version
- added config option `PRERELEASE` to specify which core version to check against; release(0) and prelease(1) branches
<br>

**v0.6b**

script start/stop handler
- added handler for SIGINT and SIGTERM for cleanup and service status notification
- added rank alert limit. To set, add `RANKLIMIT=xx` in the config. Default value is `52`.
<br>

**v0.56b**

notification and alert improvements
- notification when rank changes
- notification when voter count changes
- voter count change is not an alert reason in heartbeat anymore
- notification now includes a footer with timestamp
<br>

**v0.55b**

better notification for alert conditions
- mention user in alert condition message to receive notification
- better visibility for probes causing alert condition in heartbeat
- turn on/off verbose logging via config. colored output for debug messages
<br>

**v0.54b**
- fix: error in last block produced check before epoch
<br>

**v0.53b**
- fix: rank, voters and missed blocks should not be reported if CHK_FORGER=0
- minor doc changes
<br>

**v0.52b**
- PM2 executable path is now read from the config (solar core 3.2.0-next2 does not export alias to user's shell)
- TBW-pool process probe now can be enabled/disabled independent of TBW-tbw & TBW-pay probes
- fixed forger process alert condition test
<br>

**v0.51b**
install.sh
- non-sudo user friendly installation for required apt packages
- rewrites CPATH to prevent python package compilation errors (CPATH is restored back afterwards) 
- Added missing python3-pip APT package to the installation
- Stop jobs before complete reinstall

documentation
- how to start pm2 at boot
<br>

**v0.5b**

- Values for probes with an active alert are now shown as codeblock in heartbeat status message
- An info message will be sent to the discord channel if delegate gained any voters during the rest period


## TODO
- Add probe for Lazy Delegate version
