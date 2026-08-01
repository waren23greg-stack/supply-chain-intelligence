from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    String, Integer, Float, ForeignKey, DateTime, Boolean
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)

class Base(DeclarativeBase):
    pass

class SupplierTable(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    historical_otif_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.90)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    geopolitical_risk_index: Mapped[float] = mapped_column(Float, nullable=False, default=0.20)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )

    # One-to-Many Relationship with ERP Inventory SKUs
    skus: Mapped[List["ERPInventoryTable"]] = relationship(
        "ERPInventoryTable", 
        back_populates="primary_supplier",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Supplier(code='{self.supplier_code}', name='{self.name}', otif={self.historical_otif_rate})>"

class ERPInventoryTable(Base):
    __tablename__ = "erp_inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    daily_burn_rate: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    in_transit_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, default=150)
    
    # Foreign Key Linking to SupplierTable
    primary_supplier_code: Mapped[str] = mapped_column(
        String(50), 
        ForeignKey("suppliers.supplier_code"), 
        nullable=False
    )
    
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationship Back to Supplier
    primary_supplier: Mapped["SupplierTable"] = relationship(
        "SupplierTable", 
        back_populates="skus"
    )

    def __repr__(self) -> str:
        return f"<ERPInventory(sku='{self.sku}', stock={self.current_stock}, burn={self.daily_burn_rate})>"
