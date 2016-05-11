# Searvice Check Config

#### Global
DOMAIN = 'TEAM'

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
    { 'type':'A', 'query':'team.local', 'expected':'216.239.32.10' },
]

### FTP
FTP_FILES = [
    { 'path':'/testfile.txt', 'checksum':'12345ABCDEF' },
]

### SMB
SMB_FILES = [
    { 'sharename':'ftproot', 'path':'/index.html', 'checksum':'83e503650ffd301b55538ea896afbcedea0c79c2' },
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
            { 'name':'ftp', 'ip':'172.16.66.152', 'port':21 },
            { 'name':'mssql', 'ip':'172.16.66.152', 'port':3308 },
            { 'name':'mysql', 'ip':'172.16.66.152', 'port':3308 },
            { 'name':'https', 'ip':'172.16.66.152', 'port':443 },
            { 'name':'smb', 'ip':'172.16.66.134', 'port':139 },
        ], 
        'credentials': [
            { 'username':'joe', 'password':'toor', 'services':['http', 'ssh', 'dns', 'imap', 'pop', 'smtp', 'ftp', 'mssql', 'mysql', 'https'] },
            { 'username':'nic', 'password':'toor', 'services':['http', 'ssh', 'dns', 'imap', 'pop', 'smtp'] },
            { 'username':'Administrator', 'password':'P@ssword1', 'services':['ldap', 'smb'] },
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
