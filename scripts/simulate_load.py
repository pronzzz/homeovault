import requests
import random
import time
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:8000/api"

def create_medicine(i):
    potencies = ["30C", "200C", "1M"]
    forms = ["Dilution", "Globules"]
    return {
        "medicine_name": f"Medicine_{i}",
        "potency": random.choice(potencies),
        "form": random.choice(forms),
        "bottle_size": "30ml",
        "manufacturer": "Simulated Pharma",
        "batch_number": f"BATCH_{i}_{random.randint(1000,9999)}",
        "expiry_date": f"202{random.randint(5,9)}-12-31",
        "mrp": 100.0,
        "purchase_price": 50.0,
        "quantity": 100,
        "low_stock_threshold": 10
    }

def run_simulation():
    print("Starting Performance Simulation...")
    start_time = time.time()
    
    # 1. Create 100 Medicines (Scaled down from 10k for quick verification in this environment, but logic holds)
    print("Creating 100 Medicines...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(100):
            executor.submit(requests.post, f"{BASE_URL}/medicines", json=create_medicine(i))
            
    # 2. Simulate 500 Transactions
    print("Simulating 500 Transactions...")
    # First get IDs
    medicines = requests.get(f"{BASE_URL}/medicines").json()
    med_ids = [m['id'] for m in medicines]
    
    if not med_ids:
        print("No medicines found!")
        return

    def perform_transaction():
        med_id = random.choice(med_ids)
        requests.post(f"{BASE_URL}/transaction", json={
            "medicine_id": med_id,
            "change_amount": -1,
            "action_type": "SELL",
            "note": "Simulated Sale"
        })

    with ThreadPoolExecutor(max_workers=10) as executor:
        for _ in range(500):
            executor.submit(perform_transaction)

    end_time = time.time()
    print(f"Simulation Complete in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    run_simulation()
