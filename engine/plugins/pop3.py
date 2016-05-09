from  .. import config
import poplib

def run(options):
    ip = options['ip']
    port = options['port']
    username = options['username']
    password = options['password']

    try:
        pop = poplib.POP3(ip, port, 2)
        pop.stls()
        pop.user(username)
        pop.pass_(password)
        pop.quit()
        return True
    except:
        return False
