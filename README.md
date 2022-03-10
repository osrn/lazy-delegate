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


> _Project and most of the probe points were inspired by Solar Delegate @mtaylan 's [Solar Node Monitoring scripts](https://github.com/mtaylan/SOLAR_NODE_Monitor_Discord)_


## Requires
- Python3
- Python virtual environment
- Process Manager 2 (pm2)
- Webhook url associated with a Discord server & channel

## Installation
**install the package via**
```bash
cd && bash <(curl -s https://raw.githubusercontent.com/osrn/lazy-delegate/main/install.sh)
```

**next, make sure pm2 is installed**

`npm install pm2@latest -g` or `yarn global add pm2`

**move on to the configuration**
> Discord server, channel and webhook creation is accepted as common knowledge hence not mentioned here.


## Configuration
**clone the sample config provided and modify:**

`cp src/config/config.example src/config/config`

**Then edit:**

`src/config/config`

## Run
start the app and monitor logs
```bash
cd ~/lazy-delegate && pm2 start apps.json && pm2 logs lazy-delegate
```

to start the app at boot with pm2
```bash
cd && pm2 save
```
*(to start pm2 at boot) do; `pm2 startup` and follow the instructions*

### Maintenance
to start-stop-restart the process on-the-fly:
```bash
pm2 stop|start|restart lazy-delegate
```

Whenever the config file changes, app needs to be restarted
```bash
pm2 restart lazy-delegate
```

to remove the process for whatever reason:
```bash
pm2 stop lazy-delegate
pm2 delete lazy-delegate
# optionally, remove logs
rm ~/.pm2/logs/lazy-delegate*
```

## Inside the mind
Node probed periodically for health checks and any issues raised or cleared after the last check are reported to Discord instantly.

A heartbeat status report, also is issued in (longer) intervals.

All monitoring points are stored in the Probe class which also governs the alarm raising and clearing logic.
