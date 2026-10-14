import json
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from models.models import User, Conversation, ConversationMessage
from schemas.Enums import MessageRole
from config import SYSTEM_PROMPT

def get_active_conversation(user: User, db: Session):
    conversation = db.query(Conversation).filter(Conversation.user_id == user.id, Conversation.is_archived == False).order_by(desc(Conversation.updated_at)).first()
    return conversation

def get_or_create_conversation_test(user: User, db: Session, conversation_id: str | None = None) -> Conversation:
    if conversation_id is not None:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id,
        ).first()
        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )
        return conversation

    conversation = get_active_conversation(user,db)
    if conversation:
        return conversation

    
    conversation = Conversation(
    user_id=user.id,
    title="New conversation",
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation

def get_or_create_conversation(user: User, db: Session) -> Conversation:
    conversation = get_active_conversation(user,db)
    if conversation:
        return conversation

    
    conversation = Conversation(
    user_id=user.id,
    title="New conversation",
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation

def next_sequence(db: Session, conversation_id: str)->int:
    last_sequence = db.query(func.max(ConversationMessage.sequence)).filter(ConversationMessage.conversation_id == conversation_id).scalar()

    return (last_sequence or 0) + 1

def save_message(db: Session, conversation: Conversation, role: MessageRole, raw_payload: dict, content: str | None = None, tool_name: str | None = None, tool_call_id: str | None = None, tool_arguments: dict | None = None, tool_result: dict | None = None):
    message = ConversationMessage(
        conversation_id=conversation.id,
        sequence=next_sequence(db, conversation.id),
        role=role,
        content=content,
        raw_payload=raw_payload,
        tool_name=tool_name,
        tool_call_id=tool_call_id,
        tool_arguments=tool_arguments,
        tool_result=tool_result,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message

def build_model_input(db: Session, conversation: Conversation)->list[dict]:
    messages = db.query(ConversationMessage).filter(ConversationMessage.conversation_id == conversation.id).order_by(ConversationMessage.sequence.asc()).all()

    history = [{
        "role": "system",
        "content": SYSTEM_PROMPT
    }]

    for message in messages:
        history.append(message.raw_payload)

    return history