from fastapi import FastAPI
from routes.accounts import router as Account_Router
from routes.auth import router as Auth_Router

app = FastAPI()

app.include_router(Account_Router, prefix="/accounts")
app.include_router(Auth_Router, prefix="/auth")

