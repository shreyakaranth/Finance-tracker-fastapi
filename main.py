"""
Entry point. Run with:
    uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs for interactive Swagger UI.
"""

from fastapi import FastAPI

from database import Base, engine
import models  # noqa: F401 (needed so Base knows about the tables before create_all)
from routers import users, transactions

# creates finance.db + tables on first run if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Finance Tracker API")

app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(transactions.summary_router)


@app.get("/")
def root():
    return {"message": "Finance Tracker API is running. Visit /docs to try it out."}
