# Searvice Check Config

#### Global
DOMAIN = 'WARPED'

### HTTP
HTTP_PAGES = [
    { 'url':'', 'expected':'index.html', 'tolerance': 0.05 },
]

### HTTPS
HTTPS_PAGES = [
    { 'url':'', 'expected':'index.html', 'tolerance': 0.05 },
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
    'joe@team.vnet',
    'nic@team.vnet',
]

### LDAP
LDAP_QUERIES = [
    { 'dn': '%s@team.vnet', 'base': 'cn=users,dc=team,dc=vnet', 'filter':'(&(objectClass=*)(cn=Administrator))', 'attributes':['sAMAccountName'], 'expected':{'sAMAccountName': ['Administrator']} },
]

# Team Config
TEAMS = [
    { 'name': 'Team 1', 
        'services': [
            { 'name':'http', 'ip':'172.16.66.152', 'port':80 },
            { 'name':'ssh', 'ip':'172.16.66.152', 'port':22 },
            { 'name':'dns', 'ip':'172.16.66.152', 'port':53 },
            { 'name':'imap', 'ip':'172.16.66.152', 'port':143 },
            { 'name':'pop', 'ip':'172.16.66.152', 'port':110 },
            { 'name':'smtp', 'ip':'172.16.66.152', 'port':25 },
            { 'name':'ldap', 'ip':'172.16.66.134', 'port':389 },
        ], 
        'credentials': [
            { 'username':'joe', 'password':'test', 'services':['http', 'ssh', 'dns', 'imap', 'pop', 'smtp'] },
            { 'username':'nic', 'password':'toor', 'services':['http', 'ssh', 'dns', 'imap', 'pop', 'smtp'] },
            { 'username':'Administrator', 'password':'P@ssword1', 'services':['ldap'] },
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
