from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List
from app.database import get_db
from app import crud, schemas
from app.utils import decode_token
from jose import JWTError
import json

router = APIRouter()


direct_connections: Dict[int, List[WebSocket]] = {}

async def get_user_id_from_token(token: str) -> int | None:
    try:
        payload = decode_token(token)
        return int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        return None

@router.websocket("/ws-direct/{dialog_id}")
async def direct_message_ws(websocket: WebSocket, dialog_id: int, db: AsyncSession = Depends(get_db)):
    await websocket.accept()

    token = websocket.query_params.get("token")
    user_id = await get_user_id_from_token(token)

    if not user_id:
        await websocket.send_text("❌ Invalid token")
        await websocket.close()
        return

    if dialog_id not in direct_connections:
        direct_connections[dialog_id] = []
    direct_connections[dialog_id].append(websocket)

    allmessages_raw = await crud.get_dialog_messages(db, dialog_id)
    allmessages = {"allmessages": jsonable_encoder(allmessages_raw)}
    if(len(allmessages["allmessages"]) > 100): 
        for indexOfMSGS in range(len(allmessages["allmessages"])-100, len(allmessages["allmessages"])):
            userInfoGL = await crud.get_user(db=db, user_id=allmessages["allmessages"][indexOfMSGS]["sender_id"])
            allmessages["allmessages"][indexOfMSGS]["full_name"] = userInfoGL.full_name
    else:
        for indexOfMSGS in range(len(allmessages["allmessages"])):
            userInfoGL = await crud.get_user(db=db, user_id=allmessages["allmessages"][indexOfMSGS]["sender_id"])
            allmessages["allmessages"][indexOfMSGS]["full_name"] = userInfoGL.full_name
    for clientWhichJoined in direct_connections[dialog_id]:
        await clientWhichJoined.send_text(json.dumps(allmessages))

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            msg_in = schemas.MessageCreate(dialog_id=dialog_id, content=data["content"])
            msg = await crud.create_direct_message(db, user_id, msg_in)

            msg_out = schemas.MessageOut.from_orm(msg).dict()
            userInfo = await crud.get_user(db=db, user_id=user_id)
            msg_out["full_name"] = userInfo.full_name
            for client in direct_connections[dialog_id]:
                await client.send_text(json.dumps(jsonable_encoder(msg_out)))

    except WebSocketDisconnect:
        direct_connections[dialog_id].remove(websocket)
