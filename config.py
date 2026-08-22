from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "abcd")
DB_URL = os.getenv("DB_URL")

