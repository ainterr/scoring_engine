from .. import config

import logging
logger=logging.getLogger(__name__)
import ldap
import random

def run(options):
    ip = options['ip']
    port = options['port']
    username = options['username']
    password = options['password']

    test = random.choice(config.LDAP_QUERIES)
    dn = test['dn'] % username
    base = test['base']
    scope = ldap.SCOPE_SUBTREE
    filt = test['filter']
    attrs = test['attributes']
    expected = test['expected']
    
    try:
        uri = 'ldap://%s:%d' % (ip, port)
        con = ldap.initialize(uri)
        con.simple_bind_s(dn, password)
        output = con.search_s(base, scope, filt, attrs)
        output = output[0][1] # Only check first value
        for key in output.keys():
            for i in range(len(output[key])):
                output[key][i] = output[key][i].decode()
        return output == expected
    except Exception as e:
        logger.debug(e)
        return False
