import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings

client = AsyncIOMotorClient(settings.DATABASE_URL, tlsCAFile=certifi.where())
parsed_db_name = settings.DATABASE_URL.rsplit('/', 1)[-1].split('?')[0] if '/' in settings.DATABASE_URL.split('://')[-1] else ''
db_name = parsed_db_name if parsed_db_name else 'bugmind'
db = client[db_name]

async def get_db():
    yield db
