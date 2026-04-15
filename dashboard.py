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

# 🛡️ إعدادات الصفحة المتقدمة
st.set_page_config(
    page_title="المدافع الذكي - Smart Defender v4.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 تصميم CSS احترافي ومتطور (Dark Cyber Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
    }

    .stApp {
        background: #050a15;
        color: #e0e6f0;
    }

    /* تحسين القائمة الجانبية */
    section[data-testid="stSidebar"] {
        background: #081020;
        border-left: 1px solid #1e2d4a;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #00d4ff;
        text-align: right;
        font-weight: 900;
    }

    /* بطاقات المقاييس المتطورة */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #0d1b35 0%, #0a1428 100%);
        border: 1px solid #1e3560;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: #00d4ff;
        box-shadow: 0 12px 40px rgba(0,212,255,0.15);
    }

    div[data-testid="metric-container"] label {
        color: #7aa3cc !important;
        font-size: 0.9rem;
        font-weight: 600;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2.4rem;
        font-weight: 900;
        text-shadow: 0 0 10px rgba(0,212,255,0.3);
    }

    /* رأس الصفحة المخصص */
    .page-header {
        background: linear-gradient(90deg, #0d1b35 0%, #0a1428 100%);
        border: 1px solid #1e3560;
        border-radius: 20px;
        padding: 25px 35px;
        margin-bottom: 30px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    }

    .page-title {
        font-size: 1.8rem;
        font-weight: 900;
        color: #ffffff;
        margin: 0;
        background: linear-gradient(45deg, #00d4ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: rgba(0,255,136,0.1);
        border: 1px solid rgba(0,255,136,0.3);
        border-radius: 30px;
        padding: 8px 18px;
        color: #00ff88;
        font-size: 0.9rem;
        font-weight: 700;
    }

    .pulse-ring {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #00ff88;
        box-shadow: 0 0 0 0 rgba(0,255,136,0.7);
        animation: livepulse 2s infinite;
    }

    @keyframes livepulse {
        0%   { box-shadow: 0 0 0 0 rgba(0,255,136,0.7); }
        70%  { box-shadow: 0 0 0 15px rgba(0,255,136,0); }
        100% { box-shadow: 0 0 0 0 rgba(0,255,136,0); }
    }

    /* عناوين المخططات */
    .chart-title {
        color: #7aa3cc;
        font-size: 1rem;
        font-weight: 700;
        text-align: right;
        margin-bottom: 15px;
        padding-right: 10px;
        border-right: 4px solid #00d4ff;
    }

    /* صفوف التنبيهات */
    .alert-row {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        transition: all 0.2s;
    }

    .alert-row:hover {
        background: rgba(255,255,255,0.05);
        transform: scale(1.01);
    }

    .alert-row.critical { border-right: 5px solid #ff4444; background: linear-gradient(90deg, rgba(255,68,68,0.05), transparent); }
    .alert-row.high { border-right: 5px solid #ff8800; background: linear-gradient(90deg, rgba(255,136,0,0.05), transparent); }
    .alert-row.medium { border-right: 5px solid #88cc00; background: linear-gradient(90deg, rgba(136,204,0,0.05), transparent); }

    .alert-ip { color: #00d4ff; font-weight: 700; font-size: 1.1rem; }
    .severity-badge {
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
    }
    .sev-critical { background: #ff4444; color: white; }
    .sev-high { background: #ff8800; color: white; }
    .sev-medium { background: #88cc00; color: white; }

    /* تخصيص الأزرار */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0070cc 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 25px;
        font-weight: 700;
        transition: all 0.3s;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,212,255,0.4);
        background: linear-gradient(135deg, #00e5ff 0%, #0080ee 100%);
    }

    /* تخصيص المدخلات */
    .stTextInput input, .stSelectbox select {
        background-color: #0d1b35 !important;
        border: 1px solid #1e3560 !important;
        color: white !important;
        border-radius: 8px !important;
    }

    hr { border-color: #1e2d4a; margin: 25px 0; }
</style>
""", unsafe_allow_html=True)

# 📁 إدارة المسارات والبيانات
DATA_DIR = Path("defender_system/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "models").mkdir(parents=True, exist_ok=True)

ALERTS_FILE = DATA_DIR / "alerts.json"
BLOCKED_IPS_FILE = DATA_DIR / "blocked_ips.json"
CONFIG_FILE = DATA_DIR / "config.json"
WHITELIST_FILE = DATA_DIR / "whitelist.json"

API_BASE_URL = os.environ.get("API_BASE_URL", "https://sh-production-5beb.up.railway.app").rstrip("/")
AUTO_REFRESH_SECS = 3

# 🔄 تهيئة حالة الجلسة
for key, default in [
    ('prev_alert_count', 0),
    ('prev_blocked_count', 0),
    ('refresh_count', 0),
    ('traffic_history', []),
    ('last_tick', time.time()),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# 🛠️ وظائف مساعدة
def load_json(path, default):
    if path.exists():
        try: return json.loads(path.read_text())
        except: return default
    return default

def save_json(path, data):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e: st.error(f"❌ خطأ في الحفظ: {e}")

def dark_plotly(fig, height=280):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Cairo, sans-serif', color='#7aa3cc'),
        margin=dict(l=10, r=10, t=30, b=10),
        height=height,
        hovermode='x unified',
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#7aa3cc')),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', zeroline=False),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    )
    return fig

# 📊 وظائف المخططات والرسوم البيانية
def build_traffic_history(alerts):
    now = datetime.now()
    buckets = {}
    for i in range(30):
        t = (now - timedelta(minutes=i)).strftime('%H:%M')
        buckets[t] = {'total': 0, 'critical': 0, 'high': 0}
    for a in alerts:
        try:
            ts = datetime.fromisoformat(a.get('timestamp', ''))
            label = ts.strftime('%H:%M')
            if label in buckets:
                buckets[label]['total'] += 1
                if a.get('severity') == 'CRITICAL': buckets[label]['critical'] += 1
                elif a.get('severity') == 'HIGH': buckets[label]['high'] += 1
        except: pass
    times = sorted(buckets.keys())
    return times, buckets

def animated_traffic_chart(alerts):
    times, buckets = build_traffic_history(alerts)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=[buckets[t]['total'] for t in times], name='إجمالي التنبيهات', fill='tozeroy', line=dict(color='#00d4ff', width=3)))
    fig.add_trace(go.Scatter(x=times, y=[buckets[t]['critical'] for t in times], name='حرجة', line=dict(color='#ff4444', width=2)))
    return dark_plotly(fig, height=300)

def network_health_gauge(alerts, blocked_ips):
    critical = sum(1 for a in alerts if a.get('severity') == 'CRITICAL')
    blocked = len(blocked_ips)
    health = max(0, min(100, 100 - (critical * 5) - (blocked * 2)))
    color = '#00ff88' if health > 75 else '#ffaa00' if health > 40 else '#ff4444'
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=health,
        number={'suffix': "%", 'font': {'color': color, 'size': 40}},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': color}, 'bgcolor': "rgba(0,0,0,0)",
               'steps': [{'range': [0, 40], 'color': "rgba(255,0,0,0.1)"}, {'range': [40, 75], 'color': "rgba(255,165,0,0.1)"}]}
    ))
    return dark_plotly(fig, height=250)

def severity_donut(alerts):
    if not alerts: return None
    counts = pd.Series([a.get('severity', 'MEDIUM') for a in alerts]).value_counts()
    fig = go.Figure(go.Pie(labels=counts.index, values=counts.values, hole=.6, marker=dict(colors=['#ff4444', '#ff8800', '#88cc00'])))
    return dark_plotly(fig, height=250)

def protocol_bar(alerts):
    if not alerts: return None
    counts = pd.Series([a.get('protocol', 'TCP') for a in alerts]).value_counts()
    fig = go.Figure(go.Bar(x=counts.index, y=counts.values, marker_color='#00d4ff'))
    return dark_plotly(fig, height=250)

def top_attackers_chart(alerts):
    if not alerts: return None
    top = pd.Series([a.get('src_ip', '?') for a in alerts]).value_counts().head(5)
    fig = go.Figure(go.Bar(y=top.index, x=top.values, orientation='h', marker_color='#ff4444'))
    return dark_plotly(fig, height=250)

# 📄 صفحات التطبيق
def page_header(title, subtitle=""):
    st.markdown(f"""
    <div class="page-header">
        <div>
            <div class="page-title">{title}</div>
            <div style="color:#7aa3cc;font-size:0.95rem;margin-top:6px;">{subtitle}</div>
        </div>
        <div class="live-badge">
            <div class="pulse-ring"></div>
            مباشر — {datetime.now().strftime('%H:%M:%S')}
        </div>
    </div>""", unsafe_allow_html=True)

def dashboard_page(alerts, blocked_ips):
    page_header("📊 لوحة التحكم الأمنية", "مراقبة استباقية وتحليل فوري للتهديدات")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚨 إجمالي التنبيهات", len(alerts), delta=f"+{len(alerts)-st.session_state.prev_alert_count}" if len(alerts)>st.session_state.prev_alert_count else None)
    c2.metric("🔒 الأجهزة المعزولة", len(blocked_ips))
    c3.metric("🔴 تهديدات حرجة", sum(1 for a in alerts if a.get('severity')=='CRITICAL'))
    c4.metric("🟢 حالة النظام", "آمن")

    st.markdown("---")
    
    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.markdown('<div class="chart-title">🩺 مؤشر صحة الشبكة</div>', unsafe_allow_html=True)
        st.plotly_chart(network_health_gauge(alerts, blocked_ips), use_container_width=True)
    with col_right:
        st.markdown('<div class="chart-title">📈 نشاط الشبكة (آخر 30 دقيقة)</div>', unsafe_allow_html=True)
        st.plotly_chart(animated_traffic_chart(alerts), use_container_width=True)

    st.markdown("---")
    
    c_sev, c_proto, c_top = st.columns(3)
    with c_sev:
        st.markdown('<div class="chart-title">🎯 توزيع الخطورة</div>', unsafe_allow_html=True)
        fig = severity_donut(alerts)
        if fig: st.plotly_chart(fig, use_container_width=True)
        else: st.info("لا توجد بيانات")
    with c_proto:
        st.markdown('<div class="chart-title">🌐 البروتوكولات</div>', unsafe_allow_html=True)
        fig = protocol_bar(alerts)
        if fig: st.plotly_chart(fig, use_container_width=True)
        else: st.info("لا توجد بيانات")
    with c_top:
        st.markdown('<div class="chart-title">🔝 أخطر المصادر</div>', unsafe_allow_html=True)
        fig = top_attackers_chart(alerts)
        if fig: st.plotly_chart(fig, use_container_width=True)
        else: st.info("لا توجد بيانات")

def alerts_page(alerts):
    page_header("🚨 سجل التنبيهات", f"تم رصد {len(alerts)} نشاط مشبوه")
    if not alerts:
        st.success("✅ لا توجد تنبيهات حالياً")
        return
    
    for a in reversed(alerts[-50:]):
        sev = a.get('severity', 'MEDIUM')
        cls = sev.lower()
        st.markdown(f"""
        <div class="alert-row {cls}">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span class="alert-ip">{a.get('src_ip','?')}</span>
                <span class="severity-badge sev-{cls}">{sev}</span>
                <span style="color:#5577aa;font-size:0.8rem;">{a.get('timestamp','')}</span>
            </div>
            <div style="margin-top:10px;color:#aabccc;">{a.get('reason','')}</div>
            <div style="margin-top:8px;font-size:0.75rem;color:#4a6a8a;">البروتوكول: {a.get('protocol','TCP')} | الدرجة: {a.get('score',0):.2%}</div>
        </div>""", unsafe_allow_html=True)

def settings_page():
    page_header("⚙️ الإعدادات المتقدمة", "تخصيص معايير الدفاع وتنبيهات التليجرام")
    
    config = load_json(CONFIG_FILE, {"threshold":0.7,"auto_block":True,"proactive_mode":True})
    
    st.subheader("🎯 معايير الكشف")
    col1, col2 = st.columns(2)
    with col1: new_threshold = st.slider("عتبة الحظر (Threshold):", 0.0, 1.0, float(config.get("threshold", 0.7)), 0.05)
    with col2: auto_block = st.checkbox("تفعيل الحظر التلقائي الذكي", value=config.get("auto_block", True))
    
    st.markdown("---")
    st.subheader("📱 إعدادات التليجرام (مزامنة فورية)")
    st.warning("⚠️ سيتم إرسال هذه الإعدادات مباشرة إلى المحرك الدفاعي (Sh) لضمان عمل التنبيهات.")
    
    telegram_enabled = st.checkbox("تفعيل تنبيهات تلجرام", value=config.get("telegram_enabled", False))
    c_t1, c_t2 = st.columns(2)
    with c_t1: telegram_token = st.text_input("🔑 Bot Token:", value=config.get("telegram_token", ""), type="password")
    with c_t2: telegram_chat_id = st.text_input("💬 Chat ID:", value=config.get("telegram_chat_id", ""))
    
    if st.button("🚀 مزامنة وتفعيل التليجرام"):
        try:
            payload = {"telegram_enabled": telegram_enabled, "telegram_token": telegram_token, "telegram_chat_id": telegram_chat_id}
            res = requests.post(f"{API_BASE_URL}/api/config/telegram", json=payload, timeout=5)
            if res.status_code == 200: st.success("✅ تم تحديث الإعدادات على الخادم واختبار الاتصال!")
            else: st.error(f"❌ فشل الاتصال بالخادم: {res.status_code}")
        except Exception as e: st.error(f"❌ خطأ تقني: {e}")

    if st.button("💾 حفظ الإعدادات المحلية"):
        config.update({"threshold":new_threshold, "auto_block":auto_block, "telegram_enabled":telegram_enabled, "telegram_token":telegram_token, "telegram_chat_id":telegram_chat_id})
        save_json(CONFIG_FILE, config)
        st.success("✅ تم الحفظ محلياً")

def main():
    # جلب البيانات من الـ API
    try:
        res_a = requests.get(f"{API_BASE_URL}/api/alerts", timeout=2)
        alerts = res_a.json().get("alerts", []) if res_a.status_code==200 else []
        res_b = requests.get(f"{API_BASE_URL}/api/blocked", timeout=2)
        blocked_ips = res_b.json().get("blocked_ips", {}) if res_b.status_code==200 else {}
    except:
        alerts = load_json(ALERTS_FILE, [])
        blocked_ips = load_json(BLOCKED_IPS_FILE, {})

    with st.sidebar:
        st.markdown("<div style='text-align:center;padding:20px;'><h2 style='margin:0;'>🛡️ المدافع</h2><p style='color:#4a6a8a;'>v4.0 Enhanced</p></div>", unsafe_allow_html=True)
        page = st.radio("القائمة:", ["📊 لوحة التحكم", "🚨 سجل التنبيهات", "⚙️ الإعدادات"])
        st.markdown("---")
        st.info(f"🔄 تحديث رقم: {st.session_state.refresh_count}")

    if page == "📊 لوحة التحكم": dashboard_page(alerts, blocked_ips)
    elif page == "🚨 سجل التنبيهات": alerts_page(alerts)
    elif page == "⚙️ الإعدادات": settings_page()

    st.session_state.prev_alert_count = len(alerts)
    st.session_state.refresh_count += 1
    time.sleep(AUTO_REFRESH_SECS)
    st.rerun()

if __name__ == "__main__":
    main()
