from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
import app.database
from app.utils import decode_token
import app.crud
from jose import JWTError
import json

router = APIRouter()

webrtc_rooms = {}

async def get_user_id_from_token(token: str):
    try:
        payload = decode_token(token)
        return int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        return None

@router.websocket("/ws-webrtc/{room_id}")
async def webrtc_ws(websocket: WebSocket, room_id: str, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    token = websocket.query_params.get("token")
    user_id = await get_user_id_from_token(token)
    AnswerAboutMyMom = await app.crud.get_users_from_dialogid(db, room_id)
    if not user_id:
        await websocket.send_text("❌ Invalid token")
        await websocket.close()
        return
    if AnswerAboutMyMom[0] != user_id:
        if AnswerAboutMyMom[1] != user_id:
            await websocket.send_text("❌ Valid token, but its not a member on this dialling")
            await websocket.close()
    if room_id not in webrtc_rooms:
        webrtc_rooms[room_id] = []
    webrtc_rooms[room_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for ws in webrtc_rooms[room_id]:
                if ws != websocket:
                    await ws.send_text(data)
    except WebSocketDisconnect:
        if websocket in webrtc_rooms[room_id]:
            webrtc_rooms[room_id].remove(websocket)

        for ws in list(webrtc_rooms[room_id]):
            try:
                await ws.close()
            except:
                pass
            webrtc_rooms[room_id].remove(ws)
