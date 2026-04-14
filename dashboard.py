import streamlit as st
import pandas as pd
import json
import os
import requests
from pathlib import Path
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import time

# إعدادات الصفحة
st.set_page_config(
    page_title="المدافع الذكي - Smart Defender v4.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم CSS لنمط مظلم واحترافي
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
    }

    .stApp {
        background: #0a0e1a;
        color: #e0e6f0;
    }

    section[data-testid="stSidebar"] {
        background: #0d1221;
        border-left: 1px solid #1e2d4a;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #e0e6f0;
        text-align: right;
    }

    /* بطاقات المقاييس */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #0d1b35 0%, #112244 100%);
        border: 1px solid #1e3560;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 24px rgba(0,180,255,0.07);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(0,180,255,0.15);
    }

    div[data-testid="metric-container"] label {
        color: #7aa3cc !important;
        font-size: 0.82rem;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-size: 2.2rem;
        font-weight: 900;
    }

    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        color: #00ff99 !important;
    }

    /* رأس الصفحة */
    .page-header {
        background: linear-gradient(135deg, #0d1b35 0%, #0a2050 50%, #1a0a35 100%);
        border: 1px solid #1e3560;
        border-radius: 16px;
        padding: 20px 28px;
        margin-bottom: 22px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .page-title {
        font-size: 1.6rem;
        font-weight: 900;
        color: #e0f4ff;
        margin: 0;
    }

    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(0,255,120,0.1);
        border: 1px solid rgba(0,255,120,0.3);
        border-radius: 20px;
        padding: 6px 14px;
        color: #00ff88;
        font-size: 0.82rem;
        font-weight: 700;
    }

    .pulse-ring {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #00ff88;
        box-shadow: 0 0 0 0 rgba(0,255,136,0.7);
        animation: livepulse 1.5s infinite;
        display: inline-block;
    }

    @keyframes livepulse {
        0%   { box-shadow: 0 0 0 0 rgba(0,255,136,0.7); }
        70%  { box-shadow: 0 0 0 10px rgba(0,255,136,0); }
        100% { box-shadow: 0 0 0 0 rgba(0,255,136,0); }
    }

    /* بطاقة المخطط */
    .chart-card {
        background: linear-gradient(135deg, #0d1b35 0%, #0f1e3a 100%);
        border: 1px solid #1e3560;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 16px;
    }

    .chart-title {
        color: #7aa3cc;
        font-size: 0.88rem;
        font-weight: 700;
        text-align: right;
        margin-bottom: 8px;
        padding-right: 4px;
    }

    /* بطاقة التنبيه */
    .alert-row {
        background: linear-gradient(135deg, #1a0a0a 0%, #200d0d 100%);
        border: 1px solid #3d1515;
        border-right: 4px solid #ff4444;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        transition: transform 0.2s;
    }

    .alert-row:hover {
        transform: translateX(-4px);
        border-right-color: #ff6666;
    }

    .alert-row.high {
        background: linear-gradient(135deg, #1a1000 0%, #201500 100%);
        border: 1px solid #3d2800;
        border-right: 4px solid #ff8800;
    }

    .alert-row.medium {
        background: linear-gradient(135deg, #0e1a0a 0%, #121f0d 100%);
        border: 1px solid #1e3510;
        border-right: 4px solid #88cc00;
    }

    .alert-ip    { color: #00d4ff; font-weight: 700; font-size: 1rem; }
    .alert-time  { color: #5577aa; font-size: 0.78rem; }
    .alert-reason{ color: #aabccc; font-size: 0.84rem; margin-top: 4px; }
    .severity-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .sev-critical { background: rgba(255,68,68,0.2);  color: #ff6666; border: 1px solid #ff4444; }
    .sev-high     { background: rgba(255,136,0,0.2);  color: #ffaa44; border: 1px solid #ff8800; }
    .sev-medium   { background: rgba(136,204,0,0.2);  color: #aadd44; border: 1px solid #88cc00; }

    /* IP مُعزول */
    .blocked-card {
        background: linear-gradient(135deg, #0a0d1a 0%, #0d1122 100%);
        border: 1px solid #1e2d4a;
        border-right: 4px solid #cc0044;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }

    /* الشريط الجانبي */
    .sidebar-stat {
        background: #0d1428;
        border: 1px solid #1e2d4a;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 8px;
        text-align: center;
    }

    .sidebar-stat .val {
        font-size: 1.8rem;
        font-weight: 900;
        color: #00d4ff;
    }

    .sidebar-stat .lbl {
        font-size: 0.75rem;
        color: #556688;
        margin-top: 2px;
    }

    /* عداد التحديث */
    .refresh-counter {
        background: rgba(0,80,150,0.15);
        border: 1px solid rgba(0,120,255,0.2);
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 0.75rem;
        color: #4488bb;
        text-align: center;
    }

    /* زر */
    .stButton > button {
        background: linear-gradient(135deg, #0d3070 0%, #0a2050 100%);
        color: #00d4ff;
        border: 1px solid #1e4a9a;
        border-radius: 8px;
        font-family: 'Cairo', sans-serif;
        font-weight: 700;
        transition: all 0.2s;
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #1040a0 0%, #0d3070 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(0,150,255,0.25);
    }

    div[data-testid="stHorizontalBlock"] > div { gap: 12px; }

    .stSelectbox label, .stMultiSelect label, .stSlider label,
    .stRadio label, .stCheckbox label, .stTextInput label {
        color: #7aa3cc !important;
    }

    .stPlotlyChart { border-radius: 12px; overflow: hidden; }

    hr { border-color: #1e2d4a; }

    .footer-note {
        text-align: center;
        color: #2a3a55;
        font-size: 0.72rem;
        margin-top: 16px;
    }
</style>
""", unsafe_allow_html=True)

# المسارات
DATA_DIR = Path("defender_system/data")
ALERTS_FILE = DATA_DIR / "alerts.json"
BLOCKED_IPS_FILE = DATA_DIR / "blocked_ips.json"
CONFIG_FILE = DATA_DIR / "config.json"
WHITELIST_FILE = DATA_DIR / "whitelist.json"
import os
API_BASE_URL = os.environ.get("API_BASE_URL", "https://sh-production-5beb.up.railway.app:5000").rstrip("/")

AUTO_REFRESH_SECS = 3

# تهيئة الحالة
for key, default in [
    ('prev_alert_count', 0),
    ('prev_blocked_count', 0),
    ('refresh_count', 0),
    ('traffic_history', []),
    ('last_tick', time.time()),
]:
    if key not in st.session_state:
        st.session_state[key] = default

def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return default
    return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def dark_plotly(fig, height=280):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Cairo, sans-serif', color='#7aa3cc'),
        margin=dict(l=10, r=10, t=30, b=10),
        height=height,
        hovermode=False,
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(color='#7aa3cc')
        ),
        xaxis=dict(
            gridcolor='rgba(30,53,96,0.4)',
            zerolinecolor='rgba(30,53,96,0.3)',
            tickfont=dict(color='#4a6a8a')
        ),
        yaxis=dict(
            gridcolor='rgba(30,53,96,0.4)',
            zerolinecolor='rgba(30,53,96,0.3)',
            tickfont=dict(color='#4a6a8a')
        )
    )
    return fig

def build_traffic_history(alerts):
    now = datetime.now()
    buckets = {}
    for i in range(30):
        t = (now - timedelta(minutes=i)).strftime('%H:%M')
        buckets[t] = {'total': 0, 'critical': 0, 'high': 0, 'normal': 0}

    for a in alerts:
        try:
            ts = datetime.fromisoformat(a.get('timestamp', ''))
            label = ts.strftime('%H:%M')
            if label in buckets:
                buckets[label]['total'] += 1
                sev = a.get('severity', 'MEDIUM')
                if sev == 'CRITICAL':
                    buckets[label]['critical'] += 1
                elif sev == 'HIGH':
                    buckets[label]['high'] += 1
                else:
                    buckets[label]['normal'] += 1
        except Exception:
            pass

    times = sorted(buckets.keys())
    return times, buckets

def animated_traffic_chart(alerts):
    times, buckets = build_traffic_history(alerts)
    totals   = [buckets[t]['total']    for t in times]
    critical = [buckets[t]['critical'] for t in times]
    highs    = [buckets[t]['high']     for t in times]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=totals, name='إجمالي التنبيهات', mode='lines',
        line=dict(color='#00d4ff', width=2.5, shape='spline', smoothing=1.2),
        fill='tozeroy', fillcolor='rgba(0,212,255,0.08)',
    ))
    fig.add_trace(go.Scatter(
        x=times, y=critical, name='حرجة', mode='lines+markers',
        line=dict(color='#ff4444', width=2, shape='spline', smoothing=1.2),
        fill='tozeroy', fillcolor='rgba(255,68,68,0.07)',
        marker=dict(size=5, color='#ff4444')
    ))
    fig.add_trace(go.Scatter(
        x=times, y=highs, name='عالية', mode='lines',
        line=dict(color='#ff8800', width=1.5, shape='spline', smoothing=1.2),
        fill='tozeroy', fillcolor='rgba(255,136,0,0.05)',
    ))
    fig.update_layout(
        transition={'duration': 600, 'easing': 'cubic-in-out'},
        legend=dict(orientation='h', y=1.08, x=1, xanchor='right'),
        xaxis_title='الوقت', yaxis_title='عدد التنبيهات',
    )
    return dark_plotly(fig, height=300)

def network_health_gauge(alerts, blocked_ips):
    critical = sum(1 for a in alerts if a.get('severity') == 'CRITICAL')
    total    = len(alerts) or 1
    blocked  = len(blocked_ips)
    raw_score = max(0, 100 - (critical * 3) - (blocked * 5) - (total * 0.5))
    health    = min(100, max(0, raw_score))
    color = '#00ff88' if health > 70 else '#ffaa00' if health > 40 else '#ff4444'
    label = 'ممتاز' if health > 70 else 'تحذير' if health > 40 else 'خطر'
    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta', value=round(health, 1),
        number=dict(suffix='%', font=dict(color=color, size=36, family='Cairo')),
        title=dict(text=f'صحة الشبكة — {label}', font=dict(color='#7aa3cc', size=13)),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor='#2a3a55', tickwidth=1, tickfont=dict(color='#4a6a8a')),
            bar=dict(color=color, thickness=0.25),
            bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)',
            steps=[
                dict(range=[0, 40],  color='rgba(255,60,60,0.12)'),
                dict(range=[40, 70], color='rgba(255,160,0,0.10)'),
                dict(range=[70, 100],color='rgba(0,255,120,0.10)'),
            ],
            threshold=dict(line=dict(color=color, width=3), thickness=0.8, value=health)
        )
    ))
    return dark_plotly(fig, height=260)

def severity_donut(alerts):
    if not alerts: return None
    counts = pd.Series([a.get('severity', 'MEDIUM') for a in alerts]).value_counts()
    color_map = {'CRITICAL': '#ff4444', 'HIGH': '#ff8800', 'MEDIUM': '#88cc00', 'LOW': '#00aaff'}
    colors = [color_map.get(s, '#4488aa') for s in counts.index]
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.55,
        marker=dict(colors=colors, line=dict(color='#0a0e1a', width=2)),
        textinfo='percent+label', textfont=dict(color='#ddeeff', size=11, family='Cairo'),
        hovertemplate='%{label}: %{value} تنبيه<extra></extra>',
    ))
    fig.update_layout(annotations=[dict(text=f'{len(alerts)}<br>تنبيه', x=0.5, y=0.5, font=dict(size=16, color='#00d4ff', family='Cairo'), showarrow=False)])
    return dark_plotly(fig, height=260)

def protocol_bar(alerts):
    if not alerts: return None
    counts = pd.Series([a.get('protocol', 'TCP') for a in alerts]).value_counts()
    fig = go.Figure(go.Bar(
        x=counts.index, y=counts.values,
        marker=dict(color=counts.values, colorscale=[[0, '#0d3070'], [0.5, '#0070cc'], [1, '#00d4ff']], line=dict(color='rgba(0,0,0,0)', width=0)),
        text=counts.values, textposition='outside', textfont=dict(color='#00d4ff', family='Cairo'),
    ))
    fig.update_layout(xaxis_title='البروتوكول', yaxis_title='العدد')
    return dark_plotly(fig, height=260)

def top_attackers_chart(alerts):
    if not alerts: return None
    top = pd.Series([a.get('src_ip', '?') for a in alerts]).value_counts().head(8)
    fig = go.Figure(go.Bar(
        y=top.index, x=top.values, orientation='h',
        marker=dict(color=top.values, colorscale=[[0, '#300010'], [0.5, '#880022'], [1, '#ff4444']], line=dict(color='rgba(0,0,0,0)')),
        text=top.values, textposition='outside', textfont=dict(color='#ff6666', family='Cairo'),
    ))
    fig.update_layout(yaxis=dict(autorange='reversed'), xaxis_title='التنبيهات')
    return dark_plotly(fig, height=300)

def page_header(title, subtitle=''):
    now_str = datetime.now().strftime('%H:%M:%S')
    st.markdown(f"""
    <div class="page-header">
        <div>
            <div class="page-title">{title}</div>
            {'<div style="color:#4a6a8a;font-size:0.82rem;margin-top:4px;">' + subtitle + '</div>' if subtitle else ''}
        </div>
        <div>
            <span class="live-badge">
                <span class="pulse-ring"></span> مباشر — {now_str}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def dashboard_page(alerts, blocked_ips):
    page_header("🛡️ لوحة التحكم الرئيسية", "Smart Defender v4.0 — تحديث تلقائي كل 3 ثوانٍ")
    prev_a = st.session_state.prev_alert_count
    prev_b = st.session_state.prev_blocked_count
    critical = sum(1 for a in alerts if a.get('severity') == 'CRITICAL')
    high     = sum(1 for a in alerts if a.get('severity') == 'HIGH')
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🚨 إجمالي التنبيهات", len(alerts), delta=f"+{len(alerts)-prev_a}" if len(alerts) > prev_a else None)
    c2.metric("🔒 أجهزة معزولة", len(blocked_ips), delta=f"+{len(blocked_ips)-prev_b}" if len(blocked_ips) > prev_b else None)
    c3.metric("🔴 حرجة", critical)
    c4.metric("🟠 عالية", high)
    c5.metric("🔄 التحديثات", st.session_state.refresh_count)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    col_gauge, col_traffic = st.columns([1, 2])
    with col_gauge:
        st.markdown('<div class="chart-title">🩺 مؤشر صحة الشبكة</div>', unsafe_allow_html=True)
        st.plotly_chart(network_health_gauge(alerts, blocked_ips), use_container_width=True, key=f'gauge_{st.session_state.refresh_count}')
    with col_traffic:
        st.markdown('<div class="chart-title">📈 حركة المرور — آخر 30 دقيقة (مباشر)</div>', unsafe_allow_html=True)
        st.plotly_chart(animated_traffic_chart(alerts), use_container_width=True, key=f'traffic_{st.session_state.refresh_count}')
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    col_sev, col_proto, col_top = st.columns(3)
    with col_sev:
        st.markdown('<div class="chart-title">🎯 توزيع الخطورة</div>', unsafe_allow_html=True)
        fig = severity_donut(alerts)
        if fig: st.plotly_chart(fig, use_container_width=True, key=f'donut_{st.session_state.refresh_count}')
        else: st.info("✅ لا توجد تنبيهات")
    with col_proto:
        st.markdown('<div class="chart-title">🌐 توزيع البروتوكولات</div>', unsafe_allow_html=True)
        fig = protocol_bar(alerts)
        if fig: st.plotly_chart(fig, use_container_width=True, key=f'proto_{st.session_state.refresh_count}')
        else: st.info("لا توجد بيانات")
    with col_top:
        st.markdown('<div class="chart-title">🔝 أكثر المهاجمين نشاطاً</div>', unsafe_allow_html=True)
        fig = top_attackers_chart(alerts)
        if fig: st.plotly_chart(fig, use_container_width=True, key=f'top_{st.session_state.refresh_count}')
        else: st.info("لا توجد بيانات")
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if alerts:
        st.markdown('<div class="chart-title">⚡ آخر 5 تنبيهات</div>', unsafe_allow_html=True)
        for a in reversed(alerts[-5:]):
            sev = a.get('severity', 'MEDIUM')
            cls = 'critical' if sev == 'CRITICAL' else 'high' if sev == 'HIGH' else 'medium'
            badge = f'sev-{cls}'
            ts = a.get('timestamp', '')[-8:]
            st.markdown(f"""
            <div class="alert-row {cls}">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span class="alert-ip">{a.get('src_ip','?')}</span>
                    <span class="severity-badge {badge}">{sev}</span>
                    <span class="alert-time">{ts}</span>
                </div>
                <div class="alert-reason">{a.get('reason','')}</div>
            </div>""", unsafe_allow_html=True)

def alerts_page(alerts):
    page_header("🚨 التنبيهات الحية", f"{len(alerts)} تنبيه مسجّل")
    if not alerts:
        st.success("✅ الشبكة آمنة — لا توجد تنبيهات حالياً")
        return
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي التنبيهات", len(alerts))
    c2.metric("آخر تنبيه", alerts[-1].get('timestamp','')[-8:])
    c3.metric("تنبيهات حرجة", sum(1 for a in alerts if a.get('severity')=='CRITICAL'))
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    severity_filter = st.multiselect("فلتر الخطورة:", ["CRITICAL", "HIGH", "MEDIUM"], default=["CRITICAL", "HIGH"])
    filtered = [a for a in alerts if a.get('severity') in severity_filter]
    st.caption(f"عرض {len(filtered)} تنبيه من {len(alerts)}")
    for a in reversed(filtered[-60:]):
        sev = a.get('severity', 'MEDIUM')
        cls = 'critical' if sev == 'CRITICAL' else 'high' if sev == 'HIGH' else 'medium'
        badge = f'sev-{cls}'
        st.markdown(f"""
        <div class="alert-row {cls}">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
                <span class="alert-ip">{a.get('src_ip','?')}</span>
                <span class="severity-badge {badge}">{sev}</span>
                <span class="alert-time">{a.get('timestamp','')}</span>
            </div>
            <div class="alert-reason" style="margin-top:6px;">{a.get('reason','')}</div>
            <div style="margin-top:4px;font-size:0.75rem;color:#2a4a6a;">
                البروتوكول: {a.get('protocol','TCP')} &nbsp;|&nbsp; درجة الشذوذ: {a.get('score',0):.1%}
            </div>
        </div>""", unsafe_allow_html=True)

def blocked_ips_page(blocked_ips):
    page_header("🔒 الأجهزة المعزولة", f"{len(blocked_ips)} جهاز تحت العزل")
    if not blocked_ips:
        st.success("✅ لا توجد أجهزة معزولة — الشبكة نظيفة!")
        return
    c1, c2 = st.columns(2)
    c1.metric("إجمالي المعزولة", len(blocked_ips))
    c2.metric("عزل حرج", sum(1 for i in blocked_ips.values() if i.get('severity')=='CRITICAL'))
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    for ip, info in blocked_ips.items():
        sev = info.get('severity', 'HIGH')
        st.markdown(f"""
        <div class="blocked-card">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="color:#ff6688;font-weight:700;font-size:1rem;">{ip}</span>
                <span class="severity-badge sev-{'critical' if sev=='CRITICAL' else 'high'}">{sev}</span>
                <span class="alert-time">{info.get('blocked_at','')[-19:]}</span>
            </div>
            <div class="alert-reason" style="margin-top:6px;">{info.get('reason','')[:80]}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("🔓 رفع الحجب")
    selected = st.selectbox("اختر جهازاً:", list(blocked_ips.keys()))
    col1, col2 = st.columns([3,1])
    with col1: st.info(f"سيتم رفع الحجب عن: **{selected}**")
    with col2:
        if st.button("🔓 رفع الحجب"):
            try:
                res = requests.post(f"{API_BASE_URL}/api/block/unblock", json={"ip": selected, "reason": "تم رفع الحظر من لوحة التحكم", "admin_user": "dashboard_admin"}, timeout=5)
                if res.status_code == 200:
                    st.success(f"✅ تم رفع الحجب عن {selected}")
                    st.rerun()
                else: st.error("❌ فشل رفع الحجب من الـ API")
            except: st.error("❌ لا يمكن الاتصال بالـ API")

def settings_page():
    page_header("⚙️ الإعدادات المتقدمة", "ضبط معاملات نظام الدفاع")
    config = load_json(CONFIG_FILE, {"threshold":0.7,"capture_mode":"simulate","auto_block":True,"proactive_mode":True})
    whitelist = load_json(WHITELIST_FILE, ["127.0.0.1","::1"])
    st.subheader("🎯 إعدادات الكشف والدفاع")
    col1, col2 = st.columns(2)
    with col1: new_threshold = st.slider("عتبة الكشف (Threshold):", 0.0, 1.0, float(config.get("threshold", 0.7)), 0.05)
    with col2: auto_block = st.checkbox("تفعيل الحظر التلقائي", value=config.get("auto_block", True))
    proactive_mode = st.checkbox("تفعيل الدفاع الاستباقي", value=config.get("proactive_mode", True))
    st.markdown("---")
    st.subheader("📱 إعدادات تنبيهات تلجرام")
    telegram_enabled = st.checkbox("تفعيل تنبيهات تلجرام", value=config.get("telegram_enabled", False))
    col1, col2 = st.columns(2)
    with col1: telegram_token = st.text_input("🔑 رمز البوت (Bot Token):", value=config.get("telegram_token", ""), type="password")
    with col2: telegram_chat_id = st.text_input("💬 معرف الدردشة (Chat ID):", value=config.get("telegram_chat_id", ""))
    st.markdown("---")
    st.subheader("⚪ القائمة البيضاء")
    new_ip = st.text_input("أضف عنوان IP:", placeholder="192.168.1.1")
    if st.button("➕ إضافة للقائمة البيضاء"):
        if new_ip and new_ip not in whitelist:
            whitelist.append(new_ip)
            save_json(WHITELIST_FILE, whitelist)
            st.success(f"✅ تم إضافة {new_ip}")
            st.rerun()
    for ip in whitelist:
        c1, c2 = st.columns([5,1])
        c1.write(f"• {ip}")
        if c2.button("❌", key=f"rm_{ip}"):
            whitelist.remove(ip)
            save_json(WHITELIST_FILE, whitelist)
            st.rerun()
    st.markdown("---")
    if st.button("💾 حفظ جميع الإعدادات"):
        config.update({"threshold":new_threshold, "auto_block":auto_block, "proactive_mode":proactive_mode, "telegram_enabled":telegram_enabled, "telegram_token":telegram_token, "telegram_chat_id":telegram_chat_id})
        save_json(CONFIG_FILE, config)
        st.success("✅ تم حفظ الإعدادات بنجاح!")

def fetch_api_data(endpoint, default):
    try:
        res = requests.get(f"{API_BASE_URL}{endpoint}", timeout=2)
        if res.status_code == 200:
            data = res.json()
            # التعامل مع هيكل الرد المختلف من الـ API
            if "alerts" in data: return data["alerts"]
            if "blocked_ips" in data: return data["blocked_ips"]
            return data
    except:
        pass
    return default

def main():
    # محاولة جلب البيانات من الـ API أولاً، ثم الملفات المحلية كخيار احتياطي
    alerts = fetch_api_data("/api/alerts", load_json(ALERTS_FILE, []))
    blocked_ips = fetch_api_data("/api/blocked", load_json(BLOCKED_IPS_FILE, {}))
    with st.sidebar:
        st.markdown("<div style='text-align:center;padding:12px 0 6px;'><div style='font-size:2rem;'>🛡️</div><div style='font-size:1rem;font-weight:900;color:#e0e6f0;'>المدافع الذكي</div><div style='font-size:0.72rem;color:#4a6a8a;margin-top:2px;'>Smart Defender v4.0</div></div>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#1e2d4a;margin:8px 0;'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.markdown(f"<div class='sidebar-stat'><div class='val'>{len(alerts)}</div><div class='lbl'>تنبيه</div></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='sidebar-stat'><div class='val' style='color:#ff4466;'>{len(blocked_ips)}</div><div class='lbl'>معزول</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='refresh-counter'>🔄 تحديث #{st.session_state.refresh_count} &nbsp;|&nbsp; كل {AUTO_REFRESH_SECS}ث</div>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#1e2d4a;margin:10px 0;'>", unsafe_allow_html=True)
        page = st.radio("التنقل:", ["📊 لوحة التحكم", "🚨 التنبيهات", "🔒 الأجهزة المعزولة", "⚙️ الإعدادات"], label_visibility="collapsed")
        st.markdown("<hr style='border-color:#1e2d4a;margin:10px 0;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;'><span class='live-badge'><span class='pulse-ring'></span> مباشر — {datetime.now().strftime('%H:%M:%S')}</span></div>", unsafe_allow_html=True)
        st.markdown("<div class='footer-note' style='margin-top:16px;'>Smart Defender v4.0<br>Proactive AI Security</div>", unsafe_allow_html=True)

    if page == "📊 لوحة التحكم": dashboard_page(alerts, blocked_ips)
    elif page == "🚨 التنبيهات": alerts_page(alerts)
    elif page == "🔒 الأجهزة المعزولة": blocked_ips_page(blocked_ips)
    elif page == "⚙️ الإعدادات": settings_page()

    st.session_state.prev_alert_count = len(alerts)
    st.session_state.prev_blocked_count = len(blocked_ips)
    st.session_state.refresh_count += 1
    time.sleep(AUTO_REFRESH_SECS)
    st.rerun()

if __name__ == "__main__":
    main()
