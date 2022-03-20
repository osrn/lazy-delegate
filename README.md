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
- [True Block Weight](https://github.com/galperins4/core2_tbw) _by Solar Delegate Goose @galperins4_

__**Network status**__
- Relay sync status and lag
- Forger missed blocks
- Forger rank
- Delegate voters

<br>

> _Project and most of the probe points were inspired by Solar Delegate @mtaylan 's [Solar Node Monitoring scripts](https://github.com/mtaylan/SOLAR_NODE_Monitor_Discord)_

<br>

## Requires
- Python3
- Python virtual environment
- Process Manager 2 (pm2)
- Webhook url associated with a Discord server & channel

<br>

## Installation
**install the package via**
Replace SUDO_USER with a username with sudo elevation (i.e. having sudo group)
```bash
cd && bash <(curl -s https://raw.githubusercontent.com/osrn/lazy-delegate/main/install.sh) SUDO_USER
```

<br>

**next, make sure pm2 is installed**

`npm install pm2@latest -g` or `yarn global add pm2`

<br>

**move on to the configuration**
> Discord server, channel and webhook creation is accepted as common knowledge hence not mentioned here.

<br>

## Configuration
### clone the sample config provided

`cd ~/lazy-delegate && cp src/config/config.example src/config/config`

<br>

### revise src/config/config options

**NODE_IP=xx.xx.xx.xx**

IP address of the forger node to be monitored - as registered in PEER LIST

<br>

**DELEGATE_NAME='xxxx'**

Registered delegate name for the forger node

<br>

**LOCAL_API='http://127.0.0.1:6003/api'**

Default is local node to query API. However, this can be set to any relay node with public API

<br>

**NET_API='https://sxp.testnet.sh/api'**

Best to point to the public API for the network. Yet, it is ok to set to any relay node with public API, or even localhost. Remember to change, when Mainnet.

<br>

**DISCORD_HOOK='https://discord.com/api/webhooks/xxxxx/yyyyyyyyyy'**

Discord hook :)

<br>

**PROBE_CYCLE = 120**

Probe execution (health check) interval in seconds. Notice that a value < 60 may suffer from github API rate limiting with a 403 Forbidden response.

<br>

**HEARTBEAT_CYCLE = 3600**

Interval in seconds for heartbeat messages sent to discord.

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


