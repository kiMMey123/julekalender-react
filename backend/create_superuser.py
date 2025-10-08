import asyncio
from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, MetaData, String, Table, insert, select

from app.settings import settings
from app.database import AsyncSession, async_engine, local_session
from app.utils.security import get_password_hash, generate_uid
from app.models.user import User


async def create_first_user(session: AsyncSession) -> None:
    try:
        name = settings.ADMIN_NAME
        email = settings.ADMIN_EMAIL
        username = settings.ADMIN_USERNAME
        hashed_password = get_password_hash(settings.ADMIN_PASSWORD)

        query = select(User).filter_by(email=email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            metadata = MetaData()
            user_table = Table(
                "user",
                metadata,
                Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
                Column("name", String(50), nullable=False),
                Column("username", String(30), nullable=False, unique=True, index=True),
                Column("email", String(50), nullable=False, unique=True, index=True),
                Column("hashed_password", String, nullable=False),
                Column("name_show", Boolean, nullable=False, default=False),
                Column("email_show", Boolean, nullable=False, default=False),
                Column("uuid", String, default=generate_uid()),
                Column("is_admin", Boolean, default=False),
                Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False),
                Column("updated_at", DateTime),
                Column("deleted_at", DateTime),
                Column("is_deleted", Boolean, default=False, index=True),
            )

            data = {
                "name": name,
                "email": email,
                "username": username,
                "hashed_password": hashed_password,
                "is_admin": True,
            }

            stmt = insert(user_table).values(data)
            async with async_engine.connect() as conn:
                await conn.execute(stmt)
                await conn.commit()

            print(f"Admin user {username} created successfully.")

        else:
            print(f"Admin user {username} already exists.")

    except Exception as e:
        print(f"Error creating admin user: {e}")

async def main():
    async with local_session() as session:
        await create_first_user(session)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())