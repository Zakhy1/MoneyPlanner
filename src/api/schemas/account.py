import decimal
import uuid

from sqlmodel import Field, SQLModel

from models.core.account import AccountKind, CurrencyCode


class AccountBase(SQLModel):
    name: str = Field(max_length=64, index=True)
    kind: AccountKind = Field(default=AccountKind.CHECKING)
    currency_code: CurrencyCode = Field(default=CurrencyCode.RUB)
    include_in_net_worth: bool
    credit_limit: decimal.Decimal | None = Field(
        default=None, max_digits=12, decimal_places=2
    )


class AccountCreate(AccountBase):
    opening_balance: decimal.Decimal = Field(default=0, max_digits=12, decimal_places=2)


class AccountRead(AccountBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class AccountUpdate(AccountBase):
    pass


class AccountPatch(SQLModel):
    name: str | None = Field(max_length=64, index=True, default=None)
    kind: AccountKind | None = Field(default=None)
    currency_code: CurrencyCode | None = Field(default=None)
    include_in_net_worth: bool | None = None
    credit_limit: decimal.Decimal | None = Field(
        default=None, max_digits=12, decimal_places=2
    )
