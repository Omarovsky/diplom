from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

router = APIRouter()

# Пример структуры: room_id -> list of WebSocket
rooms: Dict[str, List[WebSocket]] = {}

@router.websocket("/ws/webrtc/{room_id}")
async def webrtc_signaling(websocket: WebSocket, room_id: str):
    await websocket.accept()

    if room_id not in rooms:
        rooms[room_id] = []
    rooms[room_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            # Рассылаем всем, кроме отправителя
            for conn in rooms[room_id]:
                if conn != websocket:
                    await conn.send_text(data)

    except WebSocketDisconnect:
        rooms[room_id].remove(websocket)
