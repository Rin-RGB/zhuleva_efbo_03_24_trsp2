from models import UserCreate
from fastapi import FastAPI

app = FastAPI()
fake_db = []


@app.get('/')
async def main_page():
    return {"message": "Выполните post запрос в swagger по ссылке  http://localhost:8000/docs"}
@app.get('/users')
async def read_users():
    return fake_db

@app.post('/create_user')
async def create_user(user: UserCreate):
    fake_db.append(user)
    return user
