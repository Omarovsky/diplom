from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import decode_token
from app import crud
from jose import JWTError
import json

router = APIRouter()

connections: dict[int, list[WebSocket]] = {}

async def get_user_id_from_token(token: str) -> int:
    try:
        payload = decode_token(token)
        return int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        return None

@router.websocket("/ws/{channel_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    channel_id: int,
    db: AsyncSession = Depends(get_db)
):

    await websocket.accept()

    token = websocket.query_params.get("token")
    user_id = await get_user_id_from_token(token)

    if not user_id:
        await websocket.send_text("Invalid token")
        await websocket.close()
        return

    if channel_id not in connections:
        connections[channel_id] = []
    connections[channel_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = await crud.create_message(
                db=db,
                message={"content": data, "channel_id": channel_id},
                user_id=user_id
            )
            out = {
                "id": message.id,
                "user_id": message.user_id,
                "content": message.content,
                "timestamp": str(message.timestamp)
            }
            for client in connections[channel_id]:
                await client.send_text(json.dumps(out))

    except WebSocketDisconnect:
        connections[channel_id].remove(websocket)
