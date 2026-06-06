from sqlmodel.ext.asyncio.session import AsyncSession


class AccountService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_list_account(self, page, page_size, user_id):
        pass

    async def create_account(self, param):
        pass

    async def update_account(self, account_id, param, param1):
        pass

    async def partial_update_account(self, account_id, param, param1):
        pass

    async def delete_account(self, account_id, param):
        pass
