import logging
from fastapi import HTTPException, status
from aredis_om import NotFoundError

from src.domain.models import Inspector, DefectRate
from src.domain.schemas import ReinspectionCheckRequest, ReinspectionCheckResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_reinspection_logic(request: ReinspectionCheckRequest) -> ReinspectionCheckResponse:
    """네이티브 비동기 I/O를 사용하는 재검사 판단 로직"""
    try:
        # run_in_threadpool 없이 바로 await 사용
        inspector = await Inspector.get(request.inspector_ip)
        if not inspector.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Inspector IP({request.inspector_ip}) is not active.")
    except NotFoundError:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Inspector IP({request.inspector_ip}) not found.")

    try:
        defect_pk = f"{request.product_model}:{request.defect_code}"
        defect_data = await DefectRate.get(defect_pk)
    except NotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Defect data not found for PK: {defect_pk}")

    retest_remove = (defect_data.total_inspections >= request.min_inspection_criteria and
                     defect_data.reproducibility_rate >= request.reproducibility_criteria)

    return ReinspectionCheckResponse(reproducibility_rate=defect_data.reproducibility_rate, retest_remove=retest_remove)

async def update_target_inspectors_job():
    """스케줄러에서 실행될 비동기 배치 작업"""
    logger.info("[BATCH JOB] Starting: update_target_inspectors")
    
    source_data = [
        {"ip_address": "192.168.1.10", "is_active": True, "factory_code": "F001", "line_name": "L01", "inspection_name": "AOI-01"},
        {"ip_address": "192.168.1.12", "is_active": True, "factory_code": "F001", "line_name": "L02", "inspection_name": "SPI-01"},
    ]
    active_ips_from_source = {d["ip_address"] for d in source_data if d.get("is_active")}
    
    # .find().all() 호출도 비동기로 처리
    all_inspectors_in_redis = await Inspector.find().all()
    
    for inspector in all_inspectors_in_redis:
        should_be_active = inspector.ip_address in active_ips_from_source
        if inspector.is_active != should_be_active:
            inspector.is_active = should_be_active
            await inspector.save() # .save() 호출도 비동기로 처리
            status_text = "ACTIVATED" if should_be_active else "DEACTIVATED"
            logger.info(f"[BATCH JOB] Inspector {inspector.ip_address} has been {status_text}.")
            
    logger.info("[BATCH JOB] Finished: update_target_inspectors")