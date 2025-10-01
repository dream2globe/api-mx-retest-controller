import redis.asyncio as redis
from src.infrastructure.config import settings

# redis.asyncio를 사용하여 네이티브 비동기 연결 클라이언트를 생성합니다.
redis_conn = redis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)