from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel, create_engine, Session, UniqueConstraint

# Database setup
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
# "../database/inventory.db" relative to backend/models.py
sqlite_file_name = os.path.join(current_dir, "../database/inventory.db")
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

class HomeopathicMedicine(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("medicine_name", "potency", "form", "bottle_size", "manufacturer", "batch_number", name="unique_medicine_sku"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    medicine_name: str = Field(index=True)
    potency: str = Field(index=True)  # e.g., "30C", "200C"
    form: str = Field(default="Dilution") # e.g., "Dilution", "Globules"
    bottle_size: str = Field(default="30ml") # e.g., "10ml", "30ml"
    manufacturer: str = Field(default="Dr. Reckeweg")
    batch_number: str = Field(index=True)
    expiry_date: date
    mrp: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    purchase_price: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    quantity: int = Field(default=0)
    low_stock_threshold: int = Field(default=5)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    medicine_id: int = Field(foreign_key="homeopathicmedicine.id")
    change_amount: int
    action_type: str = Field(default="ADJUST") # ADD, SELL, ADJUST, EXPIRE
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    note: Optional[str] = Field(default=None)
