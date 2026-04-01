from fastapi import FastAPI, Cookie, Form, Response, HTTPException
from fastapi.responses import FileResponse
from uuid import uuid4
from itsdangerous import TimestampSigner
import time

app = FastAPI()

SECRET_KEY = "secret-key-for-a-signature"  # я понимаю, что его нужно вынести в .env, но сейчас это не столь принципиально
signer = TimestampSigner(SECRET_KEY)

users_db = {
    "user123": {"id": str(uuid4()), "password": "password123", "name": "John Doe", "email": "john@example.com"},
    "admin": {"id": str(uuid4()), "password": "admin123", "name": "Admin User", "email": "admin@example.com"}
}


def verify_credentials(username: str, password: str) -> bool:
    if username not in users_db:
        return False
    return users_db[username]["password"] == password


def create_token(user_id: str) -> str:
    timestamp = int(time.time())
    message = f"{user_id}.{timestamp}"
    token = signer.sign(message).decode('utf-8')
    return token

def set_cookie_token(response: Response, token: str):
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,
        max_age=300
    )
def verify_token(token: str):
    try:
        message = signer.unsign(token).decode('utf-8')
        parts = message.split('.')
        user_id = parts[0]
        timestamp = int(parts[1])
        return user_id, timestamp
    except Exception as e:
        print(f"Ошибка: {e}")
        return None, None


@app.get('/')
async def homepage():
    return {"message": "Перейдите по ссылке http://127.0.0.1:8001/login"}


@app.get('/login')
async def login_page():
    return FileResponse("auth.html")


@app.post('/login')
async def auth(
        response: Response,
        username: str = Form(...),
        password: str = Form(...)
):
    if not verify_credentials(username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    signed_value = create_token(users_db[username]["id"])
    set_cookie_token(response, signed_value)
    return {"message": "Authorized successfully!"}


@app.get('/profile')
async def get_user(response: Response,
                   session_token: str | None = Cookie(default=None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        user_id, timestamp = verify_token(session_token)
        if not user_id or not timestamp:
            raise HTTPException(status_code=401, detail="Wrong data")
        message = None
        elapsed = int(time.time()) - timestamp
        print(f"Elapsed time: {elapsed}")
        if elapsed > 300:
            raise HTTPException (status_code=401, detail="Session expired")
        if elapsed > 180:
            new_token = create_token(user_id)
            set_cookie_token(response, new_token)
            print(f"New time: {int(time.time()) - verify_token(new_token)[1]}")
        for username in users_db:
            if users_db[username]["id"] == user_id:
                message = {"user": users_db[username]["name"],
                           "email": users_db[username]["email"]}
        if not message:
            raise HTTPException(status_code=401, detail="The user does not exist")
        return message
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.post('/logout')
async def logout(
        response: Response,
):
    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}
