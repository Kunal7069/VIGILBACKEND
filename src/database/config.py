# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# from src.database.models.video import Base

# DATABASE_URL = "postgresql://neondb_owner:npg_DGL9OJy6QIjv@ep-wild-base-a8o648s7-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"

# engine = create_async_engine(DATABASE_URL, echo=True)

# AsyncSessionLocal = sessionmaker(
#     bind=engine,
#     expire_on_commit=False,
#     class_=AsyncSession
# )

# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session

# # Function to initialize tables
# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse, urlunparse, parse_qs
import ssl
from src.database.models.video import Base

# Original URL (psycopg2 by default)
original_url = "postgresql://neondb_owner:npg_DGL9OJy6QIjv@ep-wild-base-a8o648s7-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"

# Parse and fix the scheme to use asyncpg
parsed = urlparse(original_url)

# Change the scheme to asyncpg
async_url = parsed._replace(scheme="postgresql+asyncpg")

# Remove sslmode query
qs = parse_qs(parsed.query)
qs.pop('sslmode', None)
query = "&".join(f"{key}={value[0]}" for key, value in qs.items())

# Rebuild the URL
clean_url = urlunparse(async_url._replace(query=query))

# Setup SSL context
import ssl
ssl_context = ssl.create_default_context()

# Create async engine
engine = create_async_engine(
    clean_url,
    echo=True,
    connect_args={"ssl": ssl_context}
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
