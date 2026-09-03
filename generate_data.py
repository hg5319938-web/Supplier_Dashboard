"""
FMCG supplier ecosystem - realistic data with personas, product categories,
regional ports, freight modes, and narrative cases (audit, ramp, seasonal).
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)
os.makedirs('data', exist_ok=True)

# ── SUPPLIERS (FMCG, EU/EMEA, with personas) ──────────────────────
suppliers = pd.DataFrame([
    {'supplier_id': 'SUP-001', 'supplier_name': 'RheinValley Beverages GmbH', 'country': 'Germany',
     'category': 'Beverages', 'incoterm': 'DAP', 'lead_time_base': 5, 'otif_base': 96.5, 'defect_base': 0.6, 'volume_share': 18, 'status': 'Strategic'},
    {'supplier_id': 'SUP-002', 'supplier_name': 'Lyon Dairy Cooperative', 'country': 'France',
     'category': 'Dairy & Frozen', 'incoterm': 'CIF', 'lead_time_base': 4, 'otif_base': 94.2, 'defect_base': 1.1, 'volume_share': 15, 'status': 'Preferred'},
    {'supplier_id': 'SUP-003', 'supplier_name': 'Polish Snacks S.A.', 'country': 'Poland',
     'category': 'Snacks & Confectionery', 'incoterm': 'FCA', 'lead_time_base': 6, 'otif_base': 91.0, 'defect_base': 1.9, 'volume_share': 12, 'status': 'Corrective Action'},
    {'supplier_id': 'SUP-004', 'supplier_name': 'Iberian Olive Collective SL', 'country': 'Spain',
     'category': 'Pantry & Oils', 'incoterm': 'DDP', 'lead_time_base': 8, 'otif_base': 89.5, 'defect_base': 2.3, 'volume_share': 10, 'status': 'On Watch'},
    {'supplier_id': 'SUP-005', 'supplier_name': 'Benelux Personal Care BV', 'country': 'Netherlands',
     'category': 'Personal Care', 'incoterm': 'DAP', 'lead_time_base': 5, 'otif_base': 97.8, 'defect_base': 0.4, 'volume_share': 14, 'status': 'Strategic'},
    {'supplier_id': 'SUP-006', 'supplier_name': 'Baltic Cleaning UAB', 'country': 'Lithuania',
     'category': 'Home Care', 'incoterm': 'EXW', 'lead_time_base': 7, 'otif_base': 88.3, 'defect_base': 2.6, 'volume_share': 8, 'status': 'On Watch'},
    {'supplier_id': 'SUP-007', 'supplier_name': 'AlpenSparkling AG', 'country': 'Switzerland',
     'category': 'Beverages', 'incoterm': 'CIF', 'lead_time_base': 6, 'otif_base': 98.1, 'defect_base': 0.3, 'volume_share': 11, 'status': 'Strategic'},
    {'supplier_id': 'SUP-008', 'supplier_name': 'Mediterranean Pantry Srl', 'country': 'Italy',
     'category': 'Pantry & Oils', 'incoterm': 'DAP', 'lead_time_base': 7, 'otif_base': 92.7, 'defect_base': 1.4, 'volume_share': 9, 'status': 'Preferred'},
    {'supplier_id': 'SUP-009', 'supplier_name': 'Nordic Cereal OY', 'country': 'Finland',
     'category': 'Breakfast & Cereals', 'incoterm': 'DAP', 'lead_time_base': 9, 'otif_base': 95.0, 'defect_base': 0.7, 'volume_share': 7, 'status': 'Ramping Up'},
    {'supplier_id': 'SUP-010', 'supplier_name': 'Aegean Sea Foods Ltd', 'country': 'Greece',
     'category': 'Dairy & Frozen', 'incoterm': 'CIF', 'lead_time_base': 8, 'otif_base': 90.4, 'defect_base': 1.7, 'volume_share': 6, 'status': 'On Watch'},
])

suppliers.to_excel('data/suppliers.xlsx', index=False)
print(f"Suppliers: {len(suppliers)}")

# ── SKUs / PRODUCTS ───────────────────────────────────────────────
skus = pd.DataFrame([
    {'sku_id': f'SKU-{i:04d}', 'product_name': name, 'category': cat, 'unit_cost_eur': round(np.random.uniform(0.8, 14.5), 2), 'units_per_case': np.random.choice([6,12,24,48])}
    for i, (name, cat) in enumerate([
        ('Sparkling Water 1.5L', 'Beverages'),
        ('Cola Original 330ml', 'Beverages'),
        ('Energy Citrus 500ml', 'Beverages'),
        ('Greek Yogurt 0% 1kg', 'Dairy & Frozen'),
        ('Mozzarella 125g', 'Dairy & Frozen'),
        ('Frozen Berries 500g', 'Dairy & Frozen'),
        ('Sea Salt Chips 150g', 'Snacks & Confectionery'),
        ('Dark Chocolate 70% 100g', 'Snacks & Confectionery'),
        ('Extra Virgin Olive Oil 750ml', 'Pantry & Oils'),
        ('Balsamic Vinegar 250ml', 'Pantry & Oils'),
        ('Shampoo 400ml', 'Personal Care'),
        ('Body Wash 500ml', 'Personal Care'),
        ('Laundry Detergent 2L', 'Home Care'),
        ('Dish Soap 750ml', 'Home Care'),
        ('Muesli 750g', 'Breakfast & Cereals'),
        ('Granola Bars 6pk', 'Breakfast & Cereals'),
        ('Mineral Water 6x1.5L', 'Beverages'),
        ('Ice Cream Vanilla 900ml', 'Dairy & Frozen'),
    ], start=1)
])
skus.to_excel('data/skus.xlsx', index=False)
print(f"SKUs: {len(skus)}")

# ── ORDERS (last 6 months, with seasonality) ──────────────────────
end = datetime.now()
start = end - timedelta(days=180)

orders_list = []
po_counter = 48000
for day_offset in range(180):
    order_date = start + timedelta(days=day_offset)
    # Seasonality: summer spike for beverages, holiday spike for snacks
    month = order_date.month
    if month in (6, 7, 8):
        season_boost = 1.4  # summer
    elif month in (11, 12):
        season_boost = 1.5  # holiday
    else:
        season_boost = 1.0

    n_orders = int(np.random.poisson(3.5 * season_boost))
    for _ in range(n_orders):
        sup = suppliers.sample(weights='volume_share', random_state=po_counter).iloc[0]
        sku = skus[skus['category'] == sup['category']].sample(1).iloc[0]
        cases = np.random.randint(50, 1200)
        qty = int(cases * sku['units_per_case'])
        expected = order_date + timedelta(days=int(sup['lead_time_base'] + np.random.normal(0, 1)))
        orders_list.append({
            'po_id': f'PO-{po_counter}',
            'supplier_id': sup['supplier_id'],
            'sku_id': sku['sku_id'],
            'category': sup['category'],
            'origin_port': {'Germany':'Hamburg','France':'Marseille','Poland':'Gdansk',
                            'Spain':'Valencia','Netherlands':'Rotterdam','Lithuania':'Klaipeda',
                            'Switzerland':'Basel','Italy':'Genoa','Finland':'Helsinki','Greece':'Piraeus'}[sup['country']],
            'dest_dc': np.random.choice(['DC-London','DC-Paris','DC-Berlin','DC-Amsterdam','DC-Madrid']),
            'order_date': order_date.strftime('%Y-%m-%d'),
            'expected_delivery': expected.strftime('%Y-%m-%d'),
            'cases': cases,
            'units_ordered': qty,
            'unit_cost_eur': sku['unit_cost_eur'],
            'order_value_eur': round(qty * sku['unit_cost_eur'], 2),
            'incoterm': sup['incoterm'],
            'freight_mode': np.random.choice(['Truck','Sea','Rail','Air'], p=[0.55,0.25,0.15,0.05]),
        })
        po_counter += 1

orders_df = pd.DataFrame(orders_list)
orders_df.to_excel('data/orders.xlsx', index=False)
print(f"Orders: {len(orders_df)}")

# ── RECEIPTS (with quality + delivery variance) ───────────────────
receipts_list = []
for _, po in orders_df.iterrows():
    sup = suppliers[suppliers['supplier_id'] == po['supplier_id']].iloc[0]
    expected = datetime.strptime(po['expected_delivery'], '%Y-%m-%d')

    # Freight delay bias
    if po['freight_mode'] == 'Sea': delay_bias = 1.5
    elif po['freight_mode'] == 'Air': delay_bias = -0.5
    elif po['freight_mode'] == 'Rail': delay_bias = 0.2
    else: delay_bias = 0

    # Status probability by supplier persona
    if sup['status'] == 'Corrective Action':
        on_time = np.random.random() < (sup['otif_base']/100) * 0.85
        defect_mult = 1.6
    elif sup['status'] == 'On Watch':
        on_time = np.random.random() < (sup['otif_base']/100) * 0.95
        defect_mult = 1.3
    elif sup['status'] == 'Ramping Up':
        on_time = np.random.random() < (sup['otif_base']/100) * 0.9  # newer, more variance
        defect_mult = 1.1
    else:
        on_time = np.random.random() < (sup['otif_base']/100)
        defect_mult = 1.0

    if on_time:
        actual = expected + timedelta(days=int(np.random.normal(delay_bias, 1.2)))
    else:
        actual = expected + timedelta(days=int(np.random.normal(delay_bias + 4, 2.5)))

    # In full check
    fill_rate = 0.995 if sup['status'] == 'Strategic' else 0.97
    if sup['status'] == 'Corrective Action': fill_rate = 0.93
    if sup['status'] == 'On Watch': fill_rate = 0.95

    if np.random.random() < fill_rate:
        received = po['units_ordered']
    else:
        received = int(po['units_ordered'] * np.random.uniform(0.85, 0.97))

    # Defects - quality check
    defect_rate = sup['defect_base'] * defect_mult / 100
    defective = int(received * defect_rate * np.random.uniform(0.5, 1.8))

    # QC outcome
    if defective == 0:
        qc_outcome = 'Pass'
    elif defective / received < 0.01:
        qc_outcome = 'Pass w/ Note'
    elif defective / received < 0.03:
        qc_outcome = 'Quarantine'
    else:
        qc_outcome = 'Reject'

    receipts_list.append({
        'po_id': po['po_id'],
        'supplier_id': po['supplier_id'],
        'actual_delivery': actual.strftime('%Y-%m-%d'),
        'delivery_delay_days': max(0, (actual - expected).days),
        'is_on_time': actual <= expected,
        'units_received': received,
        'units_ordered': po['units_ordered'],
        'is_in_full': received >= po['units_ordered'] * 0.98,
        'defective_units': defective,
        'defect_rate_pct': round(defective / received * 100, 2) if received else 0,
        'qc_outcome': qc_outcome,
        'freight_mode': po['freight_mode'],
        'origin_port': po['origin_port'],
        'dest_dc': po['dest_dc'],
    })

receipts_df = pd.DataFrame(receipts_list)
receipts_df.to_excel('data/receipts.xlsx', index=False)
print(f"Receipts: {len(receipts_df)}")

print("Done.")
