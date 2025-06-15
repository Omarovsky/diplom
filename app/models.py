from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, UniqueConstraint
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    messages = relationship("Message", back_populates="channel", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)

    user = relationship("User")
    channel = relationship("Channel", back_populates="messages")



class Dialog(Base):
    __tablename__ = "dialogs"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    __table_args__ = (UniqueConstraint('user1_id', 'user2_id', name='unique_dialog'),)

    messages = relationship("DirectMessage", back_populates="dialog", cascade="all, delete-orphan")


class DirectMessage(Base):
    __tablename__ = "direct_messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    dialog_id = Column(Integer, ForeignKey("dialogs.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    dialog = relationship("Dialog", back_populates="messages")
    sender = relationship("User")

