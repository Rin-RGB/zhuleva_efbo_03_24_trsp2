from fastapi import FastAPI, Cookie, Form, Response, HTTPException
from fastapi.responses import FileResponse
from uuid import uuid4

app = FastAPI()

sessions = {}

VALID_CREDENTIALS = {
    "user": "user_password",
    "admin": "admin_password"
}

def verify_credentials(username: str, password: str) -> bool:
    if username not in VALID_CREDENTIALS:
        return False
    return VALID_CREDENTIALS[username] == password

@app.get('/')
async def homepage():
    return {"message": "Перейдите по ссылке, чтобы посмотреть все конечные точки",
            "link": "http://127.0.0.1:8000/docs"}
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
    session_token = str(uuid4())
    sessions[session_token] = username

    response.set_cookie(
        key = "session_token",
        value = session_token,
        httponly=True
    )
    return {"message": "Authorized successfully!"}
@app.get('/user')
async def get_user(session_token: str | None = Cookie(default=None)):
    if not session_token or session_token not in sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return {"username": sessions[session_token], "info": "Profile info"}
@app.post('/logout')
async def logout(
        response: Response,
        session_token: str | None = Cookie(None)
):
    if session_token and session_token in sessions:
        del sessions[session_token]

    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}