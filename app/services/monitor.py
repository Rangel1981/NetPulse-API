import sys
import asyncio
from datetime import datetime
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import Asset, UptimeLog, AlertConfig

class MonitorService:

    @staticmethod
    async def send_telegram_alert(webhook_url: str, asset_name: str, target: str):
        """
        Envia uma notificacao para o Telegram usando a URL do webhook cadastrada.
        """
        mensagem = f"🚨 *Alerta NetPulse* 🚨\n\nO ativo *{asset_name}* ({target}) acabou de cair ou nao esta respondendo aos pings!"
        
        payload = {
            "text": mensagem,
            "parse_mode": "Markdown"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                resposta = await client.post(webhook_url, json=payload, timeout=5.0)
                if resposta.status_code == 200:
                    print(f" -> Alerta enviado com sucesso para o Telegram do ativo: {asset_name}")
                else:
                    print(f" -> Erro ao enviar alerta (Status {resposta.status_code}): {resposta.text}")
        except Exception as e:
            print(f" -> Falha ao conectar na API do Telegram: {e}")

    @staticmethod
    async def ping_asset(target: str) -> dict:
        """
        Executa o comando de ping no sistema operacional de forma assincrona.
        """
        param = "-n" if sys.platform.lower() == "win32" else "-c"
        start_time = datetime.utcnow()
        
        try:
            process = await asyncio.create_subprocess_exec(
                "ping", param, "1", target,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await process.wait()
            
            end_time = datetime.utcnow()
            response_time = round((end_time - start_time).total_seconds() * 1000, 2)
            
            if process.returncode == 0:
                return {"is_online": True, "response_time_ms": response_time, "error_message": None}
            else:
                return {"is_online": False, "response_time_ms": 0.0, "error_message": "Sem resposta do ping"}
                
        except Exception as e:
            return {"is_online": False, "response_time_ms": 0.0, "error_message": str(e)}

    @staticmethod
    async def run_monitoring_cycle(db: AsyncSession) -> dict:
        """
        Busca todos os ativos e traz junto as configuracoes de alerta de cada um.
        """
        # selectinload garante que o SQLAlchemy busque a tabela associada alert_config de forma assincrona
        query = select(Asset).where(Asset.is_active == True).options(selectinload(Asset.alert_config))
        result = await db.execute(query)
        assets = result.scalars().all()

        if not assets:
            return {"status": "success", "message": "Nenhum ativo cadastrado para monitorar."}

        for asset in assets:
            if asset.type == "PING":
                res = await MonitorService.ping_asset(asset.target)
                
                log = UptimeLog(
                    asset_id=asset.id,
                    is_online=res["is_online"],
                    response_time_ms=res["response_time_ms"],
                    error_message=res["error_message"],
                    tested_at=datetime.utcnow()
                )
                db.add(log)

                # Se o ativo estiver offline e possuir uma configuracao de alerta criada
                if not res["is_online"] and asset.alert_config:
                    if asset.alert_config.platform == "TELEGRAM":
                        # Dispara o alerta sem travar o loop usando asyncio.create_task
                        asyncio.create_task(
                            MonitorService.send_telegram_alert(
                                webhook_url=asset.alert_config.webhook_url,
                                asset_name=asset.name,
                                target=asset.target
                            )
                        )
        
        await db.commit()
        return {"status": "success", "message": f"Ciclo finalizado. {len(assets)} ativos verificados."}