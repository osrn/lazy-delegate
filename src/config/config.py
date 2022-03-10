from dotenv import dotenv_values
from os import path

class Config():
    def __init__(self):
        configfile = path.join(path.abspath(path.dirname(__file__)), "config")
        config = dotenv_values(configfile)

        if (len(config) == 0): print("error, config file not found:", configfile)

        self.cpu_load_th = float(config.get('CPU_LOAD_THRESHOLD','50'))
        self.mem_use_th  = float(config.get('MEM_USE_THRESHOLD','80'))
        self.swap_use_th = float(config.get('SWAP_USE_THRESHOLD','90'))
        self.hdd_use_th  = float(config.get('HDD_USE_THRESHOLD','75'))
        self.need_reboot = config.get('REBOOT_FILE','/var/run/reboot-required')

        self.chk_forger  = bool(int(config.get('CHK_FORGER', 1)))
        self.chk_tbw     = bool(int(config.get('CHK_TBW', 1)))

        self.nodelocal   = config.get('NODE_LOCAL','127.0.0.1')
        self.nodeip      = config.get('NODE_IP','127.0.0.1')
        self.apiport     = int(config.get('API_PORT',6003))
        self.latency_th  = int(config.get('LATENCY_THRESHOLD','500'))
        self.blocklag_th = int(config.get('MAX_BLOCKS_BEHIND','5'))

        self.delegate    = config.get('DELEGATE_NAME','name')
        self.delegates   = int(config.get('DELEGATES','53'))
        self.localapi    = config.get('LOCAL_API','http://'+self.nodelocal+':'+str(self.apiport)+'/api')
        self.netapi      = config.get('NET_API', self.localapi)
        self.chaingithub = config.get('CHAIN_GITHUB', 'https://api.github.com/repos/Solar-network/core/releases')

        self.probe_cycle = int(config.get('PROBE_CYCLE','120'))
        self.heartbeat_cycle = int(config.get('HEARTBEAT_CYCLE','3600'))

        self.discordhook = config.get('DISCORD_HOOK', None)
        self.discord_err_color = config.get('DISCORD_ERR', 'FF0000')
        self.discord_oki_color = config.get('DISCORD_OK', '00FF00')
