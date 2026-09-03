# Personal Finance Tracker API

A small FastAPI backend: users sign up, log in, and track income/expense
transactions. Includes JWT auth and a summary endpoint that groups
spending by category (SQL `GROUP BY`).

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000/docs** for interactive Swagger UI — you can
try every endpoint from the browser, including logging in and passing
the token automatically (click the "Authorize" button after logging in).

A `finance.db` SQLite file is created automatically on first run.

## How to try it (curl)

```bash
# 1. Sign up
curl -X POST http://127.0.0.1:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"secret123"}'

# 2. Log in (note: form data, not JSON — this is the OAuth2 password flow)
curl -X POST http://127.0.0.1:8000/login \
  -d "username=you@example.com&password=secret123"
# -> copy the "access_token" from the response

# 3. Add a transaction (replace TOKEN)
curl -X POST http://127.0.0.1:8000/transactions \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount":1200,"type":"expense","category":"groceries","date":"2026-09-02"}'

# 4. Get the summary
curl http://127.0.0.1:8000/summary -H "Authorization: Bearer TOKEN"
```

## Project layout

```
finance-tracker/
├── main.py              # FastAPI app, wires up routers
├── database.py          # DB engine/session setup
├── models.py             # SQLAlchemy tables: User, Transaction
├── schemas.py             # Pydantic request/response shapes
├── auth.py                # password hashing + JWT create/verify
├── routers/
│   ├── users.py          # /signup, /login
│   └── transactions.py   # transaction CRUD + /summary
└── requirements.txt
```

## Endpoints

| Method | Route | Auth? | Purpose |
|---|---|---|---|
| POST | `/signup` | no | create a user |
| POST | `/login` | no | returns a JWT |
| POST | `/transactions` | yes | add a transaction |
| GET | `/transactions` | yes | list your transactions |
| PUT | `/transactions/{id}` | yes | edit one of yours |
| DELETE | `/transactions/{id}` | yes | delete one of yours |
| GET | `/summary` | yes | total income, total expense, balance, spend-by-category |

## Notes on the design (for interview talking points)

- **Why JWT:** stateless — the server doesn't need to store sessions;
  the token itself proves who you are on each request.
- **Why scope every query by `user_id`:** so one user can never read,
  edit, or delete another user's transactions, even if they guess an ID.
- **Why separate `models.py` and `schemas.py`:** SQLAlchemy models
  describe the database table; Pydantic schemas describe what the API
  accepts/returns. Keeping them separate means we control exactly what
  goes out (e.g. `hashed_password` is never serialized in a response).
- **The `/summary` `GROUP BY`:** lives in `routers/transactions.py`,
  grouping expense rows by `category` and summing `amount` per group —
  the one query worth being able to explain line-by-line.
