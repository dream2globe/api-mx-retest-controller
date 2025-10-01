from pydantic import BaseModel, Field

class ReinspectionCheckRequest(BaseModel):
    inspector_ip: str = Field(..., examples=["192.168.1.10"], description="검사기 IP 주소")
    product_model: str = Field(..., examples=["MODEL-ABC"], description="제품 모델명")
    defect_code: str = Field(..., examples=["VI-001"], description="불량 항목 코드")
    min_inspection_criteria: int = Field(..., examples=[100], description="재현율 판단을 위한 최소 검사 수")
    reproducibility_criteria: float = Field(
        ..., ge=0.0, le=1.0, examples=[0.95], description="재검사 제외 판단을 위한 재현율 임계값"
    )

class ReinspectionCheckResponse(BaseModel):
    reproducibility_rate: float = Field(..., examples=[0.92], description="조회된 불량 항목의 재현율")
    retest_remove: bool = Field(..., description="재검사 목록에서 제외(제거)할지 여부. True이면 재검사 불필요 추천.")

class InspectorCreate(BaseModel):
    ip_address: str = Field(..., examples=["192.168.1.10"])
    is_active: bool = Field(True, examples=[True]) 
    factory_code: str = Field(..., examples=["F001"])
    line_name: str = Field(..., examples=["L01"])
    inspection_name: str = Field(..., examples=["AOI-01"])

class DefectRateCreate(BaseModel):
    factory_code: str = Field(..., examples=["F001"])
    process_code: str = Field(..., examples=["P005"])
    product_model: str = Field(..., examples=["MODEL-ABC"])
    defect_item: str = Field(..., examples=["VI-001"])
    reproducibility_rate: float = Field(..., ge=0.0, le=1.0, examples=[0.92])
    total_inspections: int = Field(..., examples=[150])
    reproduced_count: int = Field(..., examples=[138])