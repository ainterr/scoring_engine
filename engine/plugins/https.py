from .. import config

import logging
logger=logging.getLogger(__name__)
import requests
from requests.exceptions import *
import hashlib, random

def run(options):
    ip = options['ip']
    port = options['port']

    test = random.choice(config.HTTPS_PAGES)
    try:
        expected = open('engine/http_pages/%s' % test['expected'], 'r')
    except:
        logger.debug('Could not open file engine/http_pages/%s' % test['expected'])

    tolerance = test['tolerance']

    try:
        r = requests.get('https://{}:{}/{}'.format(ip, port, test['url']), verify=False, timeout=2)

        if r.status_code is not 200:
            logger.debug(r.status_code)
            return False

        page = [line + '\n' for line in r.text.split('\n')]
        expected_page = expected.readlines()

        diff = difflib.unified_diff(page, expected_page)
        diff_lines = [line for line in diff][2:]
        headings = [line for line in diff_lines if line[0] == '@']
        diffs = [line for line in diff_lines if line[0] in ['+', '-']]
        
        num_diff = 0
        for heading in headings:
            locations = heading.split(' ')[1:-1]
            lengths = []
            for location in locations:
                if ',' in location:
                    lengths.append(int(location.split(',')[1]))
                else:
                    lengths.append(0)
            num_diff += abs(lengths[1] - lengths[0])
        num_diff += (len(diffs) - num_diff) / 2

        return num_diff / float(len(expected_page)) <= tolerance
    except Timeout:
        logger.debug("Timeout")
        return False
    except ConnectionError:
        return False
