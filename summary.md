# Banking System — Current Codebase Summary

This project is a FastAPI-based banking application with user authentication, bank account management, transaction handling, and a conversational agent that can read and perform banking actions using OpenRouter-backed LLM tools.

## Application entry point

The app is created in `main.py` and registers three routers:

```python
app = FastAPI()

app.include_router(Account_Router, prefix="/accounts")
app.include_router(Auth_Router, prefix="/auth")
app.include_router(Agent_Router, prefix="/agent")
```

This means the API exposes account endpoints, auth endpoints, and agent endpoints under separate prefixes.

---

## Authentication routes (`/auth`)

From `routes/auth.py`:

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/signup` | Register a new user with username, email, DOB, and password |
| POST | `/auth/login` | Validate credentials and return a JWT access token |

The JWT flow is implemented in `utils/auth.py`:

- `create_access_token(user)` creates a signed token with `HS256`
- `decode_access_token(token)` validates and decodes the token
- `get_current_user(token, db)` resolves the currently authenticated `User`
- `require_role(role)` enforces role-based access restrictions
- `oAuth2Scheme` is configured with `tokenUrl="/auth/login"`

Password hashing and verification are handled in `utils/encrypt.py` using the `pwdlib` password hasher.

---

## Account routes (`/accounts`)

From `routes/accounts.py`:

| Method | Path | Purpose |
|---|---|---|
| POST | `/accounts/` | Create a new account for the authenticated user |
| GET | `/accounts/{account_number}` | Fetch a single account owned by the current user |
| GET | `/accounts/` | List all accounts for the current user |
| POST | `/accounts/{account_number}/deposit` | Deposit money into an account with PIN validation |
| POST | `/accounts/{account_number}/withdraw` | Withdraw funds after checking PIN and sufficient balance |
| POST | `/accounts/{account_number}/transfer` | Transfer funds to another account after validation |
| GET | `/accounts/{account_number}/transactions` | List all transactions related to an account |
| GET | `/accounts/{account_number}/transactions/{transaction_id}` | Fetch one specific transaction |

The business rules live in `utils/business_logic.py` and include:

- `get_specific_account(user, account_number, db)`
- `get_all_account(user, db)`
- `get_all_transaction(account_number, user, db)`
- `get_specific_transaction(account_number, transaction_id, user, db)`
- `create_transaction_slip(...)` to stage a transaction record before commit

Each account operation validates ownership and uses a PIN check before the transaction is accepted.

---

## Agent routes (`/agent`)

The project also contains an AI-powered banking agent that can read account information and perform write actions.

From `routes/agent.py`:

| Method | Path | Purpose |
|---|---|---|
| GET | `/agent/` | Run a read-only banking query through the agent |
| POST | `/agent/` | Run a write-capable agent request, including a user PIN |

The agent is wired to OpenRouter in `agent/agent.py`:

- `run_agent(prompt, db, user, pin=None)` stores the prompt in conversation history
- it sends the full history plus tool definitions to the OpenAI-compatible responses API
- it processes any returned function calls, executes the selected tool, and appends tool output back into the conversation loop
- it stops once the model returns a final answer or after the configured max iteration limit

Tool support is defined in `agent/tools/tool.py` and the tool map includes:

- `get_account_details`
- `get_transaction_history`
- `deposit_money`
- `withdraw_money`
- `transfer_money`

These functions are exposed to the LLM as callable tools for account reads and financial actions.

---

## Data models

The SQLAlchemy models are in `models/models.py`.

### `User`

Table: `users`

- `id`: primary key
- `username`: unique, max length 50
- `email`: unique, max length 255
- `dob`: date of birth
- `hashed_password`: hashed user password
- `role`: enum value from `Roles`
- `accounts`: relationship to `Account`

### `Account`

Table: `accounts`

- `id`: primary key
- `owner_id`: foreign key to `users.id`
- `account_number`: unique account identifier
- `balance`: float balance, defaults to 0
- `hashed_pin`: stored PIN hash
- `user`: relationship to owner
- `sent_transactions` and `received_transactions`: transaction relationships

### `Transaction`

Table: `transactions`

- `id`: primary key
- `transaction_id`: unique transaction id
- `type`: enum from `Transaction_Type`
- `status`: enum from `Transaction_Status`
- `timestamp`: UTC timestamp
- `sender_account_id`: nullable FK to `accounts.id`
- `receiver_account_id`: nullable FK to `accounts.id`
- `amount`: transaction amount
- `sender_account` / `receiver_account`: relationships
- computed properties `sender_account_number` and `receiver_account_number` provide the related account numbers

---

## Enums and schemas

The enum definitions are in `schemas/Enums.py`:

- `Roles`: `USER`, `ADMIN`
- `Transaction_Type`: `DEPOSIT`, `WITHDRAW`, `TRANSFER`
- `Transaction_Status`: `SUCCESS`, `PENDING`, `FAILED`
- `MessageRole`: used for conversation/message metadata

The core request/response schemas are defined under `schemas/`:

- `schemas/auth.py`: signup/login payloads and account creation input
- `schemas/accounts.py`: account summaries, deposits, withdrawals, transfers, and transaction summaries
- `schemas/agent.py`: request models for the agent endpoints

A common validation rule is the `Pin` type, which is a 4-digit string pattern enforced via Pydantic.

---

## Overall architecture

The system follows a layered backend pattern:

1. `routes/` handles HTTP endpoints and dependency injection
2. `utils/` contains authentication, encryption, and business logic helpers
3. `models/` defines database schema and relationships
4. `schemas/` validates request and response payloads
5. `agent/` extends the app with an OpenRouter-powered intelligent banking assistant that can call account management tools

This gives the project both a standard REST banking API and an AI-assisted interface for querying or acting on account data.
