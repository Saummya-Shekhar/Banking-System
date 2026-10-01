from openai import OpenAI
from config import OPENROUTER_API_KEY as API_KEY
import json
from config import SYSTEM_PROMPT, MAX_ITERATIONS
from agent.tools import Tools, TOOL_MAP
from models.models import User
from sqlalchemy.orm import Session

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)
history = []

history.append({
    "role": "system",
    "content": SYSTEM_PROMPT
})

def execute_tool(item, db:Session, user: User):

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


def run_agent(prompt: str, db: Session,user: User):

    history.append({
    "role": "user",
    "content": prompt
    })

    for iteration in range(MAX_ITERATIONS):

        response = client.responses.create(
            model="openrouter/free",
            input=history,
            tools=Tools
        )

        # Add the model's output to conversation history
        history.extend(response.output)

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        # --------------------------------
        # No tool calls
        # --------------------------------

        if not tool_calls:
            final_response = response
            break

        # --------------------------------
        # Execute tools
        # --------------------------------

        tool_outputs = []

        for item in tool_calls:

            print(f"Tool: {item.name}")
            print(f"Arguments: {item.arguments}")

            tool_output = execute_tool(item, db, user)

            tool_outputs.append(tool_output)

        # --------------------------------
        # Send tool results back to LLM
        # --------------------------------

        history.extend(tool_outputs)

    else:

        final_response = None

    if response:
        return {
            "output": response.output_text
        }
    
    else:
        return {
            "output": "Agent stopped because maximum iterations were reached."
        }

        



