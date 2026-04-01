from fastapi import FastAPI, Cookie, Form, Response, HTTPException
from fastapi.responses import FileResponse
from uuid import uuid4
from itsdangerous import TimestampSigner
app = FastAPI()

SECRET_KEY = "secret-key-for-a-signature" #я понимаю, что его нужно вынести в .env, но сейчас это не столь принципиально
signer = TimestampSigner(SECRET_KEY)

users_db = {
    "user123": {"id": str(uuid4()), "password": "password123", "name": "John Doe", "email": "john@example.com"},
    "admin": {"id": str(uuid4()), "password": "admin123", "name": "Admin User", "email": "admin@example.com"}
}

def verify_credentials(username: str, password: str) -> bool:
    if username not in users_db:
        return False
    return users_db[username]["password"] == password
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
        return {"error": "Invalid credentials"}
    user_id = users_db[username]["id"]
    signed_value = signer.sign(user_id).decode('utf-8')
    response.set_cookie(
        key="session_token",
        value=signed_value,
        httponly=True,
        max_age=3600
    )
    return {"message": "Authorized successfully!"}
@app.get('/profile')
async def get_user(session_token: str | None = Cookie(default=None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = signer.unsign(session_token, max_age=3600).decode('utf-8')
    for username in users_db:
        if users_db[username]["id"] == user_id:
            return {"user": users_db[username]["name"], "email": users_db[username]["email"]}
    raise HTTPException(status_code=401, detail="No user with such id")

@app.post('/logout')
async def logout(
        response: Response,
):
    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}