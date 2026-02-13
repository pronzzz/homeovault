from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
import shutil
import os
import csv
import io
import webbrowser
from fastapi.responses import StreamingResponse

from .models import HomeopathicMedicine, Transaction, create_db_and_tables, get_session, engine

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to create tables and backup
current_dir = os.path.dirname(os.path.abspath(__file__))

@app.on_event("startup")
def on_startup():
    # 1. Create DB and Tables
    create_db_and_tables()
    
    # 2. Automatic Backup
    db_path = os.path.join(current_dir, "../database/inventory.db")
    backup_dir = os.path.join(current_dir, "../backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"inventory_backup_{timestamp}.db")
        try:
            shutil.copy2(db_path, backup_file)
            print(f"Backup created: {backup_file}")
            # Keep only last 10 backups to save space
            backups = sorted([os.path.join(backup_dir, f) for f in os.listdir(backup_dir)])
            if len(backups) > 10:
                for b in backups[:-10]:
                    os.remove(b)
        except Exception as e:
            print(f"Backup failed: {e}")

    # 3. Phase 7: Data Integrity Check
    try:
        with Session(engine) as session:
            # SQLModel doesn't expose raw connection easily for pragma, but we can execute text
            from sqlalchemy import text
            result = session.exec(text("PRAGMA integrity_check")).first()
            # Result might be a tuple ('ok',) or string "ok" depending on driver/version
            is_ok = result == "ok" or (isinstance(result, (tuple, list)) and result[0] == "ok")
            
            if not is_ok:
                print(f"CRITICAL: Database Integrity Check Failed: {result}")
            else:
                print("Database Integrity Check: OK")
    except Exception as e:
        print(f"Integrity Check Error: {e}")

    # 4. Phase 4: Startup Scan for Expiry/Health
    with Session(engine) as session:
        medicines = session.exec(select(HomeopathicMedicine)).all()
        expired = [m for m in medicines if m.expiry_date < date.today()]
        low_stock = [m for m in medicines if m.quantity <= m.low_stock_threshold]
        
        print(f"--- STARTUP HEALTH SCAN ---")
        print(f"Total Medicines: {len(medicines)}")
        print(f"Expired Batches: {len(expired)}")
        if expired:
            for m in expired:
                print(f"  [EXPIRED] {m.medicine_name} ({m.potency}) Batch: {m.batch_number} Exp: {m.expiry_date}")
        print(f"Low Stock Items: {len(low_stock)}")
        print(f"---------------------------")
    
    # 5. Launch Browser
    print("Launching Dashboard...")
    try:
        webbrowser.open("http://localhost:8000/index.html")
    except Exception as e:
        print(f"Could not open browser: {e}")

# API Endpoints

@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now()}

@app.get("/api/medicines", response_model=List[HomeopathicMedicine])
def read_medicines(session: Session = Depends(get_session)):
    medicines = session.exec(select(HomeopathicMedicine)).all()
    return medicines

@app.post("/api/medicines", response_model=HomeopathicMedicine)
def create_medicine(medicine: HomeopathicMedicine, session: Session = Depends(get_session)):
    # 1. Validate MRP and Price
    if medicine.mrp <= 0:
        raise HTTPException(status_code=400, detail="MRP must be greater than 0.")
    if medicine.purchase_price < 0:
        raise HTTPException(status_code=400, detail="Purchase Price cannot be negative.")
    if medicine.purchase_price > medicine.mrp:
        # Warn? For now, we'll allow it but it's suspicious. PRD "Prevent zero or negative pricing" is met.
        pass

    # 2. Validate Expiry (Warning context essentially, handled by Frontend predominantly, but we ensure it's a date)
    # If adding already expired medicine?
    # Ensure conversion if it comes as string (SQLModel/Pydantic quirk sometimes)
    exp_date = medicine.expiry_date
    if isinstance(exp_date, str):
        exp_date = datetime.strptime(exp_date, "%Y-%m-%d").date()
        medicine.expiry_date = exp_date

    if exp_date < date.today():
        # strict mode: might reject. PRD says "Warn". We'll allow it (maybe logging historical stock)
        pass

    # 3. Check for duplicates based on SKU fields
    statement = select(HomeopathicMedicine).where(
        HomeopathicMedicine.medicine_name == medicine.medicine_name,
        HomeopathicMedicine.potency == medicine.potency,
        HomeopathicMedicine.form == medicine.form,
        HomeopathicMedicine.bottle_size == medicine.bottle_size,
        HomeopathicMedicine.manufacturer == medicine.manufacturer,
        HomeopathicMedicine.batch_number == medicine.batch_number
    )
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=400, detail="Medicine with this Batch/SKU already exists.")

    session.add(medicine)
    session.commit()
    session.refresh(medicine)
    return medicine

@app.delete("/api/medicines/{medicine_id}")
def delete_medicine(medicine_id: int, session: Session = Depends(get_session)):
    medicine = session.get(HomeopathicMedicine, medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    session.delete(medicine)
    session.commit()
    return {"status": "success", "message": "Medicine deleted"}

@app.post("/api/transaction")
def create_transaction(transaction: Transaction, session: Session = Depends(get_session)):
    medicine = session.get(HomeopathicMedicine, transaction.medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    # Validation: Prevent negative stock
    if medicine.quantity + transaction.change_amount < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock. Cannot reduce below zero.")
    
    # Validation: Expiry Check on SELL
    if transaction.change_amount < 0: # Selling
        if medicine.expiry_date < date.today():
             # PRD: "Expired medicines must not be sellable without override confirmation."
             # We need a flag in transaction payload to override.
             # For now, we block it unless "note" contains "OVERRIDE"
             if not transaction.note or "OVERRIDE" not in transaction.note:
                 raise HTTPException(status_code=400, detail="Cannot sell expired medicine. Add 'OVERRIDE' to notes to force.")

    # Update inventory
    medicine.quantity += transaction.change_amount
    medicine.last_updated = datetime.utcnow()
    
    session.add(medicine)
    session.add(transaction)
    session.commit()
    return {"status": "success", "new_quantity": medicine.quantity}

@app.get("/api/history")
def read_history(session: Session = Depends(get_session)):
    # Join Transaction with HomeopathicMedicine to get names
    statement = select(Transaction, HomeopathicMedicine.medicine_name, HomeopathicMedicine.batch_number).join(HomeopathicMedicine).order_by(Transaction.timestamp.desc()).limit(50)
    results = session.exec(statement).all()
    
    # Format for frontend
    history = []
    for txn, name, batch in results:
        history.append({
            "id": txn.id,
            "medicine_name": name,
            "batch_number": batch,
            "change": txn.change_amount,
            "action_type": txn.action_type,
            "timestamp": txn.timestamp,
            "note": txn.note
        })
    return history

@app.get("/api/export")
def export_csv(session: Session = Depends(get_session)):
    medicines = session.exec(select(HomeopathicMedicine)).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID', 'Name', 'Potency', 'Form', 'Size', 'Manufacturer', 
        'Batch', 'Expiry', 'MRP', 'Purchase Price', 'Quantity'
    ])
    
    for m in medicines:
        writer.writerow([
            m.id, m.medicine_name, m.potency, m.form, m.bottle_size, 
            m.manufacturer, m.batch_number, m.expiry_date, m.mrp, 
            m.purchase_price, m.quantity
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory_export.csv"}
    )

# Mount static files (Frontend)
frontend_dir = os.path.join(current_dir, "../frontend")
if not os.path.exists(frontend_dir):
    frontend_dir = "frontend"

app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
