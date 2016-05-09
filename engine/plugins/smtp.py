from .. import config

from smtplib import SMTP
import random, socket

socket.setdefaulttimeout(2)

message = 'Hello from the Scoring Engine!'

def run(options):
    ip = options['ip']
    port = options['port']
    
    from_addr = random.choice(config.SMTP_ADDRESSES)
    to_addr = random.choice(config.SMTP_ADDRESSES)

    try:
        smtp = SMTP(ip, port)
        smtp.sendmail(from_addr, to_addr, 'Subject: {}'.format(message))
        smtp.quit()
        return True
    except:
        return False
