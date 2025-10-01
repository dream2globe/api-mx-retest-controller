from fastapi import APIRouter, status, HTTPException
from aredis_om import NotFoundError

from src.application import services
from src.domain.models import Inspector, DefectRate
from src.domain.schemas import (
    ReinspectionCheckRequest, ReinspectionCheckResponse,
    InspectorCreate, DefectRateCreate
)

router = APIRouter()

@router.post("/reinspection/check", response_model=ReinspectionCheckResponse, tags=["Re-inspection"])
async def check_reinspection(request: ReinspectionCheckRequest):
    return await services.check_reinspection_logic(request)

@router.post("/manage/inspectors", response_model=Inspector, status_code=status.HTTP_201_CREATED, tags=["Data Management"])
async def create_or_update_inspector(inspector_data: InspectorCreate):
    inspector = Inspector(**inspector_data.model_dump())
    await inspector.save()
    return inspector

@router.post("/manage/defects", response_model=DefectRate, status_code=status.HTTP_201_CREATED, tags=["Data Management"])
async def create_or_update_defect_rate(defect_data: DefectRateCreate):
    pk_value = f"{defect_data.product_model}:{defect_data.defect_item}"
    defect = DefectRate(pk=pk_value, **defect_data.model_dump())
    await defect.save()
    return defect

@router.get("/manage/defects/{pk}", response_model=DefectRate, tags=["Data Management"])
async def get_defect_rate_by_pk(pk: str):
    try:
        return await DefectRate.get(pk)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="DefectRate not found.")