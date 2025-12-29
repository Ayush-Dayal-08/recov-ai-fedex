import csv
import random
import os

# Define file paths
# We use 'backend/data' if running from main folder, or just 'data' if inside backend
base_dir = "data" 
if not os.path.exists(base_dir):
    os.makedirs(base_dir)

# --- 1. Generate Training Data (500 Rows) ---
print("Generating 500 rows for training_data.csv...")

headers = [
    'account_id', 'company_name', 'industry', 'amount', 'days_overdue', 
    'payment_history_score', 'shipment_volume_30d', 'shipment_volume_change_30d', 
    'express_ratio', 'destination_diversity', 'email_opened', 
    'contact_attempts', 'dispute_flag', 'customer_tenure_months', 'region', 'outcome'
]

industries = ['Manufacturing', 'Retail', 'E-commerce', 'Healthcare', 'Construction', 'Technology', 'Textile']
regions = ['North', 'South', 'East', 'West', 'Central']

training_rows = []
for i in range(500):
    row = [
        f'ACC{i+1000}',                 # account_id
        f'Company_{i}',                 # company_name
        random.choice(industries),      # industry
        random.randint(5000, 5000000),  # amount
        random.randint(10, 180),        # days_overdue
        round(random.uniform(0.0, 1.0), 2), # payment_history_score
        random.randint(0, 200),         # shipment_volume_30d
        round(random.uniform(-0.6, 0.8), 2), # shipment_volume_change_30d
        round(random.uniform(0.0, 1.0), 2),  # express_ratio
        random.randint(1, 50),          # destination_diversity
        random.choice([True, False]),   # email_opened
        random.randint(0, 10),          # contact_attempts
        random.choice([True, False]),   # dispute_flag
        random.randint(3, 120),         # customer_tenure_months
        random.choice(regions),         # region
        random.choice([0, 1])           # outcome
    ]
    training_rows.append(row)

# Save Training Data
with open(f'{base_dir}/training_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(training_rows)
print(f"✅ Created {base_dir}/training_data.csv with 500 rows.")


# --- 2. Generate Demo Data (With HERO Account) ---
print("Generating demo_data.csv with Hero Account...")

# The "Hero" Account (ACC0001) - EXACTLY as required by the audit
hero_row = [
    'ACC0001', 'TechCorp Solutions Pvt Ltd', 'Technology', 2800000, 90, 
    0.88, 45, 0.40, 0.65, 18, True, 3, False, 36, 'South', 1
]

demo_rows = [hero_row]

# Add 14 random rows
for i in range(14):
    demo_rows.append([
        f'ACC{i+2000}',                 # account_id
        f'Demo_Client_{i}',             # company_name
        random.choice(industries),      # industry
        random.randint(10000, 1000000), # amount
        random.randint(10, 60),         # days_overdue
        round(random.uniform(0.5, 0.9), 2), # payment_history_score
        random.randint(10, 100),        # shipment_volume_30d
        round(random.uniform(-0.1, 0.2), 2), # shipment_volume_change_30d
        round(random.uniform(0.2, 0.8), 2),  # express_ratio
        random.randint(5, 20),          # destination_diversity
        random.choice([True, False]),   # email_opened
        random.randint(1, 5),           # contact_attempts
        False,                          # dispute_flag
        random.randint(12, 60),         # customer_tenure_months
        random.choice(regions),         # region
        0                               # outcome placeholder
    ])

# Save Demo Data
with open(f'{base_dir}/demo_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(demo_rows)
print(f"✅ Created {base_dir}/demo_data.csv with Hero Account ACC0001.")