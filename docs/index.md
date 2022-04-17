# Lazy Delegate - Python Solar Node Monitoring with Discord Notification Facility

Lazy Delegate is a monitoring script for running periodic health checks on Solar Network nodes and reporting via Discord. Following facilities are monitored:

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
- Relay node sync status and lag
- Forger node missed blocks
- Forger node rank
- Voters

<br>

# Sample message snapshots
**Periodic Heartbeat** ![Periodic Heartbeat](img/notif-sample-01.png?raw=true)

**Voter & rank notifications** ![Voter & rank notifications](img/notif-sample-02.png?raw=true)

**Alert for a single issue** ![Alert for a single issue](img/notif-sample-04.png?raw=true)

**Alert raise and cease** ![Alert raise and cease](img/notif-sample-03.png?raw=true)

**Heartbeat with issues, which cleared afterwards** ![Heartbeat with issues, which cleared afterwards](img/notif-sample-05.png?raw=true)
