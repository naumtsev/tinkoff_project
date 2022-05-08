import os

DB_URL = os.environ.get('DB_URL', 'sqlite:///db.db')
SECRET_KEY = os.environ.get('SECRET_KEY', 'TINKOFF KEY')
CODEFORCES_API_URL = 'https://codeforces.com/api/{}'
UPDATE_TIME = 60
