from openai import OpenAI
from config import OPENROUTER_API_KEY as API_KEY
import json
from config import SYSTEM_PROMPT, MAX_ITERATIONS
from agent.tools import TOOL_MAP, TOOLS
from models.models import User
from sqlalchemy.orm import Session
from .tools import ReadAndWriteTools, ReadOnlyTools


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

history = []

history.append({
    "role": "system",
    "content": SYSTEM_PROMPT
})


def execute_tool(
    item,
    db: Session,
    user: User,
    pin: str | None = None
):

    try:
        arguments = json.loads(item.arguments)

    except json.JSONDecodeError:

        return {
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps({
                "error": "Invalid JSON arguments."
            })
        }

    if item.name not in TOOL_MAP:

        return {
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps({
                "error": f"Tool '{item.name}' not found."
            })
        }

    try:

        if item.name in ReadAndWriteTools:

            if pin is None:
                raise ValueError("PIN is required for deposit.")

            result = TOOL_MAP[item.name](**arguments, pin=pin, db=db, user=user)

        else:

            result = TOOL_MAP[item.name](**arguments, db=db, user=user)

    except Exception as e:

        import traceback

        print("\n========== TOOL ERROR ==========")
        print(f"Tool: {item.name}")
        print(f"Arguments: {item.arguments}")
        traceback.print_exc()
        print("================================\n")

        result = {
            "error": f"Tool execution failed: {str(e)}"
        }

    return {
        "type": "function_call_output",
        "call_id": item.call_id,
        "output": json.dumps(result)
    }


def run_agent(prompt: str, db: Session, user: User, pin: str | None = None):

    history.append({
        "role": "user",
        "content": prompt
    })

    for iteration in range(MAX_ITERATIONS):

        response = client.responses.create(
            model="poolside/laguna-s-2.1:free",
            input=history,
            tools=TOOLS
        )

        history.extend(response.output)

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]


        if not tool_calls:
            final_response = response
            break


        tool_outputs = []

        for item in tool_calls:

            print(f"Tool: {item.name}")
            print(f"Arguments: {item.arguments}")

            tool_output = execute_tool(
                item=item,
                db=db,
                user=user,
                pin=pin
            )

            tool_outputs.append(tool_output)


        history.extend(tool_outputs)

    else:

        final_response = None

    if final_response:
        print(f"Input Tokens: {final_response.usage.input_tokens}")
        print(f"Output Tokens: {final_response.usage.output_tokens}")

        return {
            "output": final_response.output_text
        }


    else:

        return {
            "output": "Agent stopped because maximum iterations were reached."
        }