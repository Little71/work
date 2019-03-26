schema = 'mysql+pymysql'
username='game'
password='aohe123456'
host='192.168.0.202'
port='3306'
database = 'test_person'
ENCODING = "utf8"

SQLURL = f'{schema}://{username}:{password}@{host}:{port}/{database}'
# conn = "mysql+pymysql://game:aohe123456@192.168.0.202:3306/test_person"

SQLDEBUG =True

AUTH_SECRET ='www.xxx.com'
AUTH_EXPIRE = 8*3600
WSIP = '127.0.0.1'
WSPORT = 9999