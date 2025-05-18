from app.core import async_engine
from app.db import Base
import asyncio


async def setup_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(setup_database(async_engine))
