from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Query, HTTPException, Depends
from app.database import engine, Base
from app.routers import auth, users, chat, chat_ws, direct, ws_direct, webrtc
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import DialogOut
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(chat.router)
app.include_router(chat_ws.router)
app.include_router(direct.router)
app.include_router(ws_direct.router)
app.include_router(webrtc.router)

