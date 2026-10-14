from datetime import UTC, datetime
from uuid import uuid4
from sqlalchemy import Boolean

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum as SQLenum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from database import Base
from schemas.Enums import (
    Roles,
    Transaction_Status,
    Transaction_Type,
    MessageRole
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    dob = Column(Date, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLenum(Roles), nullable=False)

    accounts = relationship(
        "Account",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    conversations = relationship(
    "Conversation",
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
    type = Column(SQLenum(Transaction_Type), nullable=False)
    status = Column(SQLenum(Transaction_Status), nullable=False)
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

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(150), nullable=True)
    is_archived = Column(Boolean, default=False, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.sequence",
    )

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)

    conversation_id = Column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sequence = Column(Integer, nullable=False)
    role = Column(SQLenum(MessageRole), nullable=False)

    # Normal user/assistant text
    content = Column(Text, nullable=True)

    # Used for tool calls and tool responses
    raw_payload = Column(JSON, nullable=False)
    tool_name = Column(String(100), nullable=True)
    tool_call_id = Column(String(100), nullable=True)
    tool_arguments = Column(JSON, nullable=True)
    tool_result = Column(JSON, nullable=True)

    model_name = Column(String(150), nullable=True)
    token_count = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages",
    )

    __table_args__ = (
        UniqueConstraint(
            "conversation_id",
            "sequence",
            name="uq_conversation_message_sequence",
        ),
        Index(
            "ix_conversation_created",
            "conversation_id",
            "created_at",
        ),
    )

