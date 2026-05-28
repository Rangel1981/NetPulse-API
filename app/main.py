import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Importamos a classe de serviço e o router das rotas
from app.services.monitor import MonitorService
from app.routes.asset import router as asset_router

# Gerador de sessões assíncronas do banco de dados
from app.database import AsyncSessionLocal 


async def monitor_task():
    """
    Tarefa em segundo plano (Background Task) que roda um loop infinito
    executando a varredura dos ativos de 30 em 30 segundos.
    """
    print(" [NetPulse] Motor de monitoramento em segundo plano inicializado com sucesso!")
    
    while True:
        try:
            # Abrimos uma sessão assíncrona limpa e exclusiva para este ciclo
            async with AsyncSessionLocal() as session:
                # Dispara a verificação em lote dos ativos e salvamento no banco
                resultado = await MonitorService.run_monitoring_cycle(session)
                print(f" [NetPulse Log]: {resultado.get('message')}")
                
        except Exception as e:
            print(f" [NetPulse Erro] Falha crítica no ciclo de monitoramento: {e}")
        
        # A pausa inteligente que liberta o processador para atender os utilizadores
        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de Contexto (Lifespan) do FastAPI.
    Tudo o que está ANTES do 'yield' roda quando o servidor LIGA.
    Tudo o que está DEPOIS do 'yield' roda quando o servidor DESLIGA.
    """
    # 1. Quando o servidor liga, criamos a tarefa assíncrona em background
    bg_task = asyncio.create_task(monitor_task())
    
    yield  # Aqui é onde a API fica ativa e operacional para os utilizadores
    
    # 2. Quando o servidor desliga (Ctrl+C), cancelamos a tarefa
    print(" [NetPulse] Desligando o servidor, cancelando motor de monitoramento...")
    bg_task.cancel()


# INSTÂNCIA ÚNICA DA API: Inicializamos o FastAPI passando todas as configurações de uma vez só!
app = FastAPI(
    title="NetPulse",
    description="Sistema Assíncrono de Monitorização e Resiliência de Ativos de Rede",
    version="1.0.0",
    lifespan=lifespan
)

# INCLUSÃO DAS ROTAS: Agora elas estão ligadas à instância definitiva do app!
app.include_router(asset_router)


@app.get("/")
async def root():
    """
    Rota inicial de teste.
    """
    return {
        "status": "Online",
        "projeto": "NetPulse API",
        "mensagem": "O motor de monitoramento está a rodar nos bastidores!"
    }