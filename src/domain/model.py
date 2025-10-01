from aredis_om import HashModel, Field
from src.infrastructure.database import redis_conn

class Inspector(HashModel):
    ip_address: str = Field(primary_key=True, index=True)
    is_active: bool = Field(default=True)
    factory_code: str
    line_name: str
    inspection_name: str

    class Meta:
        database = redis_conn
        model_key_prefix = "inspector"

class DefectRate(HashModel):
    factory_code: str
    process_code: str
    product_model: str = Field(index=True)
    defect_item: str = Field(index=True)
    reproducibility_rate: float
    total_inspections: int
    reproduced_count: int

    class Meta:
        database = redis_conn
        model_key_prefix = "retest_info"