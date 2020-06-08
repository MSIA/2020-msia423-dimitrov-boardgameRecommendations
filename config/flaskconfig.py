import os

DEBUG = False
LOGGING_CONFIG = "config/logging/local.conf"
PORT = 5000
APP_NAME = "Boardgame_Recommendations_App"
SQLALCHEMY_TRACK_MODIFICATIONS = False
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = True  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 10

# Connection string
DB_HOST = os.environ.get('MYSQL_HOST')
DB_PORT = os.environ.get('MYSQL_PORT')
DB_USER = os.environ.get('MYSQL_USER')
DB_PW = os.environ.get('MYSQL_PASSWORD')
DATABASE = os.environ.get('MYSQL_DATABASE')
DB_DIALECT = 'mysql+pymysql'
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
if SQLALCHEMY_DATABASE_URI: # I deliberately changed this from what it was before. If the user doesn't specify an engine string as an env variable it evaluates to '' instead of None. This new check captures both scenarios because '' evaluates to Falsy, just like None.
    pass
elif DB_HOST is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/boardgames.db'
else:
    SQLALCHEMY_DATABASE_URI = f'{DB_DIALECT}://{DB_USER}:{DB_PW}@{DB_HOST}:{DB_PORT}/{DATABASE}'
