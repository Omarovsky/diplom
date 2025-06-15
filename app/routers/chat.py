from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas
from fastapi.security import OAuth2PasswordBearer
from app.utils import decode_token
from jose import JWTError

router = APIRouter(prefix="/chat", tags=["Chat"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = decode_token(token)
        return int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/channels", response_model=schemas.ChannelOut)
async def create_channel(channel: schemas.ChannelCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_channel(db, channel)

@router.get("/channels", response_model=list[schemas.ChannelOut])
async def list_channels(db: AsyncSession = Depends(get_db)):
    return await crud.get_channels(db)

@router.post("/messages", response_model=schemas.MessageOut)
async def post_message(
    message: schemas.MessageCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_message(db, message, int(user_id))

@router.get("/channels/{channel_id}/messages", response_model=list[schemas.MessageOut])
async def get_messages(channel_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_messages_by_channel(db, channel_id)
