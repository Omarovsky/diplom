from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    full_name: str | None = None

class UserOut(UserBase):
    id: int
    class Config:
        orm_mode = True

class ChannelCreate(BaseModel):
    name: str

class ChannelOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    content: str
    channel_id: int

class MessageOut(BaseModel):
    id: int
    content: str
    timestamp: datetime
    user_id: int
    channel_id: int
    class Config:
        orm_mode = True


class DialogOut(BaseModel): 
    id: int
    user1_id: int
    user2_id: int
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    dialog_id: int
    content: str

class MessageOut(BaseModel):
    id: int
    dialog_id: int
    sender_id: int
    content: str
    timestamp: datetime
    class Config:
        from_attributes = True

