"""
Pydantic models = the "shape" of data going in and out of the API.
SQLAlchemy models (models.py) = the shape of data in the database.
These are kept separate on purpose (e.g. we never send hashed_password back out).
"""

from datetime import date
from pydantic import BaseModel, EmailStr, Field


# ---------- Users ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True  # lets us return a SQLAlchemy User directly


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Transactions ----------

class TransactionCreate(BaseModel):
    amount: float = Field(gt=0)
    type: str          # "income" or "expense"
    category: str
    date: date


class TransactionOut(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: date

    class Config:
        from_attributes = True


class SummaryOut(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    by_category: dict[str, float]
