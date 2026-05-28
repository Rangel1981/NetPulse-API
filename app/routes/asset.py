from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.models import Asset
from app.schemas.asset import AssetCreate, AssetResponse
from app.database import AsyncSessionLocal

router = APIRouter(
    prefix="/assets",
    tags=["Ativos"]
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(asset_data: AssetCreate, db: AsyncSession = Depends(get_db)):
    # Busca o ativo na coluna 'target' utilizando o valor recebido
    query = select(Asset).where(Asset.target == asset_data.ip_address)
    result = await db.execute(query)
    existing_asset = result.scalar_one_or_none()

    if existing_asset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ja existe um ativo cadastrado com este endereco/IP."
        )

    # Mapeia os campos recebidos para as colunas reais do modelo Asset
    new_asset = Asset(
        name=asset_data.name,
        target=asset_data.ip_address,
        type="PING",
        interval_minutes=5,
        is_active=True
    )

    db.add(new_asset)
    await db.commit()
    await db.refresh(new_asset)
    return new_asset

@router.get("/", response_model=List[AssetResponse])
async def list_assets(db: AsyncSession = Depends(get_db)):
    query = select(Asset).order_by(Asset.id.desc())
    result = await db.execute(query)
    assets = result.scalars().all()
    return assets

@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Asset).where(Asset.id == asset_id)
    result = await db.execute(query)
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ativo nao encontrado."
        )

    await db.delete(asset)
    await db.commit()
    return None