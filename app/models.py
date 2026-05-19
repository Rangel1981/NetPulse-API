from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, BigInteger, Float, Integer, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False) # PING, HTTP, PORT
    target: Mapped[str] = mapped_column(String(255), nullable=False)  # IP, URL, etc.
    interval_minutes: Mapped[int] = mapped_column(Integer, default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relacionamentos (Para o SQLAlchemy conseguir buscar dados interligados facilmente)
    logs: Mapped[List["UptimeLog"]] = relationship("UptimeLog", back_populates="asset", cascade="all, delete-orphan")
    alert_config: Mapped[Optional["AlertConfig"]] = relationship("AlertConfig", back_populates="asset", uselist=False)

class UptimeLog(Base):
    __tablename__ = "uptime_logs"

    # BigInteger porque essa tabela vai ter milhões de registros com o tempo
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, nullable=False)
    response_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relacionamento reverso
    asset: Mapped["Asset"] = relationship("Asset", back_populates="logs")


class AlertConfig(Base):
    __tablename__ = "alert_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)  # TELEGRAM, DISCORD
    webhook_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Relacionamento reverso
    asset: Mapped["Asset"] = relationship("Asset", back_populates="alert_config")