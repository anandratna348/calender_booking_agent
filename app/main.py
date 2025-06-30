from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from app.agent import run_agent
from app.calender import force_login, handle_callback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

import os

@app.get("/is_logged_in")
def is_logged_in():
    return {"logged_in": os.path.exists("app/token.pickle")}


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body["message"]
    response = run_agent(message)
    return {"response": response}

@app.get("/authorize")
async def authorize():
    login_url = force_login()
    return RedirectResponse(login_url)

@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    success = handle_callback(request)
    if success:
        return HTMLResponse("<h2>Google Calendar Login Successful!</h2><p>You can now return to the chat.</p>")
    return HTMLResponse("<h2>Login Failed</h2>", status_code=400)

@app.get("/logout")
def logout():
    token_path = "app/token.pickle"
    if os.path.exists(token_path):
        os.remove(token_path)
    return {"success": True, "message": "User logged out"}
