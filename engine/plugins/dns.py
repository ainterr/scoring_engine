from __future__ import absolute_import

from .. import config

from dns import resolver
from dns.exception import *
import random

def run(options):
    ip = options['ip']
    port = options['port']

    test = random.choice(config.DNS_QUERIES)

    res = resolver.Resolver()
    res.nameservers = [ip]
    res.lifetime = 2.0
    res.timeout = 2.0

    try:
        response = res.query(test['query'], test['type'])[0].to_text()
    except Timeout:
        return False

    if response == test['expected']:
        return True

    return False
