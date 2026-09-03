import sqlite3, os

def build():
    c = sqlite3.connect('dashboard.db')
    cur = c.cursor()
    # scorecard
    sc = cur.execute("SELECT supplier_name, country, category, status, otif_pct, defect_pct, composite_score FROM scorecard ORDER BY composite_score DESC").fetchall()
    alerts = cur.execute("SELECT severity, supplier, detail, metric FROM alerts ORDER BY CASE severity WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END").fetchall()
    cat_rows = cur.execute("SELECT category, orders, otif, defect, avg_delay FROM category_perf ORDER BY otif DESC").fetchall()
    freight_rows = cur.execute("SELECT freight_mode, orders, on_time, avg_delay, defect FROM freight_perf ORDER BY on_time DESC").fetchall()
    port_rows = cur.execute("SELECT origin_port, orders, otif, avg_delay FROM port_perf ORDER BY otif DESC").fetchall()

    html = '''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dashboard — Page 2</title>
<style>
:root{--bg:#0a0a0a;--gold:#d4a83a;--text:#fff;--sub:#ddd;--dim:#999}
*{box-sizing:border-box;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--text)}
body{background:var(--bg);margin:0;padding:2rem}
.container{max-width:1200px;margin:0 auto}
h1{font-weight:800;letter-spacing:-.03em;margin-bottom:.2rem;color:var(--gold)}
.sub{color:var(--sub);margin-bottom:1.5rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1rem;margin-bottom:2rem}
.card{background:#111;border:1px solid #222;border-radius:12px;padding:1rem}
.card h3{margin:0 0 .5rem;font-size:.9rem;text-transform:uppercase;letter-spacing:.08em;color:var(--gold)}
table{width:100%;border-collapse:collapse;font-size:.82rem}
th{text-align:left;padding:.4rem .5rem;border-bottom:1px solid #333;color:var(--dim);font-weight:600}
td{padding:.35rem .5rem;border-bottom:1px solid #222}
.badge{display:inline-block;padding:.15rem .45rem;border-radius:999px;font-size:.72rem;font-weight:700;background:#d4a83a22;color:var(--gold);border:1px solid #d4a83a44}
.alert-high{color:#e86b6b}.alert-med{color:#e0b24d}
@media(max-width:600px){body{padding:1rem}}
</style></head><body><div class="container">
<h1>Supplier Performance Dashboard</h1><p class="sub">Static snapshot from dashboard.db — generated 2026-09-03</p>

<div class="grid">
<div class="card"><h3>Scorecard — Top Suppliers</h3>
<table><thead><tr><th>Supplier</th><th>Country</th><th>Category</th><th>OTIF</th><th>Defect</th><th>Score</th></tr></thead><tbody>'''
    for row in sc:
        name,country,cat,status,otif,defect,score = row
        html += f'<tr><td><strong>{name}</strong></td><td>{country}</td><td>{cat}</td><td>{otif}%</td><td>{defect}%</td><td><span class="badge">{score}</span></td></tr>\n'
    html += '</tbody></table></div>\n'

    html += '<div class="card"><h3>Alerts (15 active)</h3><table><thead><tr><th>Severity</th><th>Supplier</th><th>Detail</th><th>Metric</th></tr></thead><tbody>'
    for row in alerts:
        sev,sup,det,met = row
        cls = 'alert-high' if sev=='High' else 'alert-med' if sev=='Medium' else ''
        html += f'<tr><td class="{cls}"><strong>{sev}</strong></td><td>{sup}</td><td>{det}</td><td>{met}</td></tr>\n'
    html += '</tbody></table></div>\n'

    html += '<div class="card"><h3>Category Performance</h3><table><thead><tr><th>Category</th><th>Orders</th><th>OTIF</th><th>Defect</th><th>Avg Delay</th></tr></thead><tbody>'
    for row in cat_rows:
        html += f'<tr><td><strong>{row[0]}</strong></td><td>{row[1]}</td><td>{row[2]}%</td><td>{row[3]}%</td><td>{row[4]}d</td></tr>\n'
    html += '</tbody></table></div>\n'

    html += '<div class="card"><h3>Freight Mode</h3><table><thead><tr><th>Mode</th><th>Orders</th><th>On-Time</th><th>Avg Delay</th><th>Defect</th></tr></thead><tbody>'
    for row in freight_rows:
        html += f'<tr><td><strong>{row[0]}</strong></td><td>{row[1]}</td><td>{row[2]}%</td><td>{row[3]}d</td><td>{row[4]}%</td></tr>\n'
    html += '</tbody></table></div>\n'

    html += '<div class="card"><h3>Port Performance (Top 10)</h3><table><thead><tr><th>Port</th><th>Orders</th><th>OTIF</th><th>Avg Delay</th></tr></thead><tbody>'
    for row in port_rows[:10]:
        html += f'<tr><td><strong>{row[0]}</strong></td><td>{row[1]}</td><td>{row[2]}%</td><td>{row[3]}d</td></tr>\n'
    html += '</tbody></table></div>\n</div>\n</div></body></html>'

    with open('page2.html','w',encoding='utf-8') as f:
        f.write(html)
    print('page2.html written,', len(html), 'bytes')

if __name__ == '__main__':
    build()
