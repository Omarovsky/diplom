from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas, models
from fastapi.security import OAuth2PasswordBearer
from app.utils import decode_token
from jose import JWTError
from sqlalchemy import or_, select

router = APIRouter(prefix="/direct", tags=["Direct Messages"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = decode_token(token)
        return int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/dialog/{other_user_id}", response_model=schemas.DialogOut)
async def get_or_create_dialog(other_user_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await crud.get_or_create_dialog(db, user_id, other_user_id)

@router.post("/messages", response_model=schemas.MessageOut)
async def send_message(msg: schemas.MessageCreate, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await crud.create_direct_message(db, user_id, msg)

@router.get("/messages/{dialog_id}", response_model=list[schemas.MessageOut])
async def get_messages(dialog_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_dialog_messages(db, dialog_id)

@router.get("/dialogs", response_model=list[schemas.DialogOut])
async def get_user_dialogs(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Dialog).where(
            or_(models.Dialog.user1_id == user_id, models.Dialog.user2_id == user_id)
        )
    )
    return result.scalars().all()

