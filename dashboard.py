"""
Operations Dashboard - FMCG Supplier Performance
Style: Neo Kinpaku (lacquer + gold + patina) from harsh-gupta-port.netlify.app
"""
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(
    page_title="Operations — Harsh Gupta",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── TOKENS (match portfolio.html) ────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Alumni+Sans:wght@100;200;300;400&family=Albert+Sans:opsz,wght@8..24,300;8..24,400;8..24,500&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --lacquer:        oklch(7% 0.006 95);
  --lacquer-deep:   oklch(4% 0.004 95);
  --lacquer-rise:   oklch(11% 0.006 95);
  --kinpaku:        oklch(84% 0.19 80.46);
  --kinpaku-soft:   oklch(77% 0.14 82);
  --kinpaku-mute:   oklch(58% 0.065 82);
  --patina:         oklch(70% 0.12 188);
  --patina-deep:    oklch(49% 0.08 188);
  --text-bright:    oklch(96% 0 0);
  --text:           oklch(90% 0.02 82);
  --text-mute:      oklch(76% 0.012 95);
  --text-faint:     oklch(62% 0 0);
  --rule:           oklch(58% 0.065 82 / 0.22);
  --rule-soft:      oklch(58% 0.065 82 / 0.10);
  --font-display:   "Alumni Sans", sans-serif;
  --font-body:      "Albert Sans", sans-serif;
  --font-mono:      "JetBrains Mono", monospace;
}

html, body, .stApp { color-scheme: dark; }
.stApp {
  background: var(--lacquer);
  color: var(--text);
  font-family: var(--font-body);
  font-weight: 400;
  letter-spacing: 0.01em;
}
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
.block-container { padding-top: 1.5rem; max-width: 1400px; }

/* Lacquer ground noise */
.stApp::before {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background:
    radial-gradient(ellipse 1000px 700px at 10% 0%,   oklch(84% 0.19 80.46 / 0.05), transparent 60%),
    radial-gradient(ellipse 800px 600px  at 90% 100%, oklch(70% 0.12 188 / 0.04),  transparent 60%);
}
.stApp::after {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  opacity: 0.10; mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.55'/%3E%3C/svg%3E");
}

/* Selection */
::selection { background: var(--kinpaku); color: oklch(14% 0.018 95); }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--lacquer); }
::-webkit-scrollbar-thumb { background: var(--kinpaku-mute); }

/* Type */
h1, h2, h3, h4 { font-family: var(--font-display); font-weight: 300; letter-spacing: 0.04em; color: var(--text-bright); }
h1 { font-size: 3.2rem; line-height: 1; margin: 0; }
h2 { font-size: 2.2rem; font-weight: 200; margin: 0; }
h3 { font-size: 1.4rem; font-weight: 300; margin: 0; }
.mono { font-family: var(--font-mono); font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--text-mute); }
.mute { color: var(--text-mute); }
.gold { color: var(--kinpaku); }
.patina { color: var(--patina); }

/* Tilt card with gold seam */
.tilt-card {
  position: relative;
  background: var(--lacquer-rise);
  border: 1px solid var(--rule);
  padding: 28px 28px 32px 28px;
  overflow: hidden;
  transition: border-color 0.3s cubic-bezier(0.2,0.8,0.2,1);
}
.tilt-card:hover { border-color: var(--kinpaku-mute); }
.tilt-card::before {
  content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--kinpaku) 30%, var(--kinpaku) 70%, transparent);
}
.kpi-value { font-family: var(--font-display); font-size: 3rem; font-weight: 200; color: var(--kinpaku); line-height: 1; }
.kpi-value.patina { color: var(--patina); }
.kpi-value.bright { color: var(--text-bright); }
.kpi-label { font-family: var(--font-mono); font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--text-mute); margin-top: 10px; }
.kpi-delta { font-family: var(--font-mono); font-size: 0.7rem; letter-spacing: 0.08em; color: var(--patina); margin-top: 8px; }
.kpi-delta.warn { color: var(--kinpaku); }
.kpi-delta.bad { color: oklch(70% 0.18 25); }

/* Sidebar */
[data-testid="stSidebar"] { background: var(--lacquer-deep); border-right: 1px solid var(--rule); }
[data-testid="stSidebar"] * { color: var(--text); }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 32px; border-bottom: 1px solid var(--rule); }
.stTabs [data-baseweb="tab"] {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text-mute);
  padding: 16px 0;
  background: transparent;
}
.stTabs [aria-selected="true"] { color: var(--kinpaku) !important; border-bottom: 1px solid var(--kinpaku); }

/* Buttons */
.stButton button {
  background: transparent;
  border: 1px solid var(--rule);
  color: var(--kinpaku) !important;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  border-radius: 0;
  padding: 10px 20px;
  transition: all 0.3s ease;
}
.stButton button:hover { background: oklch(84% 0.19 80.46 / 0.08); border-color: var(--kinpaku); }

/* Multiselect / select */
.stMultiSelect, .stSelectbox { color: var(--text); }
[data-baseweb="select"] { background: var(--lacquer-rise); border: 1px solid var(--rule); }

/* Dataframes */
.stDataFrame { border: 1px solid var(--rule); background: var(--lacquer-rise); }

/* Gold seam divider */
.gold-seam { height: 1px; background: linear-gradient(90deg, transparent, var(--kinpaku-mute) 30%, var(--kinpaku-mute) 70%, transparent); margin: 48px 0; border: 0; }
.thin-rule { height: 1px; background: var(--rule); margin: 24px 0; border: 0; }

/* Hairline frame for charts */
.frame {
  position: relative;
  background: var(--lacquer-rise);
  border: 1px solid var(--rule);
  padding: 24px;
}
.frame::before {
  content: ""; position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--kinpaku) 40%, var(--kinpaku) 60%, transparent);
}

/* Status pill */
.pill { display: inline-block; padding: 3px 10px; font-family: var(--font-mono); font-size: 0.6rem; letter-spacing: 0.12em; text-transform: uppercase; border: 1px solid var(--rule); color: var(--text-mute); }
.pill.strategic { color: var(--kinpaku); border-color: oklch(84% 0.19 80.46 / 0.4); }
.pill.preferred { color: var(--patina); border-color: oklch(70% 0.12 188 / 0.4); }
.pill.warn { color: var(--kinpaku-soft); border-color: oklch(84% 0.19 80.46 / 0.3); }
.pill.bad { color: oklch(70% 0.18 25); border-color: oklch(70% 0.18 25 / 0.4); }
.pill.up { color: oklch(70% 0.12 95); border-color: oklch(70% 0.12 95 / 0.3); }

/* Section header */
.section-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 24px; }
.section-head h2 { }
.section-head .mono { }

/* Sig */
.sig { text-align: center; font-family: var(--font-mono); font-size: 0.65rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--kinpaku-mute); padding: 48px 0 24px 0; margin-top: 64px; border-top: 1px solid var(--rule); }
.sig span { color: var(--kinpaku); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── DATA ────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load():
    conn = sqlite3.connect('dashboard.db')
    data = {
        'scorecard': pd.read_sql('SELECT * FROM scorecard', conn),
        'trend': pd.read_sql('SELECT * FROM trend', conn),
        'shipments': pd.read_sql('SELECT * FROM shipments', conn),
        'category_perf': pd.read_sql('SELECT * FROM category_perf', conn),
        'freight_perf': pd.read_sql('SELECT * FROM freight_perf', conn),
        'port_perf': pd.read_sql('SELECT * FROM port_perf', conn),
        'alerts': pd.read_sql('SELECT * FROM alerts', conn),
        'suppliers': pd.read_sql('SELECT * FROM suppliers', conn),
    }
    conn.close()
    return data

d = load()
sc = d['scorecard']

# ── HEADER ──────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:flex-end; padding-bottom:24px; border-bottom:1px solid var(--rule); position:relative; z-index:1;">
  <div>
    <div class="mono" style="margin-bottom:14px;">◆ operations · fmcg · emea ◆</div>
    <h1>Supplier Performance <span class="gold">Console</span></h1>
  </div>
  <div style="text-align:right;">
    <div class="mono">live · refreshed 60s</div>
    <div class="mono gold" style="margin-top:6px;">✦ Harsh Gupta</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

# ── TICKER (top suppliers strip) ─────────────────────────────────
if not sc.empty:
    top3 = sc.nlargest(3, 'composite_score')[['supplier_name','composite_score','otif_pct']].values.tolist()
    bot1 = sc.nsmallest(1, 'composite_score')[['supplier_name','composite_score']].values.tolist()
    st.markdown(f"""
    <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap; font-family:var(--font-mono); font-size:0.65rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--text-mute); padding:10px 0; border-top:1px solid var(--rule); border-bottom:1px solid var(--rule);">
      <span class="gold">▸</span> Top performers:
      <span class="gold">{top3[0][0]}</span> <span style="color:var(--text-faint)">{top3[0][1]}</span> ·
      <span class="gold">{top3[1][0]}</span> <span style="color:var(--text-faint)">{top3[1][1]}</span> ·
      <span class="gold">{top3[2][0]}</span> <span style="color:var(--text-faint)">{top3[2][1]}</span>
      &nbsp;&nbsp;<span style="color:oklch(70% 0.18 25)">▸</span> Watch:
      <span style="color:oklch(70% 0.18 25)">{bot1[0][0]}</span> <span style="color:var(--text-faint)">{bot1[0][1]}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

# ── KPI ROW ─────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

avg_otif = sc['otif_pct'].mean()
avg_defect = sc['defect_pct'].mean()
avg_lead = sc['avg_lead_time'].mean()
avg_comp = sc['composite_score'].mean()
total_spend = sc['annual_spend_gbp'].sum() / 1_000_000

with c1:
    st.markdown(f"""<div class="tilt-card"><div class="kpi-value">{avg_otif:.1f}<span style="font-size:1.4rem; color:var(--kinpaku-soft)">%</span></div><div class="kpi-label">OTIF · 30d</div><div class="kpi-delta">▲ {avg_otif-92:.1f} vs target</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="tilt-card"><div class="kpi-value patina">{avg_defect:.2f}<span style="font-size:1.4rem; color:var(--patina-deep)">%</span></div><div class="kpi-label">Defect Rate</div><div class="kpi-delta {'warn' if avg_defect>1.5 else ''}">{'▲' if avg_defect>1.5 else '▼'} {abs(avg_defect-1.0):.2f} vs target</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="tilt-card"><div class="kpi-value bright">{avg_lead:.1f}<span style="font-size:1.4rem; color:var(--text-mute)">d</span></div><div class="kpi-label">Avg Lead Time</div><div class="kpi-delta {'warn' if avg_lead>5 else ''}">{'▲' if avg_lead>5 else '▼'} {abs(avg_lead-5):.1f} vs target</div></div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="tilt-card"><div class="kpi-value">{avg_comp:.1f}</div><div class="kpi-label">Composite Score</div><div class="kpi-delta">▲ {avg_comp-85:.1f} vs benchmark</div></div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""<div class="tilt-card"><div class="kpi-value bright">£{total_spend:.1f}<span style="font-size:1.2rem; color:var(--text-mute)">M</span></div><div class="kpi-label">Annual Spend</div><div class="kpi-delta">{len(sc)} active suppliers</div></div>""", unsafe_allow_html=True)

st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

# ── TABS ────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["◆ Scorecard", "◆ Trends", "◆ Logistics", "◆ Alerts"])

# ════════════════════════════════════════════════════════════════
# TAB 1 - SCORECARD
# ════════════════════════════════════════════════════════════════
with tab1:
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown("""<div class="section-head"><h2>Supplier <span class="gold">Scorecard</span></h2><div class="mono">last 30 days</div></div>""", unsafe_allow_html=True)
    with col_r:
        cat_filter = st.multiselect("Category", sc['category'].unique().tolist(), default=sc['category'].unique().tolist(), label_visibility="collapsed")

    sc_f = sc[sc['category'].isin(cat_filter)].sort_values('composite_score', ascending=False)

    # Table
    def status_pill(s):
        m = {'Strategic':'strategic','Preferred':'preferred','On Watch':'warn','Corrective Action':'bad','Ramping Up':'up'}
        return f'<span class="pill {m.get(s,"")}">{s}</span>'

    def fmt_row(r):
        otif = r['otif_pct']
        if otif >= 95: col = 'var(--kinpaku)'
        elif otif >= 88: col = 'var(--patina)'
        else: col = 'oklch(70% 0.18 25)'
        return f"""
        <tr style="border-bottom:1px solid var(--rule-soft);">
          <td style="padding:14px 12px;"><div style="color:var(--text-bright); font-weight:400;">{r['supplier_name']}</div><div class="mono" style="margin-top:2px;">{r['country']} · {r['incoterm']}</div></td>
          <td style="padding:14px 12px;">{status_pill(r['status'])}<div class="mono" style="margin-top:4px;">{r['category']}</div></td>
          <td style="padding:14px 12px; text-align:right; color:{col}; font-family:var(--font-display); font-size:1.6rem; font-weight:200;">{otif:.1f}<span style="font-size:0.9rem; color:var(--text-faint)">%</span></td>
          <td style="padding:14px 12px; text-align:right; font-family:var(--font-mono); color:var(--text-mute);">{r['defect_pct']:.2f}%</td>
          <td style="padding:14px 12px; text-align:right; font-family:var(--font-mono); color:var(--text-mute);">{r['avg_lead_time']:.1f}d</td>
          <td style="padding:14px 12px; text-align:right; font-family:var(--font-display); font-size:1.6rem; font-weight:200; color:var(--kinpaku);">{r['composite_score']:.1f}</td>
        </tr>"""

    rows_html = "".join([fmt_row(r) for _, r in sc_f.iterrows()])
    table_html = f"""
    <div style="position:relative; z-index:1;">
    <table style="width:100%; border-collapse:collapse; background:var(--lacquer-rise); border:1px solid var(--rule); position:relative;">
      <thead>
        <tr style="border-bottom:1px solid var(--kinpaku-mute);">
          <th class="mono" style="text-align:left; padding:14px 12px; color:var(--kinpaku);">◆ Supplier</th>
          <th class="mono" style="text-align:left; padding:14px 12px; color:var(--kinpaku);">◆ Status</th>
          <th class="mono" style="text-align:right; padding:14px 12px; color:var(--kinpaku);">◆ OTIF</th>
          <th class="mono" style="text-align:right; padding:14px 12px; color:var(--kinpaku);">◆ Defect</th>
          <th class="mono" style="text-align:right; padding:14px 12px; color:var(--kinpaku);">◆ Lead</th>
          <th class="mono" style="text-align:right; padding:14px 12px; color:var(--kinpaku);">◆ Score</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

    # Two charts: composite bar + category heatmap-style
    ca, cb = st.columns(2)
    with ca:
        st.markdown("""<div class="section-head"><h3>Composite <span class="gold">Ranking</span></h3><div class="mono">higher is better</div></div>""", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=sc_f['supplier_name'], x=sc_f['composite_score'], orientation='h',
            marker=dict(
                color=sc_f['composite_score'],
                colorscale=[[0,'oklch(40% 0.08 188)'],[0.5,'oklch(58% 0.065 82)'],[1,'oklch(84% 0.19 80.46)']],
                line=dict(width=0),
            ),
            text=sc_f['composite_score'].apply(lambda x: f'{x:.1f}'),
            textposition='outside',
            textfont=dict(family='JetBrains Mono', size=10, color='oklch(76% 0.012 95)'),
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Albert Sans', color='oklch(76% 0.012 95)', size=11),
            height=380, margin=dict(l=10, r=40, t=10, b=10),
            xaxis=dict(gridcolor='oklch(58% 0.065 82 / 0.08)', zerolinecolor='oklch(58% 0.065 82 / 0.15)', range=[60, 105]),
            yaxis=dict(autorange='reversed', gridcolor='rgba(0,0,0,0)'),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with cb:
        st.markdown("""<div class="section-head"><h3>Category <span class="gold">Performance</span></h3><div class="mono">otif · defect · delay</div></div>""", unsafe_allow_html=True)
        cp = d['category_perf'].copy()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name='OTIF %', x=cp['category'], y=cp['otif'], marker_color='oklch(84% 0.19 80.46)', text=cp['otif'].apply(lambda x: f'{x:.0f}'), textposition='outside', textfont=dict(family='JetBrains Mono', size=9, color='oklch(84% 0.19 80.46)')))
        fig2.add_trace(go.Scatter(name='Defect %', x=cp['category'], y=cp['defect']*5, yaxis='y2', mode='lines+markers', line=dict(color='oklch(70% 0.12 188)', width=2), marker=dict(size=8), text=cp['defect'].apply(lambda x: f'{x:.1f}%'), textposition='top center', textfont=dict(family='JetBrains Mono', size=9, color='oklch(70% 0.12 188)')))
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Albert Sans', color='oklch(76% 0.012 95)', size=11),
            height=380, margin=dict(l=10, r=10, t=20, b=80),
            xaxis=dict(tickangle=-30, gridcolor='rgba(0,0,0,0)'),
            yaxis=dict(title='', gridcolor='oklch(58% 0.065 82 / 0.08)', range=[80, 100], tickfont=dict(family='JetBrains Mono', size=10, color='oklch(76% 0.012 95)')),
            yaxis2=dict(title='', overlaying='y', side='right', range=[0, 20], showgrid=False, tickfont=dict(family='JetBrains Mono', size=9, color='oklch(70% 0.12 188)')),
            legend=dict(orientation='h', yanchor='bottom', y=-0.45, font=dict(family='JetBrains Mono', size=9, color='oklch(76% 0.012 95)'), bgcolor='rgba(0,0,0,0)'),
            barmode='group',
        )
        st.plotly_chart(fig2, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 2 - TRENDS
# ════════════════════════════════════════════════════════════════
with tab2:
    col_p, col_q = st.columns([1, 3])
    with col_p:
        st.markdown("""<div class="section-head"><h2>Performance <span class="gold">Trajectory</span></h2></div>""", unsafe_allow_html=True)
        sel = st.selectbox("supplier", sc['supplier_name'].tolist(), label_visibility="collapsed")
        sid = sc[sc['supplier_name']==sel].iloc[0]
        st.markdown(f"""
        <div class="frame" style="margin-top:16px;">
          <div class="mono" style="margin-bottom:6px;">◆ current · 30d</div>
          <div class="kpi-value" style="font-size:3.6rem;">{sid['otif_pct']:.1f}<span style="font-size:1.4rem; color:var(--kinpaku-soft)">%</span></div>
          <div class="kpi-label">OTIF</div>
          <div style="height:1px; background:var(--rule); margin:18px 0;"></div>
          <div class="mono" style="margin-bottom:6px;">◆ quality</div>
          <div class="kpi-value patina" style="font-size:2.4rem;">{sid['defect_pct']:.2f}<span style="font-size:1.1rem; color:var(--patina-deep)">%</span></div>
          <div class="kpi-label">Defect Rate</div>
          <div style="height:1px; background:var(--rule); margin:18px 0;"></div>
          <div class="mono" style="margin-bottom:6px;">◆ composite</div>
          <div class="kpi-value" style="font-size:2.4rem;">{sid['composite_score']:.1f}</div>
          <div class="kpi-label">Score · weighted</div>
        </div>
        """, unsafe_allow_html=True)

    with col_q:
        st.markdown("""<div class="section-head"><h3>OTIF · <span class="gold">6-month curve</span></h3><div class="mono">target 95%</div></div>""", unsafe_allow_html=True)
        sup_id = sc[sc['supplier_name']==sel]['supplier_id'].iloc[0]
        td = d['trend'][d['trend']['supplier_id']==sup_id].sort_values('month')
        if not td.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=td['month'], y=td['otif_pct'],
                mode='lines+markers',
                line=dict(color='oklch(84% 0.19 80.46)', width=2.5, shape='spline'),
                marker=dict(size=10, color='oklch(84% 0.19 80.46)', line=dict(color='oklch(7% 0.006 95)', width=2)),
                fill='tozeroy',
                fillcolor='oklch(84% 0.19 80.46 / 0.06)',
                name='OTIF %',
                text=td['otif_pct'].apply(lambda x: f'{x:.1f}%'),
                hovertemplate='%{x} · %{text}<extra></extra>',
            ))
            fig.add_hline(y=95, line_dash='dot', line_color='oklch(70% 0.12 188)', opacity=0.6, annotation_text='Target', annotation_font=dict(family='JetBrains Mono', size=9, color='oklch(70% 0.12 188)'), annotation_position='top right')
            fig.add_hline(y=88, line_dash='dot', line_color='oklch(70% 0.18 25)', opacity=0.4, annotation_text='Watch', annotation_font=dict(family='JetBrains Mono', size=9, color='oklch(70% 0.18 25)'), annotation_position='bottom right')
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Albert Sans', color='oklch(76% 0.012 95)', size=11),
                height=440, margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(gridcolor='oklch(58% 0.065 82 / 0.06)', title=None),
                yaxis=dict(gridcolor='oklch(58% 0.065 82 / 0.06)', title=None, range=[75, 105]),
                showlegend=False, hovermode='x unified',
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='thin-rule'>", unsafe_allow_html=True)

    # Comparison + scatter
    ca, cb = st.columns(2)
    with ca:
        st.markdown("""<div class="section-head"><h3>All Suppliers · <span class="gold">Trend Overlay</span></h3><div class="mono">last 6m</div></div>""", unsafe_allow_html=True)
        fig3 = go.Figure()
        for sid_name in sc['supplier_name'].tolist():
            sup_id = sc[sc['supplier_name']==sid_name]['supplier_id'].iloc[0]
            td = d['trend'][d['trend']['supplier_id']==sup_id].sort_values('month')
            if len(td) > 0:
                fig3.add_trace(go.Scatter(x=td['month'], y=td['otif_pct'], mode='lines', name=sid_name, line=dict(width=1.5), opacity=0.7))
        fig3.add_hline(y=95, line_dash='dot', line_color='oklch(84% 0.19 80.46)', opacity=0.4)
        fig3.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Albert Sans', color='oklch(76% 0.012 95)', size=10),
            height=400, margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(gridcolor='oklch(58% 0.065 82 / 0.06)'),
            yaxis=dict(gridcolor='oklch(58% 0.065 82 / 0.06)', range=[75, 105]),
            legend=dict(font=dict(family='JetBrains Mono', size=8, color='oklch(76% 0.012 95)'), bgcolor='rgba(0,0,0,0)', orientation='h', yanchor='bottom', y=-0.4),
            hovermode='x unified',
        )
        st.plotly_chart(fig3, use_container_width=True)

    with cb:
        st.markdown("""<div class="section-head"><h3>Quality vs <span class="gold">Speed</span></h3><div class="mono">defect · lead time</div></div>""", unsafe_allow_html=True)
        fig4 = px.scatter(
            sc, x='avg_lead_time', y='defect_pct', size='composite_score', color='composite_score',
            hover_name='supplier_name',
            color_continuous_scale=[[0,'oklch(40% 0.08 188)'],[0.5,'oklch(58% 0.065 82)'],[1,'oklch(84% 0.19 80.46)']],
            size_max=35,
        )
        fig4.add_vline(x=sc['avg_lead_time'].mean(), line_dash='dot', line_color='oklch(58% 0.065 82 / 0.4)')
        fig4.add_hline(y=sc['defect_pct'].mean(), line_dash='dot', line_color='oklch(58% 0.065 82 / 0.4)')
        fig4.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Albert Sans', color='oklch(76% 0.012 95)', size=11),
            height=400, margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(title=dict(text='Avg Lead Time (days)', font=dict(family='JetBrains Mono', size=10)), gridcolor='oklch(58% 0.065 82 / 0.08)'),
            yaxis=dict(title=dict(text='Defect %', font=dict(family='JetBrains Mono', size=10)), gridcolor='oklch(58% 0.065 82 / 0.08)'),
            coloraxis_showscale=False, showlegend=False,
        )
        st.plotly_chart(fig4, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 3 - LOGISTICS
# ════════════════════════════════════════════════════════════════
with tab3:
    sh = d['shipments']
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="section-head"><h3>Shipment <span class="gold">Status</span></h3><div class="mono">live pipeline</div></div>""", unsafe_allow_html=True)
        sc_count = sh['shipment_status'].value_counts()
        colors_map = {'Delivered':'oklch(70% 0.12 188)','In Transit':'oklch(84% 0.19 80.46)','At Port':'oklch(58% 0.065 82)','Customs Hold':'oklch(70% 0.18 25)','Pending Pickup':'oklch(76% 0.012 95)'}
        fig = go.Figure(go.Pie(
            labels=sc_count.index, values=sc_count.values, hole=0.65,
            marker=dict(colors=[colors_map.get(s, 'oklch(58% 0.065 82)') for s in sc_count.index]),
            textinfo='label+percent', textposition='outside',
            textfont=dict(family='JetBrains Mono', size=10, color='oklch(76% 0.012 95)'),
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Albert Sans', color='oklch(76% 0.012 95)', size=11),
            height=360, margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True, legend=dict(orientation='h', yanchor='bottom', y=-0.2, font=dict(family='JetBrains Mono', size=9, color='oklch(76% 0.012 95)'), bgcolor='rgba(0,0,0,0)'),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""<div class="section-head"><h3>Freight Mode · <span class="gold">Reliability</span></h3><div class="mono">on-time %</div></div>""", unsafe_allow_html=True)
        fp = d['freight_perf']
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=fp['freight_mode'], y=fp['on_time'],
            marker=dict(color=fp['on_time'], colorscale=[[0,'oklch(40% 0.08 25)'],[0.5,'oklch(58% 0.065 82)'],[1,'oklch(70% 0.12 188)']], line=dict(width=0)),
            text=fp['on_time'].apply(lambda x: f'{x:.1f}%'), textposition='outside',
            textfont=dict(family='JetBrains Mono', size=10, color='oklch(76% 0.012 95)'),
        ))
        fig.add_hline(y=95, line_dash='dot', line_color='oklch(84% 0.19 80.46)', opacity=0.4)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Albert Sans', color='oklch(76% 0.012 95)', size=11),
            height=360, margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(gridcolor='rgba(0,0,0,0)', title=None),
            yaxis=dict(gridcolor='oklch(58% 0.065 82 / 0.08)', range=[80, 105], title=None),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='thin-rule'>", unsafe_allow_html=True)

    # Port performance + DC destination
    ca, cb = st.columns(2)
    with ca:
        st.markdown("""<div class="section-head"><h3>Origin Port · <span class="gold">Performance</span></h3><div class="mono">otif %</div></div>""", unsafe_allow_html=True)
        pp = d['port_perf'].head(10)
        fig = go.Figure(go.Bar(
            x=pp['otif'], y=pp['origin_port'], orientation='h',
            marker=dict(color=pp['otif'], colorscale=[[0,'oklch(40% 0.08 25)'],[0.5,'oklch(58% 0.065 82)'],[1,'oklch(84% 0.19 80.46)']], line=dict(width=0)),
            text=pp['otif'].apply(lambda x: f'{x:.1f}%'), textposition='outside',
            textfont=dict(family='JetBrains Mono', size=9, color='oklch(76% 0.012 95)'),
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Albert Sans', color='oklch(76% 0.012 95)', size=11),
            height=380, margin=dict(l=10, r=40, t=10, b=10),
            xaxis=dict(gridcolor='oklch(58% 0.065 82 / 0.08)', range=[80, 100]),
            yaxis=dict(autorange='reversed', gridcolor='rgba(0,0,0,0)'),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with cb:
        st.markdown("""<div class="section-head"><h3>DC · <span class="gold">Inbound Volume</span></h3><div class="mono">orders per dc</div></div>""", unsafe_allow_html=True)
        dc_counts = sh['dest_dc'].value_counts().reset_index()
        dc_counts.columns = ['dc', 'count']
        fig = go.Figure(go.Bar(
            x=dc_counts['dc'], y=dc_counts['count'],
            marker=dict(color='oklch(84% 0.19 80.46)', line=dict(width=0)),
            text=dc_counts['count'], textposition='outside',
            textfont=dict(family='JetBrains Mono', size=10, color='oklch(76% 0.012 95)'),
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Albert Sans', color='oklch(76% 0.012 95)', size=11),
            height=380, margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(gridcolor='rgba(0,0,0,0)'),
            yaxis=dict(gridcolor='oklch(58% 0.065 82 / 0.08)'),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='thin-rule'>", unsafe_allow_html=True)

    # Recent shipments table
    st.markdown("""<div class="section-head"><h3>Recent <span class="gold">Shipments</span></h3><div class="mono">last 15</div></div>""", unsafe_allow_html=True)
    recent_sh = sh.sort_values('order_date', ascending=False).head(15)
    def ship_status_pill(s):
        m = {'Delivered':'preferred','In Transit':'strategic','At Port':'warn','Customs Hold':'bad','Pending Pickup':'up'}
        return f'<span class="pill {m.get(s,"")}">{s}</span>'
    rows = ""
    for _, r in recent_sh.iterrows():
        rows += f"""
        <tr style="border-bottom:1px solid var(--rule-soft);">
          <td class="mono" style="padding:10px 12px; color:var(--kinpaku);">{r['shipment_id']}</td>
          <td style="padding:10px 12px;">{r['supplier_name']}</td>
          <td class="mono" style="padding:10px 12px; color:var(--text-mute);">{r['origin_port']} → {r['dest_dc']}</td>
          <td class="mono" style="padding:10px 12px; color:var(--text-mute);">{r['freight_mode']}</td>
          <td class="mono" style="padding:10px 12px; text-align:right; color:var(--text-mute);">€{r['value_eur']:,.0f}</td>
          <td class="mono" style="padding:10px 12px; text-align:right; color:{'oklch(70% 0.18 25)' if r['delay_days']>2 else 'var(--text-mute)'};">{r['delay_days']}d</td>
          <td style="padding:10px 12px;">{ship_status_pill(r['shipment_status'])}</td>
        </tr>"""
    st.markdown(f"""
    <table style="width:100%; border-collapse:collapse; background:var(--lacquer-rise); border:1px solid var(--rule);">
      <thead><tr style="border-bottom:1px solid var(--kinpaku-mute);">
        <th class="mono" style="text-align:left; padding:10px 12px; color:var(--kinpaku);">◆ PO</th>
        <th class="mono" style="text-align:left; padding:10px 12px; color:var(--kinpaku);">◆ Supplier</th>
        <th class="mono" style="text-align:left; padding:10px 12px; color:var(--kinpaku);">◆ Lane</th>
        <th class="mono" style="text-align:left; padding:10px 12px; color:var(--kinpaku);">◆ Mode</th>
        <th class="mono" style="text-align:right; padding:10px 12px; color:var(--kinpaku);">◆ Value</th>
        <th class="mono" style="text-align:right; padding:10px 12px; color:var(--kinpaku);">◆ Delay</th>
        <th class="mono" style="text-align:left; padding:10px 12px; color:var(--kinpaku);">◆ Status</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 4 - ALERTS
# ════════════════════════════════════════════════════════════════
with tab4:
    al = d['alerts']
    if al.empty:
        st.markdown("""<div class="section-head"><h2>No active <span class="gold patina">alerts</span></h2></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="section-head"><h2>Action <span class="gold">Items</span></h2><div class="mono">requires review</div></div>""", unsafe_allow_html=True)
        # Group by severity
        for sev, color in [('High', 'oklch(70% 0.18 25)'), ('Medium', 'oklch(84% 0.19 80.46)')]:
            sub = al[al['severity']==sev]
            if sub.empty: continue
            st.markdown(f"""<div class="mono" style="margin:24px 0 12px 0; color:{color};">◆ {sev} severity · {len(sub)} items</div>""", unsafe_allow_html=True)
            cards = '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(340px, 1fr)); gap:1px; background:var(--rule);">'
            for _, a in sub.iterrows():
                cards += f"""
                <div style="background:var(--lacquer-rise); padding:20px 24px; position:relative; border-top:2px solid {color};">
                  <div class="mono" style="color:{color}; margin-bottom:8px;">◆ {a['type']} · {a['metric']}</div>
                  <div style="color:var(--text-bright); font-size:1.05rem; margin-bottom:4px;">{a['supplier']}</div>
                  <div style="color:var(--text-mute); font-size:0.9rem;">{a['detail']}</div>
                </div>"""
            cards += '</div>'
            st.markdown(cards, unsafe_allow_html=True)

# ── FOOTER ──────────────────────────────────────────────────────
st.markdown("""
<div class="sig">
  <span>✦</span>
</div>
""", unsafe_allow_html=True)
