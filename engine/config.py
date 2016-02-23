# Searvice Check Config

### HTTP
HTTP_PAGES = [
    { 'url':'/', 'checksum':'12345ABCDEF' },
]

### DNS
DNS_QUERIES = [
    { 'type':'A', 'query':'ns.google.com', 'expected':'216.239.32.10' },
]

### FTP
FTP_FILES = [
    { 'path':'/testfile.txt', 'checksum':'12345ABCDEF' },
]

### SMTP
SMTP_ADDRESSES = [
    'test@someemail.com',
]

# Team Config
TEAMS = [
    { 'name': 'NUCCDC', 
        'services': [
            { 'name':'http', 'ip':'10.0.0.100', 'port':80 },
        ], 
        'credentials': [
            { 'username':'joe', 'password':'Sup3rSecret!' }
        ]
    },
]
