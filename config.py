from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "abcd")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DB_URL = os.getenv("DB_URL")
MAX_ITERATIONS = 5
SYSTEM_PROMPT = "You are a basic agent with tool calling capabilities. Handle the queries of the user by using appropriate and required tools."


