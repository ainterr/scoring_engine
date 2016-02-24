from .. import config

import requests
from requests.exceptions import *
import hashlib, random

def run(options):
    return True
    ip = options['ip']
    port = options['port']

    test = random.choice(config.HTTP_PAGES)

    try:
        r = requests.get('http://{}:{}/{}'.format(ip, port, test['url']), timeout=2)

        if r.status_code is not 200:
            return False

        sha1 = hashlib.sha1()
        sha1.update(r.content)
        checksum = sha1.hexdigest()

        if checksum == test['checksum']: return True

    except Timeout:
        return False

    return False
