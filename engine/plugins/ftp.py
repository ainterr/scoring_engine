from .. import config

import ftplib
import random, hashlib, tempfile

def run(options):
    ip = options['ip']
    port = options['port']
    username = options['username']
    password = options['password']

    test = random.choice(config.FTP_FILES)

    ftp = ftplib.FTP()
    t = tempfile.TemporaryFile()

    try:
        ftp.connect(ip, port, timeout=2)
        ftp.login(user=username, password=password)
        ftp.retrbinary('RETR {}'.format(test['path']), t.write)
        ftp.quit()
    except ftplib.all_errors as e:
        return False

    sha1 = hashlib.sha1()
    t.seek(0)
    sha1.update(t.read())
    t.close()

    checksum = sha1.hexdigest()

    if checksum == test['checksum']:
        return True

    return False
