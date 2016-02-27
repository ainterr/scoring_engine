from .. import config
import pymysql, random

def run(options):
    ip = options['ip']
    port = options['port']
    username = options['username']
    password = options['password']

    test = random.choice(config.MYSQL_QUERIES)

    conn = pymysql.connect(host=ip, port=port, user=username, password=password, database=test['db'])
    cursor = conn.cursor()
    cursor.execute(test['query'])

    response = ' '.join([res[0] for res in cursor.fetchall()])
    conn.close()
    if response == test['response']:
        return True
    return False
