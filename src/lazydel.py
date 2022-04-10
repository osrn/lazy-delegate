# -*- coding: utf-8 -*-
"""Solar Delegate Node monitoring script for
   running periodic health checks and
   reporting via Discord.
"""
from util.probe import Probe
from util.log import logerr, logdbg
from config.config import Config
from os import path
from discord_webhook import DiscordWebhook, DiscordEmbed
import psutil, pytz, requests, datetime, schedule, time, os, subprocess, json, signal, sys
#import traceback

__version__     = '0.6b'
__version_info__= tuple([ num for num in __version__.split('.')])
__author__      = "osrn"
__email__       = "osrn.network@gmail.com"

def getUtcTimeStr(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")

def get_round(height):
    mod = divmod(height, conf.delegates)
    return (mod[0] + int(mod[1] > 0))

def getHostStatus():
    lb = psutil.boot_time()
    lastboot.setValue(lb, lambda x: (os.path.exists(conf.need_reboot)), err='pending restart')

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
    try:
        pm2status=json.loads(subprocess.run([conf.pm2,'jlist'], capture_output=True, text=True).stdout)

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

        if (conf.chk_pool):
            ps=findJsonElement(pm2status, 'name', 'pool')
            if (ps is not None):
                tbwpool.setValue(ps['pm2_env']['status'], lambda x: (x != 'online'))
            else:
                tbwpool.setValue('n/a', lambda x: (x != 'online'))
                logerr('ERROR: pool process unknown to pm2')
    except Exception as e:
        logerr('ERROR: something seriously went wrong accessing pm2', e)
        #traceback.print_exc()
        relayproc.setValue('n/a', lambda x: (x != 'online'))
        if (conf.chk_forger): 
            forgerproc.setValue('n/a', lambda x: (x != 'online'))
        if (conf.chk_tbw):
            tbwcore.setValue('n/a', lambda x: (x != 'online'))
            tbwpay.setValue('n/a', lambda x: (x != 'online'))
        if (conf.chk_pool):
            tbwpool.setValue('n/a', lambda x: (x != 'online'))

    # TODO: last payment status


def codeblock(text):
    #~~__***`ttt`***__~~
    return '__**`'+str(text)+'`**__'

def getNetwork():
    global relayHeight, peerSwVersion, networkHeight

    # Fetch from Local API
    if (conf.chk_forger):
        try:
            r = requests.get(conf.localapi+'/blockchain')
            if r.status_code == 200:
                networkHeight = int(r.json()['data']['block']['height'])
            else:
                networkHeight = 'n/a'
                logerr('ERROR: Response code %s when accessing local API' % (r.status_code))
        except Exception as e:
            logerr("ERROR: Exception raised getting local /blockchain", e)
            #traceback.print_exc()

        try:
            r = requests.get(conf.localapi+'/delegates/'+conf.delegate)
            if r.status_code == 200:
                nodeRank.value = int(r.json()['data']['rank'])
                lastForged = int(r.json()['data']['blocks']['last']['height']) if (int(r.json()['data']['blocks']['produced']) > 0) else 0

                if (nodeRank.value == nodeRank.prevValue):
                    nodeRank.notif = ''
                else:
                    nodeRank.notif = 'Rank new:`{2}` old: `{1}` ∆: `{0}`'.format( \
                        ('inf' if (type(nodeRank.prevValue) == str) else (nodeRank.value - nodeRank.prevValue), \
                        nodeRank.prevValue, \
                        nodeRank.value))
            else:
                nodeRank.value = 'n/a'
                lastForged = 'n/a'
                logerr('ERROR: Response code %s when accessing local API' % (r.status_code))
        except Exception as e:
            logerr("ERROR: Exception raised getting local /delegates", e)
            #traceback.print_exc()
            nodeRank.value = 'n/a'
            lastForged = 'n/a'

        if (networkHeight == 'n/a' or lastForged == 'n/a'):
            missedBlocks.value = 'n/a'
        else:
            diff = get_round(networkHeight) - get_round(lastForged)
            missedBlocks.value = diff-1 if diff > 0 else diff

        try:
            r = requests.get(conf.localapi+'/delegates/'+conf.delegate+'/voters')
            if r.status_code == 200:
                voters = int(r.json()['meta']['totalCount'])
                pv = nodeVoters.prevValue 
                nodeVoters.setValue(voters, lambda x: True if (voters < (0 if type(pv) == str else pv)) else False)
                if ((type(pv) != str) and (voters > pv)):
                    nodeVoters.notif = 'You have %d new voter(s)' % (voters - pv)
                elif ((type(pv) != str) and (voters < pv)):
                    nodeVoters.notif = 'You have %d less voter(s)' % (pv - voters)
                else:
                    nodeVoters.notif = ''
            else:
                nodeVoters.setValue('n/a', lambda x: True)
                logerr('ERROR: Response code %s when accessing local API' % (r.status_code))
        except Exception as e:
            logerr("ERROR: Exception raised getting local /voters", e)
            #traceback.print_exc()
            nodeVoters.setValue('n/a', lambda x: True)

    try:
        r = requests.get(conf.localapi+'/node/syncing')
        if r.status_code == 200:
            relayInSync.setValue(not bool(r.json()['data']['syncing']), lambda x: (not(x)))
            relayLag.value = int(r.json()['data']['blocks'])
            relayHeight = r.json()['data']['height']
        else:
            relayInSync.setValue('n/a', lambda x: True)
            relayLag.value = 'n/a'
            logerr('ERROR: Response code %s when accessing local API' % (r.status_code))
    except Exception as e:
        logerr("ERROR: Exception raised getting local /syncing", e)
        #traceback.print_exc()
        relayInSync.setValue('n/a', lambda x: True)
        relayLag.value = 'n/a'

    # Fetch from Network API
    try:
        r = requests.get(conf.netapi+'/peers/'+conf.nodeip)
        if r.status_code == 200:
            nodeLatency.value = int(r.json()['data']['latency'])
            peerSwVersion = r.json()['data']['version']
        else:
            nodeLatency.value = 'n/a'
            peerSwVersion = 'n/a'
            logerr('ERROR: Response code %s when accessing network API' % (r.status_code))
    except Exception as e:
        logerr("ERROR: Exception raised in Network /peers", e)
        #traceback.print_exc()
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
            logerr('ERROR: Response code %s when accessing Last Release in Github' % (r.status_code))
            #lastReleaseDate = 'N/A'
    except Exception as e:
        logerr("ERROR: Exception raised getting Last Release", e)
        #traceback.print_exc()
        lastReleaseVers = '--'

    nodeSwVersion.setValue(peerSwVersion, lambda x: (x != lastReleaseVers))



'''
HEALTH CHECKS
'''
def health_checks():
    global lastProbeTime
    lastProbeTime = datetime.datetime.now()

    print('INFO: >>> starting health checks ...', datetime.datetime.now())
    getHostStatus()
    getProcesses()
    getNetwork()

    logdbg('name', 'value', 'threshold', 'isAlert', 'alertCount', 'lastAlert', sep='|')
    for p in probes:
        logdbg(p.name, p.value, p.th, p.isAlert, p.alertCount, p.lastAlertAt, sep='|')

    embed0 = DiscordEmbed()
    embed1 = DiscordEmbed()
    embed2 = DiscordEmbed()
    tEvents = 0

    p = lastboot
    if (p.isAlert and (p.lastAlertAt > lastProbeTime)):
        logdbg('raised', p.name)
        embed1.add_embed_field(name=p.name, value=codeblock(getUtcTimeStr(p.value))+' '+p.alertdesc)
        tEvents += 1
    if (not(p.isAlert) and (p.lastCeaseAt > lastProbeTime)):
        logdbg('ceased', p.name)
        embed2.add_embed_field(name=p.name, value=codeblock(getUtcTimeStr(p.value))+' '+p.alertdesc)
        tEvents += 1

    for p in probes[1:]:
        if (len(p.notif) > 0):
            logdbg('notification', p.name)
            embed0.add_embed_field(name=p.name, value=str(p.notif), inline=False)
            p.notif = ''
            tEvents += 1
        if (p.isAlert and (p.lastAlertAt > lastProbeTime)):
            logdbg('raised', p.name)
            embed1.add_embed_field(name=p.name, value=codeblock(p.value))
            tEvents += 1
        if (not(p.isAlert) and (p.lastCeaseAt > lastProbeTime)):
            logdbg('ceased', p.name)
            embed2.add_embed_field(name=p.name, value=codeblock(p.value))
            tEvents += 1

    if tEvents > 0:
        tShouldAlert = False
        embed_for_header = None
        embeds=[]
        if len(embed0.get_embed_fields()) > 0:
            embeds.append(embed0)
            embed_for_header=embed0
            embed_for_footer=embed0
        if len(embed1.get_embed_fields()) > 0:
            if embed_for_header is None: embed_for_header=embed1
            embed1.set_title("Issues open:")
            embed1.set_color(conf.discord_err_color)
            embeds.append(embed1)
            embed_for_footer=embed1
            tShouldAlert = True
        if len(embed2.get_embed_fields()) > 0:
            if embed_for_header is None: embed_for_header=embed2
            embed2.set_title("Issues cleared:")
            embed2.set_color(conf.discord_oki_color)
            embeds.append(embed2)
            embed_for_footer=embed2

        embed_for_header.set_author(name='DELEGATE '+conf.delegate.upper()+" NOTIFICATION")
        embed_for_footer.set_footer(text='Notifs by Lazy Delegate')
        embed_for_footer.set_timestamp()
        
        discordpush(embeds,tShouldAlert,alerts=len(embed1.get_embed_fields()))

    print('INFO: >>> health check run complete ...', datetime.datetime.now(), end='\n\n')




'''
HEARTBEAT FACILITY
'''
def heartbeat():
    global relayHeight

    print('INFO: >>> starting heartbeat ...', datetime.datetime.now())
    embeds = []
    totAlerts = 0
    # Embed 0: Insert node stats
    embed = DiscordEmbed()
    embed.set_author(name='DELEGATE '+conf.delegate.upper()+" HEARTBEAT")
    embed.set_title("__**Node stats**__")

    tAlert = 0

    for p in probes[1:5]:
        v = codeblock(p.value)+'%' if p.isAlert else str(p.value)+'%'
        embed.add_embed_field(name=p.name, value=v)
        tAlert += p.alertCount

    p = lastboot
    v = codeblock(getUtcTimeStr(p.value)+ ' *') if p.isAlert else str(getUtcTimeStr(p.value))
    embed.add_embed_field(name=p.name, value=v)
    tAlert += 1 if p.alertCount > 0 else 0

    ecolor=conf.discord_err_color if (tAlert > 0) else conf.discord_oki_color
    embed.set_color(ecolor)
    embeds.append(embed)

    totAlerts = tAlert

    # Embed 1: Insert network stats
    embed = DiscordEmbed()
    embed.set_title("__**Network stats**__")

    embed.add_embed_field(name=relayproc.name, value=str(relayproc.value))
    tAlert = 1 if relayproc.alertCount > 0 else 0

    for p in probes[5:9]:
        v = codeblock(p.value) if p.isAlert else str(p.value)
        embed.add_embed_field(name=p.name, value=v)
        tAlert += 1 if p.alertCount > 0 else 0

    if (conf.chk_forger):
        for p in (forgerproc, nodeRank, missedBlocks):
            v = codeblock(p.value) if p.isAlert else str(p.value)
            embed.add_embed_field(name=p.name, value=v)
            tAlert += 1 if p.alertCount > 0 else 0
        
        # no alert for voter change
        embed.add_embed_field(name=nodeVoters.name, value=str(nodeVoters.value))

    if (conf.chk_tbw):
        for p in (tbwcore, tbwpay):
            v = codeblock(p.value) if p.isAlert else str(p.value)
            embed.add_embed_field(name=p.name, value=v)
            tAlert += 1 if p.alertCount > 0 else 0

    if (conf.chk_pool):
        p = tbwpool
        v = codeblock(p.value) if p.isAlert else str(p.value)
        embed.add_embed_field(name=p.name, value=v)
        tAlert += 1 if p.alertCount > 0 else 0

    totAlerts += tAlert

    embed.set_footer(text='Stats by Lazy Delegate')
    embed.set_timestamp()
    ecolor=conf.discord_err_color if (tAlert > 0) else conf.discord_oki_color
    embed.set_color(ecolor)
    embeds.append(embed)

    if (totAlerts == 0): embeds[0].set_description('All systems check :ok:')

    logdbg('sending discord message ...')
    discordpush(embeds, (totAlerts > 0), totAlerts)
    print('INFO: >>> heartbeat run complete ...', datetime.datetime.now())


def servicemsg(state=0):
    embed = DiscordEmbed()
    if (state == 0):
        msg='INFO: >>> starting Lazy Delegate Monitor %s ... @ %s' % (__version__, str(datetime.datetime.now()))
    else:
        msg='INFO: <<< stopping Lazy Delegate Monitor %s ... @ %s' % (__version__, str(datetime.datetime.now()))
    embed.set_description(msg)
    embed.set_author(name='DELEGATE '+conf.delegate.upper()+" NOTIFICATION")
    embed.set_footer(text='Notifs by Lazy Delegate')
    embed.set_timestamp()
    print(msg)
    discordpush([embed])


def discordpush(embeds, alert=False, alerts=0):
    if conf.discordhook is not None:
        webhook = DiscordWebhook(url=conf.discordhook)
        if alert:
            webhook.set_content('Warning! you have {1} probe alerts <@{0}> :warning:'.format(conf.discorduser, alerts))

        for e in embeds:
            webhook.add_embed(e)

        try:
            response = webhook.execute(remove_embeds=True)
        except:
            logerr('ERROR: Discord webhook failed! Response is: ', response)


def sighandler(signum, frame):
    schedule.clear()
    servicemsg(1)
    time.sleep(5) # Allow for discord message and any cleanup
    sys.exit(0)

signal.signal(signal.SIGINT, sighandler)
signal.signal(signal.SIGTERM, sighandler)

'''
MAIN
'''
servicemsg(0)
conf = Config()
if (conf.error):
    logerr("FATAL ERROR: config file not found:")
    quit()

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
probes       += [relayInSync, relayLag, nodeLatency, nodeSwVersion]

relayproc     = Probe('Relay proc', init='--')
probes       += [relayproc]

if (conf.chk_forger):
    forgerproc  = Probe('Forger proc', init='--')
    nodeRank    = Probe('Rank', limit=conf.ranklimit)
    missedBlocks= Probe('Blockmiss', limit=0)
    nodeVoters  = Probe('Voters', init='--')
    probes     += [forgerproc, nodeRank, missedBlocks, nodeVoters]

if (conf.chk_tbw):
    tbwcore   = Probe('TBW Core', init='--')
    tbwpay    = Probe('TBW Pay', init='--')
    probes   += [tbwcore, tbwpay]

if (conf.chk_pool):
    tbwpool   = Probe('TBW Pool', init='--')
    probes   += [tbwpool]

relayHeight = 0
networkHeight = 0
peerSwVersion = ''

lastProbeTime = datetime.datetime.now()

job0 = schedule.every(conf.probe_cycle).seconds.do(health_checks)
time.sleep(5)
job1 = schedule.every(conf.heartbeat_cycle).seconds.do(heartbeat)

schedule.run_all() # cause run_pending() does not immediately start jobs but wait for the durations

while True:
    schedule.run_pending()
    time.sleep(1)
