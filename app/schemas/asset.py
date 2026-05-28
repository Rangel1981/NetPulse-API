from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AssetBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    ip_address: str = Field(..., description="Endereco IP ou alvo do dispositivo")

class AssetCreate(AssetBase):
    pass

class AssetResponse(BaseModel):
    id: int
    name: str
    type: str
    target: str = Field(..., description="Mapeia a coluna target do banco de dados")
    interval_minutes: int
    is_active: bool
    created_at: datetime

    # Mantem a compatibilidade para quem consome a API ler como ip_address
    @property
    def ip_address(self) -> str:
        return self.target

    class Config:
        from_attributes = True