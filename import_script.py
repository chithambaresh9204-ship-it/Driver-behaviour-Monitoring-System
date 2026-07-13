"""
Simple script to create drivers and import data
Run this once before using the app
"""
import pandas as pd
from auth import AuthManager
from database import db
from datetime import datetime
import bcrypt

# Create 10 drivers
drivers_list = [
    ("driver1@gmail.com", "Suresh", "DL001"),
    ("driver2@gmail.com", "Navin", "DL002"),
    ("driver3@gmail.com", "Prakash", "DL003"),
    ("driver4@gmail.com", "Kumaravelu", "DL004"),
    ("driver5@gmail.com", "Depak", "DL005"),
    ("driver6@gmail.com", "Manish", "DL006"),
    ("driver7@gmail.com", "Balaji", "DL007"),
    ("driver8@gmail.com", "Aeholi", "DL008"),
    ("driver9@gmail.com", "Satheesh", "DL009"),
    ("driver10@gmail.com", "Harish", "DL010"),
]

driver_mapping = {}

print("Creating drivers...")
for email, name, license_no in drivers_list:
    existing = db.get_user_by_email(email)
    if not existing:
        password_hash = bcrypt.hashpw("Password123!".encode(), bcrypt.gensalt()).decode()
        user_id = db.add_user(email, password_hash, name, 'driver')
        if user_id:
            drv_id = f"DRV{user_id:06d}"
            db.add_driver(
                driver_id=drv_id,
                user_id=user_id,
                phone="9876543210",
                license_no=license_no,
                license_exp=None,
                dob=None,
                address="India",
                join_date=datetime.now().strftime('%Y-%m-%d')
            )
            driver_mapping[name] = drv_id
            print(f"✓ Created {name} ({email}) -> {drv_id}")
    else:
        drv_id = f"DRV{existing[0]:06d}"
        driver_mapping[name] = drv_id
        print(f"  Already exists: {name} ({email}) -> {drv_id}")

print(f"\n✓ Created {len(driver_mapping)} drivers\n")

# Import data
print("Importing data...")
try:
    df = pd.read_csv('final_dataset.csv')
    print(f"Loaded {len(df)} records from CSV")
    
    def calculate_risk_level(score):
        if score >= 85:
            return 'Very Low'
        elif score >= 70:
            return 'Low'
        elif score >= 55:
            return 'Medium'
        else:
            return 'High'
    
    # Create reverse mapping (driver_name -> drv_id)
    reverse_mapping = {v.split('_')[-1]: drv_id for v, drv_id in driver_mapping.items()}
    
    imported = 0
    for _, row in df.iterrows():
        csv_driver_id = str(row['driver_id']).strip()
        driver_name = str(row['driver_name']).strip()
        month_year = str(row['month']).strip()
        
        # Try to find matching driver
        drv_id = None
        for name, mapped_id in driver_mapping.items():
            if name.lower() in driver_name.lower() or driver_name.lower() in name.lower():
                drv_id = mapped_id
                break
        
        if not drv_id:
            continue
        
        overall_score = int((min(100, int(row['avg_speed'])) + 
                           min(100, max(0, 100 - (row['harsh_acceleration_count'] * 10))) +
                           min(100, max(0, 100 - (row['harsh_braking_count'] * 10))) +
                           min(100, max(0, 100 - (row['sharp_turn_count'] * 10))) +
                           min(100, max(0, 100 - (row['fatigue_score']))) +
                           min(100, max(0, 100 - (row['distraction_events'] * 15)))) / 6)
        
        risk_level = calculate_risk_level(overall_score)
        
        db.add_monthly_score(
            driver_id=drv_id,
            month_year=month_year,
            overall_score=overall_score,
            speed=min(100, int(row['avg_speed'])),
            focus=min(100, max(0, 100 - (row['distraction_events'] * 15))),
            braking=min(100, max(0, 100 - (row['harsh_braking_count'] * 10))),
            turning=min(100, max(0, 100 - (row['sharp_turn_count'] * 10))),
            risk_level=risk_level,
            incidents=int(row['harsh_acceleration_count'] + row['harsh_braking_count']),
            miles=int(row['trip_duration_minutes']),
            avg_speed=int(row['avg_speed'])
        )
        imported += 1
    
    print(f"✓ Imported {imported} records\n")
    print("✓ Setup complete! You can now run: streamlit run app.py")
    
except Exception as e:
    print(f"Error: {e}")