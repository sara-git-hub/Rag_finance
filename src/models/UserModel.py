from models.BaseDataModel import BaseDataModel
from models.db_schemes.minirag.schemes.user import User, UserRole
from sqlalchemy import select
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserModel(BaseDataModel):

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def create_user(self, username: str, email: str, password: str, role: UserRole = UserRole.USER):
        async with self.db_client() as session:
            # Check if this is the first user (make them admin)
            result = await session.execute(select(User))
            existing_users = result.scalars().all()

            # First user is always admin
            if len(existing_users) == 0:
                role = UserRole.ADMIN

            new_user = User(
                username=username,
                email=email,
                hashed_password=self.get_password_hash(password),
                role=role,
                is_active=True
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user

    async def get_user_by_username(self, username: str):
        async with self.db_client() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str):
        async with self.db_client() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()

    async def get_all_users(self):
        async with self.db_client() as session:
            result = await session.execute(select(User))
            return result.scalars().all()

    async def update_user_role(self, username: str, new_role: UserRole):
        async with self.db_client() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()
            if user:
                user.role = new_role
                await session.commit()
                await session.refresh(user)
            return user

    async def deactivate_user(self, username: str):
        async with self.db_client() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()
            if user:
                user.is_active = False
                await session.commit()
                await session.refresh(user)
            return user
