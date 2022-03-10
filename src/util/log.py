import sys

def logerr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def logstd(*args, **kwargs):
    print(*args, file=sys.stdout, **kwargs)