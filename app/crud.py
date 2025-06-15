from app.models import Channel, Message, Dialog, DirectMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from app import models, schemas
from app.utils import hash_password, verify_password
from app.schemas import MessageCreate, DialogOut

async def create_user_with_password(db: AsyncSession, user: schemas.UserCreate):
    new_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def authenticate_user(db: AsyncSession, username: str, password: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    user = result.scalars().first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalars().first()

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()

async def update_user(db: AsyncSession, user_id: int, user_update: schemas.UserUpdate):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        return None

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        return None

    await db.delete(user)
    await db.commit()
    return user

async def create_channel(db: AsyncSession, channel: schemas.ChannelCreate):
    new_channel = Channel(name=channel.name)
    db.add(new_channel)
    await db.commit()
    await db.refresh(new_channel)
    return new_channel

async def get_channels(db: AsyncSession):
    result = await db.execute(select(Channel))
    return result.scalars().all()

async def create_message(db: AsyncSession, message: MessageCreate | dict, user_id: int):
    if isinstance(message, dict):
        message = MessageCreate(**message)

    new_message = Message(
        content=message.content,
        user_id=user_id,
        channel_id=message.channel_id
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message

async def get_messages_by_channel(db: AsyncSession, channel_id: int):
    result = await db.execute(
        select(Message).where(Message.channel_id == channel_id).order_by(Message.timestamp)
    )
    return result.scalars().all()

async def get_or_create_dialog(db: AsyncSession, user1_id: int, user2_id: int):
    uid1, uid2 = sorted([user1_id, user2_id])
    result = await db.execute(
        select(Dialog).where(
            and_(
                Dialog.user1_id == uid1,
                Dialog.user2_id == uid2
            )
        )
    )
    dialog = result.scalars().first()
    if dialog:
        return dialog

    new_dialog = Dialog(user1_id=uid1, user2_id=uid2)
    db.add(new_dialog)
    await db.commit()
    await db.refresh(new_dialog)
    return new_dialog

async def create_direct_message(db: AsyncSession, sender_id: int, msg: schemas.MessageCreate):
    new_msg = DirectMessage(
        dialog_id=msg.dialog_id,
        sender_id=sender_id,
        content=msg.content
    )
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)
    return new_msg

async def get_dialog_messages(db: AsyncSession, dialog_id: int):
    result = await db.execute(
        select(DirectMessage).where(DirectMessage.dialog_id == dialog_id).order_by(DirectMessage.timestamp)
    )
    return result.scalars().all()

async def get_users_from_dialogid(db: AsyncSession, dialog_id: int):
    row = await db.execute(
        select(models.Dialog.user1_id, models.Dialog.user2_id).where(
            models.Dialog.id == dialog_id
        )
    )
    user_ids = row.first()
    if user_ids:
        return list(user_ids)
