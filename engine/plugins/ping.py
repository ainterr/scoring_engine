from .. import config
import os

def run(options):
    ip = options['ip']

    for tries in range(5):
        res = os.system('ping -c5 -W2 -q {} > /dev/null'.format(ip))
        if res == 0:
            return True
    return False
