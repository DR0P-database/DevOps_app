# config.py
import os

USER = 'app_admin'
PASSWORD = 'pswd'
DB_NAME = 'devops_app_database'

DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{USER}:{PASSWORD}@localhost/{DB_NAME}")