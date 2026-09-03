"""
CRUD for transactions, plus the /summary endpoint.
Every query here is filtered by the logged-in user's id, so users can
only ever see or touch their own transactions.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
import schemas
import auth
from database import get_db

router = APIRouter(prefix="/transactions", tags=["transactions"])

# separate router (no prefix) just for /summary, since it's not nested under /transactions
summary_router = APIRouter(tags=["summary"])


@router.post("", response_model=schemas.TransactionOut)
def create_transaction(
    tx_in: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if tx_in.type not in ("income", "expense"):
        raise HTTPException(status_code=400, detail="type must be 'income' or 'expense'")

    tx = models.Transaction(**tx_in.model_dump(), user_id=current_user.id)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@router.get("", response_model=list[schemas.TransactionOut])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.user_id == current_user.id)
        .order_by(models.Transaction.date.desc())
        .all()
    )


def _get_owned_transaction(tx_id: int, db: Session, current_user: models.User) -> models.Transaction:
    tx = (
        db.query(models.Transaction)
        .filter(models.Transaction.id == tx_id, models.Transaction.user_id == current_user.id)
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.put("/{tx_id}", response_model=schemas.TransactionOut)
def update_transaction(
    tx_id: int,
    tx_in: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    tx = _get_owned_transaction(tx_id, db, current_user)
    for field, value in tx_in.model_dump().items():
        setattr(tx, field, value)
    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/{tx_id}")
def delete_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    tx = _get_owned_transaction(tx_id, db, current_user)
    db.delete(tx)
    db.commit()
    return {"detail": "Transaction deleted"}


@summary_router.get("/summary", response_model=schemas.SummaryOut)
def summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Totals + spend-by-category for the logged-in user."""
    base = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id)

    total_income = base.filter(models.Transaction.type == "income").with_entities(
        func.coalesce(func.sum(models.Transaction.amount), 0.0)
    ).scalar()

    total_expense = base.filter(models.Transaction.type == "expense").with_entities(
        func.coalesce(func.sum(models.Transaction.amount), 0.0)
    ).scalar()

    # the GROUP BY flex: total expense amount per category
    category_rows = (
        db.query(models.Transaction.category, func.sum(models.Transaction.amount))
        .filter(
            models.Transaction.user_id == current_user.id,
            models.Transaction.type == "expense",
        )
        .group_by(models.Transaction.category)
        .all()
    )
    by_category = {category: total for category, total in category_rows}

    return schemas.SummaryOut(
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        by_category=by_category,
    )
