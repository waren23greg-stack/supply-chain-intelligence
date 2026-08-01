import os
import logging
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from data_pipeline.models import Base, SupplierTable, ERPInventoryTable

# Configure standard logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SupplyChainIngestion")

# Default connection string falls back to local PostgreSQL or SQLite for quick testing
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://postgres:postgres@localhost:5432/supply_chain_db"
)

# Initialize SQLAlchemy Engine & Session
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """
    Creates all relational tables in the target database if they don't already exist.
    """
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables successfully created/verified.")

def get_sample_suppliers() -> list[dict]:
    return [
        {
            "supplier_code": "SUP-TWN-01",
            "name": "Taipei Silicon Precision",
            "country": "Taiwan",
            "historical_otif_rate": 0.78,
            "lead_time_days": 18,
            "geopolitical_risk_index": 0.65,
        },
        {
            "supplier_code": "SUP-GER-02",
            "name": "Bavarian Industrial Drives",
            "country": "Germany",
            "historical_otif_rate": 0.96,
            "lead_time_days": 10,
            "geopolitical_risk_index": 0.15,
        },
        {
            "supplier_code": "SUP-VNM-03",
            "name": "Mekong Electronics Assembly",
            "country": "Vietnam",
            "historical_otif_rate": 0.85,
            "lead_time_days": 24,
            "geopolitical_risk_index": 0.40,
        },
        {
            "supplier_code": "SUP-MEX-04",
            "name": "Monterrey Stamping & Wire",
            "country": "Mexico",
            "historical_otif_rate": 0.91,
            "lead_time_days": 7,
            "geopolitical_risk_index": 0.25,
        }
    ]

def get_sample_inventory() -> list[dict]:
    return [
        {
            "sku": "IC-ARM-992",
            "name": "Automotive Microcontroller Unit",
            "current_stock": 1200,
            "daily_burn_rate": 80,
            "in_transit_qty": 400,
            "reorder_point": 1440,
            "primary_supplier_code": "SUP-TWN-01"
        },
        {
            "sku": "DRV-SRV-104",
            "name": "High-Torque Precision Servo",
            "current_stock": 450,
            "daily_burn_rate": 15,
            "in_transit_qty": 0,
            "reorder_point": 200,
            "primary_supplier_code": "SUP-GER-02"
        },
        {
            "sku": "PCB-MAIN-88",
            "name": "Main Controller Circuit Board",
            "current_stock": 310,
            "daily_burn_rate": 40,
            "in_transit_qty": 500,
            "reorder_point": 960,
            "primary_supplier_code": "SUP-VNM-03"
        },
        {
            "sku": "WIR-HAR-09",
            "name": "Heavy Duty Engine Wiring Harness",
            "current_stock": 2200,
            "daily_burn_rate": 110,
            "in_transit_qty": 1000,
            "reorder_point": 1500,
            "primary_supplier_code": "SUP-MEX-04"
        }
    ]

def seed_database(db: Optional[Session] = None) -> None:
    """
    Upserts sample supplier and ERP inventory records into PostgreSQL.
    """
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        logger.info("Starting supplier data ingestion...")
        for supplier_data in get_sample_suppliers():
            stmt = select(SupplierTable).where(
                SupplierTable.supplier_code == supplier_data["supplier_code"]
            )
            existing_supplier = db.execute(stmt).scalar_one_or_none()

            if existing_supplier:
                for key, value in supplier_data.items():
                    setattr(existing_supplier, key, value)
            else:
                new_supplier = SupplierTable(**supplier_data)
                db.add(new_supplier)

        db.commit()
        logger.info("Supplier table successfully seeded.")

        logger.info("Starting ERP inventory data ingestion...")
        for sku_data in get_sample_inventory():
            stmt = select(ERPInventoryTable).where(
                ERPInventoryTable.sku == sku_data["sku"]
            )
            existing_sku = db.execute(stmt).scalar_one_or_none()

            if existing_sku:
                for key, value in sku_data.items():
                    setattr(existing_sku, key, value)
            else:
                new_sku = ERPInventoryTable(**sku_data)
                db.add(new_sku)

        db.commit()
        logger.info("ERP inventory table successfully seeded.")

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to ingest data: {str(e)}")
        raise
    finally:
        if close_session:
            db.close()

if __name__ == "__main__":
    init_db()
    seed_database()
    logger.info("Database ingestion pipeline completed successfully.")
