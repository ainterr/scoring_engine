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
    except:
        return False

    tries = 0
    while tries < 5:
        try:
            pop.user(username)
            pop.pass_(password)
            pop.quit()
            return True
        except:
            pop.quit()
            pop = poplib.POP3(ip, port, 2)
            pop.stls()
            tries += 1

    return False
