from fastapi import FastAPI
from redis.exceptions import ResponseError

from src.api.endpoints import router as api_router
from src.infrastructure.scheduler import scheduler
from src.infrastructure.database import redis_conn
from src.domain.models import Inspector, DefectRate

app = FastAPI(
    title="재검사 판단 API",
    description="Redis에 캐싱한 재검사 분석 결과를 읽어서 검사기의 요청에 따라 재검사 필요 여부를 판단하는 API",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    # Redis 연결 확인
    try:
        await redis_conn.ping()
        print("Successfully connected to Redis.")
    except Exception as e:
        print(f"Could not connect to Redis: {e}")
        # 실제 프로덕션에서는 여기서 앱을 종료시키는 로직이 필요할 수 있습니다.

    # RediSearch 인덱스 생성 (비동기 실행)
    try:
        await Inspector.Meta.database.execute_command("FT.CREATE", Inspector.Meta.index_name, "ON", "HASH", "PREFIX", "1", f"{Inspector.Meta.model_key_prefix}:", "SCHEMA", "ip_address", "TAG")
        await DefectRate.Meta.database.execute_command("FT.CREATE", DefectRate.Meta.index_name, "ON", "HASH", "PREFIX", "1", f"{DefectRate.Meta.model_key_prefix}:", "SCHEMA", "product_model", "TAG", "retest_info", "TAG")
    except ResponseError as e:
        if "Index already exists" in str(e): print("RediSearch index already exists.")
        else:
            raise e
    
    scheduler.start()
    print("APScheduler (AsyncIO) started...")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    await redis_conn.close()
    print("APScheduler and Redis connection closed.")

app.include_router(api_router)