from openai import OpenAI
from config import OPENROUTER_API_KEY as API_KEY
import json
from config import SYSTEM_PROMPT, MAX_ITERATIONS
from agent.tools import TOOL_MAP, TOOLS
from models.models import User,ConversationMessage, Conversation
from sqlalchemy.orm import Session
from schemas.Enums import MessageRole
from .tools import ReadAndWriteTools, ReadOnlyTools
from utils.agent import get_or_create_conversation, save_message, build_model_input, next_sequence

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

history = []

history.append({
    "role": "system",
    "content": SYSTEM_PROMPT
})

def execute_tool(item, db: Session, user: User, pin: str | None = None):
    try:
        arguments = json.loads(item.arguments)
    except json.JSONDecodeError:
        return {
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps({
                "error": "Invalid tool arguments."
            }),
        }

    if item.name not in TOOL_MAP:
        return {
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps({
                "error": f"Unknown tool: {item.name}"
            }),
        }

    try:
        if item.name in ReadAndWriteTools:
            if pin is None:
                raise ValueError(
                    "A PIN is required for this operation."
                )

            result = TOOL_MAP[item.name](
                **arguments,
                pin=pin,
                db=db,
                user=user,
            )
        else:
            result = TOOL_MAP[item.name](
                **arguments,
                db=db,
                user=user,
            )

    except Exception as exc:
        db.rollback()

        result = {
            "error": "Tool execution failed.",
            "detail": str(exc),
        }

    return {
        "type": "function_call_output",
        "call_id": item.call_id,
        "output": json.dumps(result),
    }

def serialize_response_item(item) -> dict:
    
    return item.model_dump(
        mode="json",
        exclude_none=True,
    )

def run_agent(prompt: str, db: Session, user: User, conversation_id: str | None = None, pin: str | None = None):
    conversation = get_or_create_conversation(
        db=db,
        user=user,
        conversation_id=conversation_id,
    )

    user_payload = {
        "role": "user",
        "content": prompt,
    }

    save_message(
        db=db,
        conversation=conversation,
        role=MessageRole.USER,
        content=prompt,
        raw_payload=user_payload,
    )

    final_response = None

    for _ in range(MAX_ITERATIONS):
        history = build_model_input(
            db=db,
            conversation=conversation,
        )

        response = client.responses.create(
            model="openrouter/free",
            input=history,
            tools=TOOLS,
        )

        function_calls = []

        # Save every model output item exactly as returned.
        for item in response.output:
            payload = serialize_response_item(item)

            if item.type == "function_call":
                function_calls.append(item)

                save_message(
                    db=db,
                    conversation=conversation,
                    role=MessageRole.ASSISTANT,
                    raw_payload=payload,
                    tool_name=item.name,
                    tool_call_id=item.call_id,
                    tool_arguments=json.loads(item.arguments),
                )

            elif item.type == "message":
                save_message(
                    db=db,
                    conversation=conversation,
                    role=MessageRole.ASSISTANT,
                    raw_payload=payload,
                    content=response.output_text,
                )

            else:
                save_message(
                    db=db,
                    conversation=conversation,
                    role=MessageRole.ASSISTANT,
                    raw_payload=payload,
                )

        if not function_calls:
            final_response = response
            break

        for item in function_calls:
            tool_output = execute_tool(
                item=item,
                db=db,
                user=user,
                pin=pin,
            )

            tool_result = json.loads(tool_output["output"])

            save_message(
                db=db,
                conversation=conversation,
                role=MessageRole.TOOL,
                raw_payload=tool_output,
                tool_name=item.name,
                tool_call_id=item.call_id,
                tool_result=tool_result,
            )

    if final_response is None:
        return {
            "conversation_id": conversation.id,
            "output": (
                "The request could not be completed within "
                "the allowed number of steps."
            ),
        }

    return {
        "conversation_id": conversation.id,
        "output": final_response.output_text,
    }