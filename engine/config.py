# Searvice Check Config

#### Global
DOMAIN = 'WARPED'

### HTTP
HTTP_PAGES = [
    { 'url':'', 'expected':'index.html', 'tolerance': 0.05 },
]

### HTTPS
HTTPS_PAGES = [
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

### MSSQL
MSSQL_QUERIES = [
    { 'db': 'employee_data', 'query': 'SELECT SSN FROM dbo.hr_info WHERE LastName LIKE \'Erikson\'', 'response': '122751924' },
]

### MYSQL
MYSQL_QUERIES = [
    { 'db': 'mysql', 'query': 'SELECT password FROM user WHERE user=\'root\' AND host=\'localhost\'', 'response': '*9CFBBC772F3F6C106020035386DA5BBBF1249A11' }
]

### SMTP
SMTP_ADDRESSES = [
    'test@someemail.com',
]

# Team Config
TEAMS = [
    { 'name': 'Team 1', 
        'services': [
            { 'name':'http', 'ip':'172.16.66.152', 'port':80 },
            { 'name':'ssh', 'ip':'172.16.66.152', 'port':22 },
        ], 
        'credentials': [
            { 'username':'joe', 'password':'Sup3rSecret!', 'services':['http, ssh'] }
        ]
    },
    { 'name': 'Team 2', 
        'services': [
            { 'name':'http', 'ip':'10.0.0.100', 'port':80 },
        ], 
        'credentials': [
            { 'username':'joe', 'password':'Sup3rSecret!', 'services':['http'] }
        ]
    },
]
