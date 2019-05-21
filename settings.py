import pathlib  
from envparse import env

env.read_envfile()

BASE_PATH = pathlib.Path(__file__).parent

MYSQL_HOST = env('MYSQL_HOST', cast=str, default='localhost')
MYSQL_PORT = env('MYSQL_PORT', cast=int, default=3306)
MYSQL_USER = env('MYSQL_USER', cast=str)
MYSQL_PASSWORD = env('MYSQL_PASSWORD', cast=str)
MYSQL_DATABASE = env('MYSQL_DATABASE', cast=str)

DEBUG_LEVEL = env('DEBUG_LEVEL', cast=str, default='DEBUG')

TREOLAN_WDSL = env('TREOLAN_WDSL', cast=str, default='https://api.treolan.ru/webservices/treolan.wsdl') 
TREOLAN_LOGIN = env('TREOLAN_LOGIN', cast=str) 
TREOLAN_PASSWORD = env('TREOLAN_PASSWORD', cast=str) 

DEBUG_LEVEL = env('DEBUG_LEVEL', cast=str, default='DEBUG')
