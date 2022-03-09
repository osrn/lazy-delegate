import psutil, pytz, requests, datetime, schedule, time, os, subprocess, json
from os import path
from util.probe import Probe
from discord_webhook import DiscordWebhook, DiscordEmbed
from config.config import Config

def getUtcTimeStr(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")

def get_round(height):
    mod = divmod(height, conf.delegates)
    return (mod[0] + int(mod[1] > 0))

def getHostStatus():
    #nodeLastBoot.value = datetime.datetime.fromtimestamp(psutil.boot_time(), tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    lb = psutil.boot_time()
    lastboot.setValue(lb, lambda x: (os.path.exists(conf.need_reboot)))
    
    cpuload.value = psutil.cpu_percent()
    memusage.value = psutil.virtual_memory().percent
    swapusage.value = psutil.swap_memory().percent
    diskusage.value = psutil.disk_usage('/').percent

    '''
    print("users logged in")
    for u in psutil.users(): ## number of users logged in
        print(u.name)
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
            relayproc.setValue('N/A', lambda x: (x != 'online'))

        ps=findJsonElement(pm2status, 'name', 'solar-forger')
        if (ps is not None):
            forgerproc.setValue(ps['pm2_env']['status'], lambda x: (x != 'online'))
        else:
            forgerproc.setValue('N/A', lambda x: (x != 'online'))

        ps=findJsonElement(pm2status, 'name', 'tbw')
        if (ps is not None):
            tbwcore.setValue(ps['pm2_env']['status'], lambda x: (x != 'online'))
        else:
            tbwcore.setValue('N/A', lambda x: (x != 'online'))

        ps=findJsonElement(pm2status, 'name', 'pay')
        if (ps is not None):
            tbwpay.setValue(ps['pm2_env']['status'], lambda x: (x != 'online'))
        else:
            tbwpay.setValue('N/A', lambda x: (x != 'online'))

        ps=findJsonElement(pm2status, 'name', 'pool')
        if (ps is not None):
            tbwpool.setValue(ps['pm2_env']['status'], lambda x: (x != 'online'))
        else:
            tbwpool.setValue('N/A', lambda x: (x != 'online'))

    except:
        print('something went wrong queryying pm2')

    # TODO: last payment status



def codeblock(text):
    return '`'+str(text)+'`'

def getNetwork():
    global relayHeight, peerSwVersion, networkHeight

    r = requests.get(conf.localapi+'/blockchain')
    if r.status_code == 200:
        networkHeight = int(r.json()['data']['block']['height'])
    else:
        print (r.status_code)

    r = requests.get(conf.localapi+'/delegates/'+conf.delegate)
    if r.status_code == 200:
        nodeRank.value = int(r.json()['data']['rank'])
        lastForged = int(r.json()['data']['blocks']['last']['height'])
    else:
        print (r.status_code)

    missedBlocks.value = get_round(networkHeight) - get_round(lastForged) -1

    r = requests.get(conf.localapi+'/delegates/'+conf.delegate+'/voters')
    if r.status_code == 200:
        voters = int(r.json()['meta']['totalCount'])
        nodeVoters.setValue(voters, lambda x: True if (voters < nodeVoters.prevValue) else False)
    else:
        print (r.status_code)

    r = requests.get(conf.localapi+'/node/syncing')
    if r.status_code == 200:
        relayInSync.setValue(not bool(r.json()['data']['syncing']), lambda x: (not(x)))
        relayLag.value = int(r.json()['data']['blocks'])
        relayHeight = r.json()['data']['height']
    else:
        print (r.status_code)

    r = requests.get(conf.netapi+'/peers/'+conf.nodeip)
    if r.status_code == 200:
        nodeLatency.value = int(r.json()['data']['latency'])
        peerSwVersion = r.json()['data']['version']
    else:
        print (r.status_code)

    r = requests.get(conf.chaingithub)
    if r.status_code == 200:
        lastReleaseVers = r.json()[0]['name']
        #lastReleaseDate = r.json()[0]['published_at']
    else:
        print (r.status_code)
        lastReleaseVers = 'N/A'
        #lastReleaseDate = 'N/A'

    nodeSwVersion.setValue(peerSwVersion, lambda x: (x != lastReleaseVers))


def health_checks():
    global lastProbeTime
    lastProbeTime = datetime.datetime.now()

    print('>>> starting health checks ...', datetime.datetime.now())
    getHostStatus()     
    getProcesses()
    getNetwork()

    print('name', 'value', 'threshold', 'isAlert', 'alertCount', 'lastAlert', sep='|')
    for p in probes:
        print(p.name, p.value, p.th, p.isAlert, p.alertCount, p.lastAlertAt, sep='|')

    #print(lastboot.name, getUtcTimeStr(lastboot.value))
    embed0 = DiscordEmbed()
    embed1 = DiscordEmbed()
    embed2 = DiscordEmbed()
    tEvents = 0
    for p in probes:
        if (p.isAlert and (p.lastAlertAt > lastProbeTime)):
            print('raised ', p.name)
            embed1.add_embed_field(name=p.name, value=codeblock(p.value))
            tEvents += 1
        if (not(p.isAlert) and (p.lastCeaseAt > lastProbeTime)):
            print('ceased ', p.name)
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

    print('>>> health check run complete ...', datetime.datetime.now(), end='\n\n')


def heartbeat():
    global relayHeight

    print('>>> starting heartbeat ...', datetime.datetime.now())
    embeds = []

    embed = DiscordEmbed()
    embed.set_author(name='DELEGATE '+conf.delegate.upper()+" HEARTBEAT")
    embed.set_title("__**Node Stats**__")
    embed.set_description('Last boot: ' + getUtcTimeStr(lastboot.value))
    embed.add_embed_field(name=cpuload.name, value=codeblock(cpuload.value)+'%')
    embed.add_embed_field(name=memusage.name, value=codeblock(memusage.value)+'%')
    embed.add_embed_field(name=swapusage.name, value=codeblock(swapusage.value)+'%')
    embed.add_embed_field(name=diskusage.name, value=codeblock(diskusage.value)+'%')
    tAlert = 0
    for p in probes[0:5]:
        tAlert += p.alertCount
    ecolor=conf.discord_err_color if (tAlert > 0) else conf.discord_oki_color
    embed.set_color(ecolor)
    #embed.set_image(url='your image url') # set image
    #embed.set_thumbnail(url='your thumbnail url') # set thumbnail
    embeds.append(embed)

    embed = DiscordEmbed()
    embed.set_title("__**Processes**__")
    tAlert = 0
    for p in probes[5:10]:
        embed.add_embed_field(name=p.name, value=codeblock(p.value))
        tAlert += p.alertCount
    ecolor=conf.discord_err_color if (tAlert > 0) else conf.discord_oki_color
    embed.set_color(ecolor)
    embeds.append(embed)

    embed = DiscordEmbed()
    embed.set_title("__**Network Stats**__")
    tAlert = 0
    for p in probes[10:]:
        embed.add_embed_field(name=p.name, value=codeblock(p.value))
        tAlert += p.alertCount
    embed.set_footer(text='Stats by sol messenger')
    embed.set_timestamp()
    ecolor=conf.discord_err_color if (tAlert > 0) else conf.discord_oki_color
    embed.set_color(ecolor)
    embeds.append(embed)

    discordpush(embeds)
    print('>>> heartbeat run complete ...', datetime.datetime.now())


def discordpush(embeds):
    if conf.discordhook is not None:
        webhook = DiscordWebhook(url=conf.discordhook)
        for e in embeds:
            webhook.add_embed(e)
        try:
            response = webhook.execute(remove_embeds=True)
        except:
            print('snap!', response)


conf = Config()

lastboot      = Probe('Last Boot')
cpuload       = Probe('CPU Load', limit=conf.cpu_load_th)
memusage      = Probe('Mem Used', limit=conf.mem_use_th)
swapusage     = Probe('Swap Used', limit=conf.swap_use_th)
diskusage     = Probe('HDD Used', limit=conf.hdd_use_th)

relayproc     = Probe('Relay proc', init='N/A')
forgerproc    = Probe('Forger proc', init='N/A')
tbwcore       = Probe('TBW Core', init='N/A')
tbwpay        = Probe('TBW Pay', init='N/A')
tbwpool       = Probe('TBW Pool', init='N/A')

relayInSync   = Probe('Synced', init=True)
relayLag      = Probe('Lagging', limit=conf.blocklag_th)
nodeLatency   = Probe('Latency', limit=conf.latency_th)
nodeSwVersion = Probe('SW Version', init='')
nodeRank      = Probe('Rank', limit=conf.delegates)
nodeVoters    = Probe('Voters')
missedBlocks  = Probe('Blockmiss', limit=0)

probes =  [lastboot, cpuload, memusage, swapusage, diskusage]
probes += [relayproc, forgerproc, tbwcore, tbwpay, tbwpool]
probes += [relayInSync, relayLag, nodeLatency, nodeSwVersion, nodeRank, nodeVoters, missedBlocks]

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
