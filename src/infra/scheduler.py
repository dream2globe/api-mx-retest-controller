from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.application.services import update_target_inspectors_job
from src.infrastructure.config import settings
import logging

logging.getLogger('apscheduler').setLevel(logging.WARNING)

scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
scheduler.add_job(
    update_target_inspectors_job,
    'interval',
    minutes=settings.INSPECTOR_UPDATE_INTERVAL,
    id="update_inspectors_job",
    replace_existing=True
)