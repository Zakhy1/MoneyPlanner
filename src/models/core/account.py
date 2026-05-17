import decimal
import uuid
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .transaction import Transaction


class CurrencyCode(str, Enum):
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"


class AccountKind(str, Enum):
    CASH = "cash"
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    LOAN = "loan"


class Account(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=64, index=True)
    kind: AccountKind = Field(default=AccountKind.CHECKING)
    currency_code: CurrencyCode = Field(default=CurrencyCode.RUB)
    include_in_net_worth: bool
    opening_balance: decimal.Decimal = Field(default=0, max_digits=12, decimal_places=2)
    credit_limit: decimal.Decimal | None = Field(
        default=None, max_digits=12, decimal_places=2
    )
    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="accounts")  # noqa: F821

    transactions: list["Transaction"] = Relationship(
        back_populates="account",
        sa_relationship_kwargs={"foreign_keys": "Transaction.account_id"},
    )
    counterparty_transactions: list["Transaction"] = Relationship(
        back_populates="counterparty_account",
        sa_relationship_kwargs={"foreign_keys": "Transaction.counterparty_account_id"},
    )
