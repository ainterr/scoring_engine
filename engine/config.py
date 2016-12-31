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

# Services Config
SERVICES = [
    { 'name':'http',  'subnet_host':'152', 'port':80,   'plugin':'http' },
    { 'name':'ssh',   'subnet_host':'152', 'port':22,   'plugin':'ssh' },
    { 'name':'dns',   'subnet_host':'152', 'port':53,   'plugin':'dns' },
    { 'name':'imap',  'subnet_host':'152', 'port':143,  'plugin':'imap' },
    { 'name':'pop',   'subnet_host':'152', 'port':110,  'plugin':'pop' },
    { 'name':'smtp',  'subnet_host':'152', 'port':25,   'plugin':'smtp' },
    { 'name':'ldap',  'subnet_host':'134', 'port':389,  'plugin':'ldap' },
    { 'name':'ftp',   'subnet_host':'152', 'port':21,   'plugin':'ftp' },
    { 'name':'mssql', 'subnet_host':'152', 'port':3308, 'plugin':'mssql' },
    { 'name':'mysql', 'subnet_host':'152', 'port':3309, 'plugin':'mysql' },
    { 'name':'https', 'subnet_host':'152', 'port':443,  'plugin':'https' },
    { 'name':'smb',   'subnet_host':'134', 'port':139,  'plugin':'smb' },
] 

# Default Credentials Config
DEFAULT_CREDS = [
    { 'username':'joe', 'password':'toor', 'services':['http', 'ssh', 'dns', 'imap', 'pop', 'smtp', 'ftp', 'mssql', 'mysql', 'https'] },
    { 'username':'nic', 'password':'toor', 'services':['http', 'ssh', 'dns', 'imap', 'pop', 'smtp'] },
    { 'username':'Administrator', 'password':'P@ssword1', 'services':['ldap', 'smb'] },
]

# Team Config
TEAMS = [
    { 'name': 'Team 1', 
      'subnet': '192.168.1.0',
      'netmask': '255.255.255.0'
    },
    { 'name': 'Team 2', 
      'subnet': '192.168.2.0',
      'netmask': '255.255.255.0'
    },
]
