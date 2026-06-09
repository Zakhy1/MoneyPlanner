from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Account


class AccountService:
    def __init__(self, session: AsyncSession):
        self.session = session

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

    async def create_account(self, param):
        pass

    async def update_account(self, account_id, param, param1):
        pass

    async def partial_update_account(self, account_id, param, param1):
        pass

    async def delete_account(self, account_id, param):
        pass
