from .. import config

import requests
from requests.exceptions import *
import hashlib, random

def run(options):
    ip = options['ip']
    port = options['port']

    test = random.choice(config.HTTPS_PAGES)

    try:
        r = requests.get('https://{}:{}/{}'.format(ip, port, test['url']), verify=False, timeout=2)

        if r.status_code is not 200:
            print(r.status_code)
            return False

        sha1 = hashlib.sha1()
        sha1.update(r.content)
        checksum = sha1.hexdigest()

        if checksum == test['checksum']:
            return True
    except Timeout:
        print("Timeout")
        return False

    print("Bad checksum")
    return False
