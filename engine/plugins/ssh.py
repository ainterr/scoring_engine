from .. import config
from paramiko import client

def run(options):
    ip = options['ip']
    port = options['port']
    username = options['username']
    password = options['password']

    try:
        cli = client.SSHClient()
        cli.load_system_host_keys()
        cli.set_missing_host_key_policy(client.AutoAddPolicy())
        cli.connect(ip, port, username, password)
        return True
    except:
        return False
