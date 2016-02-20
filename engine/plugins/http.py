import requests
from requests.exceptions import *

def run(options):
    ip = options['ip']
    port = options['port']

    try:
        r = requests.get('http://{}:{}'.format(ip, port), timeout=2)

        if r.status_code is 200:
            return True

        return False
    except Timeout:
        return False
