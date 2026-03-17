from redis import asyncio as aioredis
from src.config import Config

JTI_EXPIRY = 3600

# token_blocklist = aioredis.StrictRedis(
#     host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0
# )

token_blocklist = aioredis.from_url(Config.REDIS_URL)


async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)

async def token_in_blocklsit(jti:str)->bool:
    jti = await token_blocklist.get(jti)

    return jti is not None
