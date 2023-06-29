from typing import List

from database.connection import Base
from database.enums import BrokerType, CurrencyType
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"
    telegram_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column()
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_active_conversation: Mapped[bool] = mapped_column(default=True)
    is_banned: Mapped[bool] = mapped_column(default=False)
    accounts: Mapped[List["Account"]] = relationship(back_populates="user")
    histories: Mapped[List["History"]] = relationship(back_populates="user")


class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String(32))
    histories: Mapped[List["History"]] = relationship(back_populates="chat")


class History(Base):
    __tablename__ = "histories"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    user: Mapped["User"] = relationship(back_populates="histories")
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    chat: Mapped["Chat"] = relationship(back_populates="histories")
    command: Mapped[str] = mapped_column(String(255))


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    user: Mapped["User"] = relationship(back_populates="accounts")
    broker_type: Mapped["BrokerType"]
    api_key: Mapped[str] = mapped_column(String(255))
    broker_account_id: Mapped[str] = mapped_column(String(255))
    is_notifications: Mapped[bool] = mapped_column(default=True)
    orders: Mapped[List["Order"]] = relationship(back_populates="account")
    __table_args__ = (
        UniqueConstraint(
            "broker_type", "api_key", "broker_account_id", name="_duplicates"
        ),
    )


class Share(Base):
    __tablename__ = "shares"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    broker_type: Mapped["BrokerType"]
    name: Mapped[str] = mapped_column(String(32))
    code: Mapped[str] = mapped_column(String(32))
    step: Mapped[float] = mapped_column()
    orders: Mapped[List["Order"]] = relationship(back_populates="share")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    amount: Mapped[int] = mapped_column()
    price: Mapped[float] = mapped_column()
    currency: Mapped[CurrencyType]
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    account: Mapped["Account"] = relationship(back_populates="orders")
    share_id: Mapped[int] = mapped_column(ForeignKey("shares.id"))
    share: Mapped["Share"] = relationship(back_populates="orders")
    # status: int
    # type_: int
