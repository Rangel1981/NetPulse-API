from models import Asset, UptimeLog
import sys
import asyncio
from datetime import datetime, timezone
from sqlalchemy import AsyncSession 
from sqlalchemy import select

class MonitorService:

    @staticmethod
    async def ping_asset(ip_address: str):
        if sys.platform.lower() == "win32":
            param = "-n"
        else:
            param = "-c"

        
        start_time = datetime.now()
        
        try:
            
            process = await asyncio.create_subprocess_exec(
                "ping", param, "1", ip_address,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await asyncio.wait_for(process.wait(), timeout=3.0)
            end_time = datetime.now()
            latencia = (end_time - start_time).total_seconds() * 1000
            latencia = round(latencia, 2)
            if process.returncode == 0:
                return True, latencia

            else:
                return False, 0.0

        except:
            return False, 0.0

    @classmethod
    async def run_monitoring_cycle(cls, db: AsyncSession):
        result = await db.execute(select(Asset))
        assets = result.scalars().all()

        if not assets:
            return {"message": "Nenhum ativo cadastrado para monitorar."}
    
        tasks = [cls.ping_asset(asset.ip_address) for asset in assets]
        results = await asyncio.gather(*tasks)

        for asset, (is_online, response_time) in zip(assets, results):
            log = UptimeLog(asset_id=asset.id, is_online=is_online, response_time=response_time, checked_at=datetime.now(timezone.utc))
            db.add(log)
            asset.last_status = "online" if is_online else "offline"
            asset.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        return {"message": f"Ciclo finalizado. {len(assets)} ativos verificados com sucesso."}
