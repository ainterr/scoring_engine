#!/bin/bash
sudo apt-get update
sudo apt-get install -y freetds-dev libsasl2-dev libldap2-dev python-dev \
	libssl-dev libffi-dev python3 python3-pip

sudo pip3 install django django-bootstrap3 dnspython3 paramiko pysmb==1.1.16 \
	pymysql pymssql pyldap requests
