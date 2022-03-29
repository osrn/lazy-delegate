import sys
from colorama import Fore, Style
from config.config import Config

def logerr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def logstd(*args, **kwargs):
    print(*args, file=sys.stdout, **kwargs)

def logdbg(*args, **kwargs):
    if conf.debug:
        print(Fore.BLUE, "DEBUG: ", *args, Style.RESET_ALL, file=sys.stdout, **kwargs)

conf = Config()
