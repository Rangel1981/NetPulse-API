from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Cria o motor (engine) assíncrono para o PostgreSQL
# O pool_pre_ping=True ajuda a recuperar a conexão caso o banco caia temporariamente
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=False)

# Cria a fábrica de sessões assíncronas
# Cada requisição à nossa API terá a sua própria sessão isolada
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False # Evita problemas de carregamento preguiçoso (lazy loading)  
)

# Classe Base para os nossos futuros Modelos (Tabelas)
class Base(DeclarativeBase):
    pass

# Função Dependência (Dependency Injection) que o FastAPI vai usar
# Ela garante que a sessão do banco abra quando a requisição chega e feche quando termina

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
             