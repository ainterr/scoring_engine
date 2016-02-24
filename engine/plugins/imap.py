from .. import config

from imaplib import IMAP4
import socket

socket.setdefaulttimeout(5)

def run(options):

    ip = options['ip']
    port = options['port']
    username = options['username']
    password = options['password']
    
    try:
        imap = IMAP4(ip, port)
        imap.starttls()
    except:
        return False

    tries = 0
    while tries < 5:
        try:
            print(username, password)
            imap.login(username, password)
            imap.logout()
            return True
        except:
            print("Login Failed")
            imap.logout()
            imap = IMAP4(ip, port)
            imap.starttls()
            tries += 1
            
    return False
