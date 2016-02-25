# Searvice Check Config

### HTTP
HTTP_PAGES = [
    { 'url':'', 'checksum':'12345ABCDEF' },
]

### DNS
DNS_QUERIES = [
    { 'type':'A', 'query':'ns.google.com', 'expected':'216.239.32.10' },
]

### FTP
FTP_FILES = [
    { 'path':'/testfile.txt', 'checksum':'12345ABCDEF' },
]

### SMB
SMB_FILES = [
    { 'sharename':'ftp', 'path':'/testfile.txt', 'checksum':'e05fcb614ab36fdee72ee1f2754ed85e2bd0e8d0' },
]

SMB_CONFIG = { 'domain':'TEAM' }

### MSSQL
MSSQL_QUERIES = [
    { 'db': 'employee_data', 'query': 'SELECT SSN FROM dbo.hr_info WHERE LastName LIKE \'Erikson\'', 'response': '122751924' },
]

MSSQL_USERS = [
    { 'username':'WARPED\\Administrator', 'password':'P@ssword1' },
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
