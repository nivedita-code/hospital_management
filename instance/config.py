# Mongo Settings
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SESSION_TYPE = 'filesystem'

# OS Settings
SERVER_TYPE = os.environ.get('SERVER_TYPE', 'LOCAL')  # LOCAL, TEST, PROD
MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME')
SECRET_KEY = os.environ['SECRET_KEY']
VERSION = os.environ['VERSION']


if SERVER_TYPE == 'LOCAL':
    MONGO_ATLAS_CONNECTION_STRING = "mongodb://localhost:27017/"
else:
    raise Exception("Bad Configuration")

"------------------------------------Collections-----------------------------------"
MONGO_COL_ORG: str = "organisation"
MONGO_COL_USER: str = "user"
