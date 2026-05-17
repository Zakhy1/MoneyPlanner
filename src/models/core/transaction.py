import decimal
import uuid
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import TEXT, DateTime
from sqlmodel import Field, Relationship, SQLModel

from .account import Account
from .category import Category


class TransactionKind(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"


class Transaction(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    occurred_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(UTC),
    )
    kind: TransactionKind
    amount: decimal.Decimal = Field(default=0, max_digits=12, decimal_places=2)
    account_id: uuid.UUID = Field(foreign_key="account.id")
    counterparty_account_id: uuid.UUID | None = Field(
        default=None, foreign_key="account.id"
    )
    category_id: uuid.UUID | None = Field(default=None, foreign_key="category.id")
    note: str = Field(sa_type=TEXT)

    account: Account = Relationship(
        back_populates="transactions",
        sa_relationship_kwargs={"foreign_keys": "Transaction.account_id"},
    )
    category: Category | None = Relationship(back_populates="transactions")
    counterparty_account: Account | None = Relationship(
        back_populates="counterparty_transactions",
        sa_relationship_kwargs={"foreign_keys": "Transaction.counterparty_account_id"},
    )
