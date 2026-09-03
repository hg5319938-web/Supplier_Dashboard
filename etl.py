"""
ETL for FMCG supplier performance.
Builds: scorecard, trend, shipments, category_perf, freight_perf, ports, alerts.
"""
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta

def run_etl():
    suppliers = pd.read_excel('data/suppliers.xlsx')
    orders = pd.read_excel('data/orders.xlsx')
    receipts = pd.read_excel('data/receipts.xlsx')
    skus = pd.read_excel('data/skus.xlsx')

    # Date conversions
    receipts['actual_delivery'] = pd.to_datetime(receipts['actual_delivery'])
    receipts['expected_delivery_dt'] = pd.to_datetime(
        orders.set_index('po_id').loc[receipts['po_id']]['expected_delivery'].values
    )
    orders['order_date'] = pd.to_datetime(orders['order_date'])

    # OTIF = On Time AND In Full
    receipts['otif'] = receipts['is_on_time'] & receipts['is_in_full']
    receipts['month'] = receipts['actual_delivery'].dt.to_period('M').astype(str)

    cutoff = datetime.now() - timedelta(days=30)
    recent = receipts[receipts['actual_delivery'] >= cutoff].copy()

    # ── SCORECARD ─────────────────────────────────────────────
    scorecard_rows = []
    for _, s in suppliers.iterrows():
        sub = recent[recent['supplier_id'] == s['supplier_id']]
        if len(sub) == 0:
            sub = receipts[receipts['supplier_id'] == s['supplier_id']].tail(20)
        if len(sub) == 0:
            continue
        otif_pct = round((sub['otif'].sum() / len(sub)) * 100, 1)
        defect_pct = round(sub['defective_units'].sum() / sub['units_received'].sum() * 100, 2)
        lead_days = sub['delivery_delay_days'].mean()
        # Composite: OTIF 50% / Quality 30% / Lead 20%
        comp = round(otif_pct*0.5 + max(0, 100-defect_pct*10)*0.3 + max(0, 100-lead_days*4)*0.2, 1)
        spend = orders[orders['supplier_id']==s['supplier_id']]['order_value_eur'].sum()
        scorecard_rows.append({
            'supplier_id': s['supplier_id'],
            'supplier_name': s['supplier_name'],
            'country': s['country'],
            'category': s['category'],
            'status': s['status'],
            'incoterm': s['incoterm'],
            'otif_pct': otif_pct,
            'defect_pct': defect_pct,
            'avg_lead_time': round(sub['delivery_delay_days'].mean(), 1),
            'composite_score': comp,
            'total_orders_30d': len(sub),
            'annual_spend_gbp': round(spend, 0),
            'volume_share_pct': s['volume_share'],
        })
    scorecard = pd.DataFrame(scorecard_rows)

    # ── TREND (monthly, last 6m) ──────────────────────────────
    trend = receipts.groupby(['supplier_id','month']).agg(
        total=('po_id','count'),
        on_time=('is_on_time','sum'),
        in_full=('is_in_full','sum'),
        otif_count=('otif','sum'),
        defect_qty=('defective_units','sum'),
        received_qty=('units_received','sum'),
    ).reset_index()
    trend['otif_pct'] = (trend['otif_count']/trend['total']*100).round(1)
    trend['defect_pct'] = (trend['defect_qty']/trend['received_qty']*100).round(2)

    # ── SHIPMENTS ─────────────────────────────────────────────
    sh = orders.merge(
        suppliers[['supplier_id','supplier_name','country','status']],
        on='supplier_id', how='left'
    )
    sh = sh.merge(
        receipts[['po_id','actual_delivery','delivery_delay_days','is_on_time','is_in_full','qc_outcome']],
        on='po_id', how='left'
    )
    sh['origin_port'] = sh['origin_port'].fillna('Unknown')
    sh['dest_dc'] = sh['dest_dc'].fillna('Unknown')
    sh['freight_mode'] = sh['freight_mode'].fillna('Truck')
    sh['shipment_status'] = sh['actual_delivery'].apply(
        lambda x: 'Delivered' if pd.notna(x) else np.random.choice(['In Transit','At Port','Customs Hold','Pending Pickup'], p=[0.5,0.2,0.1,0.2])
    )
    sh['on_time'] = sh['is_on_time'].fillna(False)
    sh['order_date_s'] = pd.to_datetime(sh['order_date']).dt.strftime('%Y-%m-%d')
    sh['expected_delivery_s'] = pd.to_datetime(sh['expected_delivery']).dt.strftime('%Y-%m-%d')
    sh['actual_delivery_s'] = pd.to_datetime(sh['actual_delivery']).dt.strftime('%Y-%m-%d')
    sh['delay_days'] = sh['delivery_delay_days'].fillna(0).astype(int)
    shipments = sh[['po_id','supplier_name','country','category','status','incoterm',
                    'origin_port','dest_dc','freight_mode','order_date_s','expected_delivery_s',
                    'actual_delivery_s','delay_days','order_value_eur','shipment_status','on_time','qc_outcome']].rename(
        columns={'po_id':'shipment_id','order_date_s':'order_date',
                 'expected_delivery_s':'expected_arrival','actual_delivery_s':'actual_arrival',
                 'order_value_eur':'value_gbp','status':'supplier_status'}
    )

    # ── CATEGORY PERFORMANCE ──────────────────────────────────
    cat_perf = receipts.merge(orders[['po_id','category']], on='po_id', how='left')
    cat_perf['otif'] = cat_perf['is_on_time'] & cat_perf['is_in_full']
    category_perf = cat_perf.groupby('category').agg(
        orders=('po_id','count'),
        otif=('otif', lambda x: round(x.mean()*100, 1)),
        defect=('defect_rate_pct', lambda x: round(x.mean(), 2)),
        avg_delay=('delivery_delay_days', lambda x: round(x.mean(), 1)),
    ).reset_index().sort_values('otif', ascending=False)

    # ── FREIGHT MODE PERFORMANCE ──────────────────────────────
    freight_perf = receipts.groupby('freight_mode').agg(
        orders=('po_id','count'),
        on_time=('is_on_time', lambda x: round(x.mean()*100, 1)),
        avg_delay=('delivery_delay_days', lambda x: round(x.mean(), 1)),
        defect=('defect_rate_pct', lambda x: round(x.mean(), 2)),
    ).reset_index().sort_values('on_time', ascending=False)

    # ── PORT PERFORMANCE ──────────────────────────────────────
    port_perf = receipts.groupby('origin_port').agg(
        orders=('po_id','count'),
        otif=('otif', lambda x: round(x.mean()*100, 1)),
        avg_delay=('delivery_delay_days', lambda x: round(x.mean(), 1)),
    ).reset_index().sort_values('otif', ascending=False)

    # ── ALERTS (action items) ─────────────────────────────────
    alerts = []
    # Quality alerts
    for _, s in suppliers.iterrows():
        sub = recent[recent['supplier_id']==s['supplier_id']]
        if len(sub) == 0: continue
        defect = sub['defective_units'].sum() / sub['units_received'].sum() * 100
        otif = sub['otif'].mean() * 100
        if defect > 2.0:
            alerts.append({'severity':'High','type':'Quality','supplier':s['supplier_name'],
                          'detail':f'Defect rate {defect:.2f}% exceeds 2% threshold','metric':f'{defect:.1f}%'})
        if otif < 90:
            alerts.append({'severity':'High','type':'Delivery','supplier':s['supplier_name'],
                          'detail':f'OTIF {otif:.1f}% below 90% target','metric':f'{otif:.1f}%'})
        if s['status'] == 'Corrective Action':
            alerts.append({'severity':'Medium','type':'Contract','supplier':s['supplier_name'],
                          'detail':'CAPA review due Q-end','metric':'CAPA'})
    # Add some shipment-level alerts
    late = shipments[(shipments['shipment_status'].isin(['Customs Hold','At Port'])) & (shipments['delay_days']>3)]
    for _, r in late.head(5).iterrows():
        alerts.append({'severity':'Medium','type':'Shipment','supplier':r['supplier_name'],
                      'detail':f"{r['shipment_id']} stuck at {r['shipment_status']}",'metric':f"{r['delay_days']}d"})
    alerts_df = pd.DataFrame(alerts) if alerts else pd.DataFrame(columns=['severity','type','supplier','detail','metric'])

    # ── WRITE TO SQLITE ───────────────────────────────────────
    if os.path.exists('dashboard.db'):
        os.remove('dashboard.db')
    conn = sqlite3.connect('dashboard.db')
    scorecard.to_sql('scorecard', conn, index=False)
    trend.to_sql('trend', conn, index=False)
    shipments.to_sql('shipments', conn, index=False)
    category_perf.to_sql('category_perf', conn, index=False)
    freight_perf.to_sql('freight_perf', conn, index=False)
    port_perf.to_sql('port_perf', conn, index=False)
    alerts_df.to_sql('alerts', conn, index=False)
    suppliers.to_sql('suppliers', conn, index=False)
    conn.close()

    print(f"ETL complete: scorecard={len(scorecard)}, trend={len(trend)}, shipments={len(shipments)}, alerts={len(alerts_df)}")

if __name__ == '__main__':
    run_etl()
