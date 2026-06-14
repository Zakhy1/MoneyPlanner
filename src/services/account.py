import uuid

from sqlmodel import delete, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Account, Transaction
from models.core.account import AccountKind
from services.exceptions import (
    AcccountDoesNotExistsError,
    OwnerPermissionError,
    ValidationError,
)


class AccountService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_owner(self, account: Account, user_id: uuid.UUID):
        if account.user_id != user_id:
            raise OwnerPermissionError

    async def get_account(self, account_id: uuid.UUID):
        db_account = await self.session.get(Account, account_id)
        if db_account is None:
            raise AcccountDoesNotExistsError
        return db_account

    async def validate_account(self, account: Account):
        """
        Цель — проверить валидность счета по следующим правилам:
        * `credit_limit` разрешен только для kind=credit_card
        *
        :return:
        """
        statement = select(Account).where(
            Account.user_id == account.user_id, Account.name == Account.name
        )
        existing_account = await self.session.exec(statement)
        if existing_account.first() is not None:
            raise ValidationError("An account with the same name already exists")
        if account.credit_limit is not None and account.kind != AccountKind.CREDIT_CARD:
            raise ValidationError("credit_limit is only allowed for credit cards")

    async def get_list_account(self, page, page_size, user_id):
        """
        :param page_size:
        :param page:
        :param user_id:
        :return: list Account
        """
        offset_value = (page - 1) * page_size
        statement = (
            select(Account)
            .where(Account.user_id == user_id)
            .order_by(Account.name)
            .offset(offset_value)
            .limit(page_size)
        )
        accounts = await self.session.exec(statement)
        return accounts.all()

    async def create_account(self, account: Account) -> Account:
        await self.validate_account(account)
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def update_account(
        self, account_id: uuid.UUID, account: Account, user_id: uuid.UUID
    ):
        db_account = await self.get_account(account_id)
        await self.check_owner(account, user_id)
        await self.validate_account(account)
        update_dict = account.model_dump()

        db_account.sqlmodel_update(update_dict)

        self.session.add(db_account)
        await self.session.commit()
        await self.session.refresh(db_account)
        return db_account

    async def partial_update_account(
        self, account_id: uuid.UUID, update_data: dict, user_id: uuid.UUID
    ):
        db_account = await self.get_account(account_id)

        # Проверка
        candidate = db_account.model_copy(update=update_data)
        await self.validate_account(candidate)
        await self.check_owner(db_account, user_id)

        for key, value in update_data.items():
            if key not in [
                "name",
                "kind",
                "currency_code",
                "include_in_net_worth",
                "credit_limit",
            ]:
                continue
            setattr(db_account, key, value)

        self.session.add(db_account)
        await self.session.commit()
        await self.session.refresh(db_account)
        return db_account

    async def delete_account(self, account_id: uuid.UUID, user_id: uuid.UUID):
        """
        При удалении счета:
        * Всем транзакциям с counterparty_account_id = account_id будет установлен null
        * Удалить транзакции внутри счета (где account_id = counterparty_account_id)
        :param account_id:
        :param user_id:
        :return:
        """
        db_account = await self.get_account(account_id)
        await self.check_owner(db_account, user_id)

        # Обновляем транзакции
        statement = (
            update(Transaction)
            .where(Transaction.counterparty_account_id == account_id)
            .values(counterparty_account_id=None)
        )
        await self.session.exec(statement)

        statement = (
            update(Transaction)
            .where(Transaction.account_id == account_id)
            .values(account_id=None)
        )
        await self.session.exec(statement)

        statement = delete(Transaction).where(
            Transaction.account_id == account_id,
            Transaction.counterparty_account_id == account_id,
        )
        await self.session.exec(statement)

        # Удаляем сам счет
        await self.session.delete(db_account)
        await self.session.commit()
        return True
