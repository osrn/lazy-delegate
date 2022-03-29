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

> _Project and most of the probes were inspired by Solar Delegate @mtaylan 's [Solar Node Monitoring scripts](https://github.com/mtaylan/SOLAR_NODE_Monitor_Discord)_

Discord messages are colored in parallel with alert status and the probes causing alert are displayed in bold and code style with colored background.

<br>

## Requires
- Python3
- Python virtual environment
- Process Manager 2 (pm2)
- Webhook url associated with a Discord server & channel

<br>

## Installation
Replace SUDO_USER with a username having sudo rights (i.e. having sudo group) and run command below
```bash
cd && bash <(curl -s https://raw.githubusercontent.com/osrn/lazy-delegate/develop/install.sh) SUDO_USER
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

**LOCAL_API='http://127.0.0.1:6003/api'**

Default is local node to query API. However, this can be set to any relay node with public API

<br>

**NET_API='https://sxp.mainnet.sh/api'**

Best to point to the public API for the network. Yet, it is ok to set to any relay node with public API, or even localhost. Remember to change, when Mainnet.

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

**DISCORD_USER='<@userid>'**

Discord user to notify with @mention for alert messages

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
