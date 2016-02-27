from .. import config
import pymssql, socket, random

def run(options):
    socket.setdefaulttimeout(2)

    ip = options['ip']
    username = options['username']
    password = options['password']

    test = random.choice(config.MSSQL_QUERIES)

    try:
        conn = pymssql.connect(ip, '{}\\{}'.format(config.DOMAIN, username), password, test['db'])
        cursor = conn.cursor()
        cursor.execute(test['query'])
        response = ' '.join([str(row[0]) for row in cursor.fetchall()])
        if response == test['response']:
            return True
        return False
    except:
        return False
