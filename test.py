from getpass import getpass
import re
import sys

from config import DB_URL, OPENROUTER_API_KEY


def main() -> int:
    if not DB_URL:
        print("DB_URL is missing. Add it to your .env file.")
        return 1

    if not OPENROUTER_API_KEY:
        print("OPENROUTER_API_KEY is missing. Add it to your .env file.")
        return 1

    from database import SessionLocal
    from models.models import Conversation, User
    from agent import agent as agent_module
    from utils.agent import get_or_create_conversation_test

    agent_module.get_or_create_conversation = get_or_create_conversation_test
    run_agent = agent_module.run_agent

    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.username).all()
        if not users:
            print("No users found in the configured database.")
            return 1

        print("Choose a user for this local agent test:")
        for index, user in enumerate(users, start=1):
            print(f"{index}. {user.username}")

        while True:
            selection = input("User number (or q to quit): ").strip()
            if selection.lower() == "q":
                return 0
            if selection.isdigit() and 1 <= int(selection) <= len(users):
                user = users[int(selection) - 1]
                break
            print("Choose one of the listed numbers.")

        print("\n1. Read-only (default)")
        print("2. Allow live deposits, withdrawals, and transfers")
        mode = input("Mode [1]: ").strip() or "1"
        pin = None

        if mode == "2":
            confirmation = input(
                "This uses the configured database and can move real balances. "
                "Type ALLOW LIVE WRITES to continue: "
            ).strip()
            if confirmation != "ALLOW LIVE WRITES":
                print("Write access was not enabled.")
                return 0

            while True:
                pin = getpass("Account PIN (input hidden): ")
                if re.fullmatch(r"\d{4}", pin):
                    break
                print("The PIN must be exactly four digits.")
        elif mode != "1":
            print("Unknown mode; continuing read-only.")

        conversation = Conversation(
            user_id=user.id,
            title="Local CLI agent test",
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        print(f"\nTesting as {user.username}. Conversation: {conversation.id}")
        print("Enter a prompt, or /quit to exit.")
        if pin is None:
            print("Read-only mode is active; financial write tools will be blocked.")
        else:
            print("Live write mode is active for this session.")

        while True:
            try:
                prompt = input("\nYou: ").strip()
            except EOFError:
                print()
                break

            if prompt.lower() in {"/quit", "/exit"}:
                break
            if not prompt:
                continue

            try:
                result = run_agent(
                    prompt=prompt,
                    db=db,
                    user=user,
                    conversation_id=conversation.id,
                    pin=pin,
                )
                print(f"Agent: {result.get('output', result)}")
            except Exception as exc:
                db.rollback()
                print(f"Agent call failed: {exc}")

        return 0
    finally:
        db.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(0)