from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from database import Base
from schemas.Enums import (
    Roles,
    Transaction_Status,
    Transaction_Type,
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    dob = Column(Date, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(Roles), nullable=False)

    accounts = relationship(
        "Account",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_number = Column(String(20), unique=True, nullable=False, index=True)
    balance = Column(Float, nullable=True, default=0)
    hashed_pin = Column(String(255), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)


    user = relationship(
        "User",
        back_populates="accounts",
    )

    sent_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.sender_account_id",
        back_populates="sender_account",
    )

    received_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.receiver_account_id",
        back_populates="receiver_account",
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50), unique=True, nullable=False, index=True)
    type = Column(Enum(Transaction_Type), nullable=False)
    status = Column(Enum(Transaction_Status), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    sender_account_id = Column(
        Integer,
        ForeignKey("accounts.id"),
        nullable=True,
    )

    receiver_account_id = Column(
        Integer,
        ForeignKey("accounts.id"),
        nullable=True,
    )

    amount = Column(Float, nullable=False)

    sender_account = relationship(
        "Account",
        foreign_keys=[sender_account_id],
        back_populates="sent_transactions",
    )

    receiver_account = relationship(
        "Account",
        foreign_keys=[receiver_account_id],
        back_populates="received_transactions",
    )

    @property
    def sender_account_number(self):
        if self.sender_account is None:
            return None
        return self.sender_account.account_number

    @property
    def receiver_account_number(self):
        if self.receiver_account is None:
            return None
        return self.receiver_account.account_number
