# -*- coding: utf-8 -*-
"""Solar Delegate Node monitoring script for
   running periodic health checks and
   reporting via Discord.
"""
from util.probe import Probe
from util.log import logerr
from config.config import Config
from os import path
from discord_webhook import DiscordWebhook, DiscordEmbed
import psutil, pytz, requests, datetime, schedule, time, os, subprocess, json

__version__     = '0.1'
__version_info__= tuple([ int(num) for num in __version__.split('.')])
__author__      = "osrn"
__email__       = "osrn.network@gmail.com"

def getUtcTimeStr(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")

def get_round(height):
    mod = divmod(height, conf.delegates)
    return (mod[0] + int(mod[1] > 0))

def getHostStatus():
    lb = psutil.boot_time()
    lastboot.setValue(lb, lambda x: (os.path.exists(conf.need_reboot)))

    cpuload.value = psutil.cpu_percent()
    memusage.value = psutil.virtual_memory().percent
    swapusage.value = psutil.swap_memory().percent
    diskusage.value = psutil.disk_usage('/').percent
    '''
    for u in psutil.users(): 
    '''

def findJsonElement(json_obj, key, value):
    element = None
    for dict in json_obj:
        if dict[key] == value:
            element = dict
            break
    return element

def getProcesses():
    #['pm2_env']['version']
    try:
        pm2status=json.loads(subprocess.run(['pm2','jlist'], capture_output=True, text=True).stdout)

        ps=findJsonElement(pm2status, 'name', 'solar-relay')
        if (ps is not None):
            relayproc.setValue(ps['pm2_env']['status'], lambda x: (x != 'online'))
        else:
            relayproc.setValue('n/a', lambda x: (x != 'online'))
            logerr('ERROR: solar-relay process unknown to pm2')

        if (conf.chk_forger):
            ps=findJsonElement(pm2status, 'name', 'solar-forger')
            if (ps is not None):
                forgerproc.setValue(ps['pm2_env']['status'], lambda x: (x != 'online'))
            else:
                forgerproc.setValue('n/a', lambda x: (x != 'online'))
                logerr('ERROR: solar-forger process unknown to pm2')

        if (conf.chk_tbw):
            ps=findJsonElement(pm2status, 'name', 'tbw')
            if (ps is not None):
                tbwcore.setValue(ps['pm2_env']['status'], lambda x: (x != 'online'))
            else:
                tbwcore.setValue('n/a', lambda x: (x != 'online'))
                logerr('ERROR: tbw process unknown to pm2')

            ps=findJsonElement(pm2status, 'name', 'pay')
            if (ps is not None):
                tbwpay.setValue(ps['pm2_env']['status'], lambda x: (x != 'online'))
            else:
                tbwpay.setValue('n/a', lambda x: (x != 'online'))
                logerr('ERROR: pay process unknown to pm2')

            ps=findJsonElement(pm2status, 'name', 'pool')
            if (ps is not None):
                tbwpool.setValue(ps['pm2_env']['status'], lambda x: (x != 'online'))
            else:
                tbwpool.setValue('n/a', lambda x: (x != 'online'))
                logerr('ERROR: pool process unknown to pm2')
    except:
        relayproc.setValue('n/a', lambda x: (x != 'online'))
        if (conf.chk_forger): 
            forgerproc.setValue('n/a', lambda x: (x != 'online'))
        if (conf.chk_tbw):
            tbwcore.setValue('n/a', lambda x: (x != 'online'))
            tbwpay.setValue('n/a', lambda x: (x != 'online'))
            tbwpool.setValue('n/a', lambda x: (x != 'online'))
        logerr('ERROR: something seriously went wrong accessing pm2')

    # TODO: last payment status


def codeblock(text):
    return '`'+str(text)+'`'

def getNetwork():
    global relayHeight, peerSwVersion, networkHeight

    # Fetch from Local API
    try:
        r = requests.get(conf.localapi+'/blockchain')
        if r.status_code == 200:
            networkHeight = int(r.json()['data']['block']['height'])
        else:
            networkHeight = 'n/a'
            logerr('ERROR: Response code %d when accessing local API' % (r.status_code))

        r = requests.get(conf.localapi+'/delegates/'+conf.delegate)
        if r.status_code == 200:
            nodeRank.value = int(r.json()['data']['rank'])
            lastForged = int(r.json()['data']['blocks']['last']['height'])
        else:
            nodeRank.value = 'n/a'
            lastForged = 'n/a'
            logerr('ERROR: Response code %d when accessing local API' % (r.status_code))

        if (networkHeight == 'n/a' or lastForged == 'n/a'):
            missedBlocks.value = 'n/a'
        else:
            diff = get_round(networkHeight) - get_round(lastForged)
            missedBlocks.value = diff-1 if diff > 0 else diff

        r = requests.get(conf.localapi+'/delegates/'+conf.delegate+'/voters')
        if r.status_code == 200:
            voters = int(r.json()['meta']['totalCount'])
            nodeVoters.setValue(voters, lambda x: True if (voters < nodeVoters.prevValue) else False)
        else:
            nodeVoters.setValue('n/a', lambda x: True)
            logerr('ERROR: Response code %d when accessing local API' % (r.status_code))

        r = requests.get(conf.localapi+'/node/syncing')
        if r.status_code == 200:
            relayInSync.setValue(not bool(r.json()['data']['syncing']), lambda x: (not(x)))
            relayLag.value = int(r.json()['data']['blocks'])
            relayHeight = r.json()['data']['height']
        else:
            relayInSync.setValue('n/a', lambda x: True)
            relayLag.value = 'n/a'
            logerr('ERROR: Response code %d when accessing local API' % (r.status_code))
    except:
        nodeRank.value = 'n/a'
        missedBlocks.value = 'n/a'
        nodeVoters.setValue('n/a', lambda x: True)
        relayInSync.setValue('n/a', lambda x: True)
        relayLag.value = 'n/a'
        logerr('ERROR: Cannot reach local API')

    # Fetch from Network API
    try:
        r = requests.get(conf.netapi+'/peers/'+conf.nodeip)
        if r.status_code == 200:
            nodeLatency.value = int(r.json()['data']['latency'])
            peerSwVersion = r.json()['data']['version']
        else:
            nodeLatency.value = 'n/a'
            peerSwVersion = 'n/a'
            logerr('ERROR: Response code %d when accessing network API' % (r.status_code))
    except:
        nodeLatency.value = 'n/a'
        peerSwVersion = 'n/a'

    # Fetch from Github
    try:
        r = requests.get(conf.chaingithub)
        if r.status_code == 200:
            lastReleaseVers = r.json()[0]['name']
            #lastReleaseDate = r.json()[0]['published_at']
        else:
            lastReleaseVers = '--'
            logerr('ERROR: Response code %d when accessing Last Release in Github' % (r.status_code))
            #lastReleaseDate = 'N/A'
    except:
        lastReleaseVers = '--'
        logerr('ERROR: Cannot reach Github')

    nodeSwVersion.setValue(peerSwVersion, lambda x: (x != lastReleaseVers))

def health_checks():
    global lastProbeTime
    lastProbeTime = datetime.datetime.now()

    print('INFO: >>> starting health checks ...', datetime.datetime.now())
    getHostStatus()
    getProcesses()
    getNetwork()

    print('DEBUG:', 'name', 'value', 'threshold', 'isAlert', 'alertCount', 'lastAlert', sep='|')
    for p in probes:
        print('DEBUG:', p.name, p.value, p.th, p.isAlert, p.alertCount, p.lastAlertAt, sep='|')

    embed0 = DiscordEmbed()
    embed1 = DiscordEmbed()
    embed2 = DiscordEmbed()
    tEvents = 0

    p = lastboot
    if (p.isAlert and (p.lastAlertAt > lastProbeTime)):
        print('DEBUG: raised', p.name)
        embed1.add_embed_field(name=p.name, value=codeblock(getUtcTimeStr(p.value))+' Restart pending!')
        tEvents += 1
    if (not(p.isAlert) and (p.lastCeaseAt > lastProbeTime)):
        print('DEBUG: ceased', p.name)
        embed2.add_embed_field(name=p.name, value='Restart pending')
        tEvents += 1

    for p in probes[1:]:
        if (p.isAlert and (p.lastAlertAt > lastProbeTime)):
            print('DEBUG: raised', p.name)
            embed1.add_embed_field(name=p.name, value=codeblock(p.value))
            tEvents += 1
        if (not(p.isAlert) and (p.lastCeaseAt > lastProbeTime)):
            print('DEBUG: ceased', p.name)
            embed2.add_embed_field(name=p.name, value=codeblock(p.value))
            tEvents += 1

    if tEvents > 0:
        embed0.set_author(name='DELEGATE '+conf.delegate.upper()+" Alert Status changed")
        embeds=[embed0]
        if len(embed1.get_embed_fields()) > 0:
            embed1.set_title("Issues open:")
            embed1.set_color(conf.discord_err_color)
            embeds.append(embed1)
        if len(embed2.get_embed_fields()) > 0:
            embed2.set_title("Issues cleared:")
            embed2.set_color(conf.discord_oki_color)
            embeds.append(embed2)
        discordpush(embeds)

    print('INFO: >>> health check run complete ...', datetime.datetime.now(), end='\n\n')


def heartbeat():
    global relayHeight

    print('INFO: >>> starting heartbeat ...', datetime.datetime.now())
    embeds = []

    embed = DiscordEmbed()
    embed.set_author(name='DELEGATE '+conf.delegate.upper()+" HEARTBEAT")
    embed.set_title("__**Node stats**__")
    restartNotif = ' Restart pending!' if lastboot.isAlert else ''
    embed.set_description('Last boot: ' + getUtcTimeStr(lastboot.value)+restartNotif)
    tAlert = lastboot.alertCount
    for p in probes[1:5]:
        embed.add_embed_field(name=p.name, value=str(p.value)+'%')
        tAlert += p.alertCount
    ecolor=conf.discord_err_color if (tAlert > 0) else conf.discord_oki_color
    embed.set_color(ecolor)
    embeds.append(embed)

    embed = DiscordEmbed()
    embed.set_title("__**Network stats**__")
    
    embed.add_embed_field(name=relayproc.name, value=str(relayproc.value))
    tAlert = relayproc.alertCount
    if (conf.chk_forger):
        embed.add_embed_field(name=forgerproc.name, value=str(forgerproc.value))
        tAlert += forgerproc.alertCount

    if (conf.chk_tbw):
        for p in (tbwcore, tbwpay, tbwpool):
            embed.add_embed_field(name=p.name, value=str(p.value))
            tAlert += p.alertCount

    for p in probes[5:12]:
        embed.add_embed_field(name=p.name, value=str(p.value))
        tAlert += p.alertCount

    embed.set_footer(text='Stats by Lazy Delegate')
    embed.set_timestamp()
    ecolor=conf.discord_err_color if (tAlert > 0) else conf.discord_oki_color
    embed.set_color(ecolor)
    embeds.append(embed)

    print('DEBUG: sending discord message ...')
    discordpush(embeds)
    print('INFO: >>> heartbeat run complete ...', datetime.datetime.now())


def discordpush(embeds):
    if conf.discordhook is not None:
        webhook = DiscordWebhook(url=conf.discordhook)
        for e in embeds:
            webhook.add_embed(e)

        try:
            response = webhook.execute(remove_embeds=True)
        except:
            logerr('ERROR: Discord webhook failed! Response is: ', response)


conf = Config()

lastboot      = Probe('Last Boot')
cpuload       = Probe('CPU Load', limit=conf.cpu_load_th)
memusage      = Probe('Mem Used', limit=conf.mem_use_th)
swapusage     = Probe('Swap Used', limit=conf.swap_use_th)
diskusage     = Probe('HDD Used', limit=conf.hdd_use_th)
probes        = [lastboot, cpuload, memusage, swapusage, diskusage]

relayInSync   = Probe('Synced', init=True)
relayLag      = Probe('Lagging', limit=conf.blocklag_th)
nodeLatency   = Probe('Latency', limit=conf.latency_th)
nodeSwVersion = Probe('SW Version', init='')
nodeRank      = Probe('Rank', limit=conf.delegates)
nodeVoters    = Probe('Voters')
missedBlocks  = Probe('Blockmiss', limit=0)
probes       += [relayInSync, relayLag, nodeLatency, nodeSwVersion, nodeRank, nodeVoters, missedBlocks]

relayproc     = Probe('Relay proc', init='--')
probes       += [relayproc]

if (conf.chk_forger):
    forgerproc= Probe('Forger proc', init='--')
    probes   += [forgerproc]

if (conf.chk_tbw):
    tbwcore   = Probe('TBW Core', init='--')
    tbwpay    = Probe('TBW Pay', init='--')
    tbwpool   = Probe('TBW Pool', init='--')
    probes   += [tbwcore, tbwpay, tbwpool]

relayHeight = 0
networkHeight = 0
peerSwVersion = ''

lastProbeTime = datetime.datetime.now()

print('INFO: >>> starting Lazy Delegate Monitor ...', datetime.datetime.now())

job0 = schedule.every(conf.probe_cycle).seconds.do(health_checks)
time.sleep(5)
job1 = schedule.every(conf.heartbeat_cycle).seconds.do(heartbeat)

schedule.run_all() # cause run_pending() does not immediately start jobs but wait for the durations

while True:
    schedule.run_pending()
    time.sleep(1)
