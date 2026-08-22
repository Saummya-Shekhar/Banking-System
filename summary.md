# Banking System — Codebase Summary

Generated via CodeGraph exploration of the FastAPI banking system.

## App Entry (`main.py`)

```python
app = FastAPI()
app.include_router(Account_Router, prefix="/accounts")  # routes/accounts.py
app.include_router(Auth_Router, prefix="/auth")         # routes/auth.py
```

---

## Routes

### `routes/auth.py` (prefix `/auth`)

| Method | Path | Function | Description |
|---|---|---|---|
| POST | `/auth/signup` | `signup(signup: SignupRequest, db)` | Creates a new `User` (rejects duplicate username/email), role defaults to `Roles.USER` |
| POST | `/auth/login` | `Login(login: LoginRequest, db)` | Verifies credentials, returns JWT access token |

### `routes/accounts.py` (prefix `/accounts`)

| Method | Path | Function | Response Model | Description |
|---|---|---|---|---|
| POST | `/accounts/` | `create_account(info: CreateAccountRequest, user, db)` | — | Creates an `Account` for the current user with a generated account number and hashed PIN |
| GET | `/accounts/{account_number}` | `get_account_details(account_number, user, db)` | `AccountSummary` | Fetch a single account owned by the user |
| GET | `/accounts/` | `get_all_accounts(user, db)` | `list[AccountSummary]` | List all accounts owned by the user |
| POST | `/accounts/{account_number}/deposit` | `deposit(account_number, info: DepositRequest, user, db)` | `BasicResponse` | Deposits funds; validates PIN; logs a `Transaction` slip (success/failed) |
| POST | `/accounts/{account_number}/withdraw` | `deposit(account_number, info: DepositRequest, user, db)` *(shadowed name — actually withdraw logic)* | `BasicResponse` | Withdraws funds; validates PIN and balance; logs a `Transaction` slip |
| POST | `/accounts/{account_number}/transfer` | `transfer(account_number, info: TransferRequest, user, db)` | `BasicResponse` | Transfers funds between accounts; validates receiver, PIN, and balance; logs a `Transaction` slip |
| GET | `/accounts/{account_number}/transactions` | `get_all_transactions(account_number, user, db)` | `list[TransactionSummary]` | List all transactions (sent or received) for an account |
| GET | `/accounts/{account_number}/transactions/{transaction_id}` | `get_specific_transactions(account_number, transaction_id, user, db)` | `TransactionSummary` | Fetch one specific transaction |

> Note: the withdraw endpoint's handler function is also named `deposit` (name collision with the deposit handler above) — same file, different route decorator.

---

## Functions

### `utils/business_logic.py`

- `get_specific_account(user, account_number, db)` — fetches a user-owned `Account` by number, 401 if not found
- `get_all_account(user, db)` — fetches all accounts owned by user, 401 if none
- `get_all_transaction(account_number, user, db)` — fetches all transactions (sent/received) for an account, ordered by timestamp desc
- `get_specific_transaction(account_number, transaction_id, user, db)` — fetches one transaction by id scoped to the account
- `create_transaction_slip(db, amount, transaction_type, transaction_status, sender_id=None, receiver_id=None)` — builds and stages a `Transaction` row (does not commit)

### `utils/auth.py`

- `create_access_token(user) -> str` — signs a JWT (HS256) with `sub`, `role`, 30-min expiry
- `decode_access_token(token)` — verifies/decodes JWT, raises 401 on invalid token
- `get_current_user(token, db) -> User` — FastAPI dependency resolving the authenticated user from the bearer token
- `require_role(role)` — dependency factory returning a `checker(user)` that enforces a specific `Roles` value (403 if mismatched)
- `oAuth2Scheme` — `OAuth2PasswordBearer(tokenUrl="/auth/login")`
- `ALGORITHM = "HS256"`

### `utils/encrypt.py`

- `hash_password(password) -> str` — hashes via `pwdlib` recommended hasher
- `verify_password(password, hashed_password) -> bool`
- `generate_transaction_id() -> str` — random UUID4
- `generate_account_number() -> str` — `"ACC" + 7-digit random suffix`
- `password_hasher = PasswordHash.recommended()`

---

## Schemas (Pydantic)

### `schemas/auth.py`

| Class | Fields |
|---|---|
| `SignupRequest` | `username: str`, `email: EmailStr`, `dob: date`, `password: str` |
| `LoginRequest` | `username: str`, `password: str` |
| `LoginResponse` | `access_token: str`, `token_type: str` |
| `CreateAccountRequest` | `pin: Pin` (4-digit string) |

### `schemas/accounts.py`

| Class | Fields |
|---|---|
| `AccountSummary` | `account_number: str`, `balance: float` *(from_attributes)* |
| `CreateAccountRequest` | `pin: Pin` |
| `UserResponse` | `id: int`, `username: str`, `email: EmailStr` |
| `DepositRequest` | `amount: float (>0)`, `pin: Pin` |
| `WithdrawRequest` | `amount: float (>0)`, `pin: Pin` |
| `TransferRequest` | `receiver_account_number: str`, `amount: float (>0)`, `pin: Pin` |
| `TransactionSummary` | `transaction_id: str`, `amount: float`, `type: Transaction_Type`, `status: Transaction_Status`, `timestamp: datetime`, `receiver_account_number: str \| None`, `sender_account_number: str \| None` *(from_attributes)* |
| `BasicResponse` | `message: str`, `balance: float`, `slip: TransactionSummary` *(from_attributes)* |

`Pin = Annotated[str, Field(pattern=r"^\d{4}$")]` (defined in both `schemas/auth.py` and `schemas/accounts.py`)

### `schemas/Enums.py`

| Enum | Values |
|---|---|
| `Roles` | `USER`, `ADMIN` |
| `Transaction_Type` | `DEPOSIT`, `WITHDRAW`, `TRANSFER` |
| `Transaction_Status` | `SUCCESS`, `PENDING`, `FAILED` |

---

## Models (SQLAlchemy — `models/models.py`)

### `User` (table: `users`)
- `id: int` (PK)
- `username: str(50)` (unique)
- `email: str(255)` (unique)
- `dob: Date`
- `hashed_password: str(255)`
- `role: Enum(Roles)`
- `accounts` → relationship to `Account` (cascade delete-orphan)

### `Account` (table: `accounts`)
- `id: int` (PK)
- `owner_id: int` (FK → `users.id`)
- `account_number: str(20)` (unique, indexed)
- `balance: float` (default 0)
- `hashed_pin: str(255)`
- `user` → relationship to `User`
- `sent_transactions` / `received_transactions` → relationships to `Transaction`

### `Transaction` (table: `transactions`)
- `id: int` (PK)
- `transaction_id: str(50)` (unique, indexed)
- `type: Enum(Transaction_Type)`
- `status: Enum(Transaction_Status)`
- `timestamp: DateTime(timezone=True)` (default now UTC)
- `sender_account_id: int` (FK → `accounts.id`, nullable)
- `receiver_account_id: int` (FK → `accounts.id`, nullable)
- `amount: float`
- `sender_account` / `receiver_account` → relationships to `Account`
- `sender_account_number` / `receiver_account_number` → computed properties resolving the related account's number
