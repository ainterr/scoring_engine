from .. import config
from smb.SMBConnection import SMBConnection
import smb, random, hashlib, tempfile

def run(options):
    ip = options['ip']
    port = options['port']
    username = options['username']
    password = options['password']

    test = random.choice(config.SMB_FILES)

    conn = SMBConnection(username, password, '', 'Web-app', config.DOMAINb)
    conn.connect(ip, port)
    t = tempfile.TemporaryFile()
    conn.retrieveFile(test['sharename'], test['path'], t)

    sha1 = hashlib.sha1()
    t.seek(0)
    sha1.update(t.read())
    t.close()
    checksum = sha1.hexdigest()

    if checksum == test['checksum']:
        return True

    return False

