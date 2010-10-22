import os

PROJECT_DIR = os.path.dirname(__file__)


ADMINS = (
    ('Adelein Rodriguez', 'adeleinr@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'webme'             # Or path to database file if using sqlite3.
DATABASE_USER = 'root'              # Not used with sqlite3.
DATABASE_PASSWORD = 'plumas00'      # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

FACEBOOK_API_KEY = '163084660386318'
FACEBOOK_SECRET_KEY = '4ce322f9bd2f37a8dc5d18ab7d19a4f9'



# These are the hostnames as returned by platform.node().
# If you aren't sure what to put, leave them blank and the error message should tell you which hostname Python sees.
DEVELOPMENT_HOST = 'localhost'
PRODUCTION_HOST = ''