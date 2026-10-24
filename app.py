import math
import random
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

from detector import detect_possible_leak


# =========================================================
# HYDRANEXUS // WAKANDA CONTROL SYSTEM
# =========================================================
st.set_page_config(
    page_title="HydraNexus | Water Intelligence Command",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- THEME ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Orbitron:wght@500;600;700;800;900&display=swap');

    :root {
        --bg:#030812; --panel:#091729; --panel2:#0d2037;
        --cyan:#35e7ff; --blue:#397dff; --green:#39f5a5;
        --red:#ff405d; --amber:#ffc857; --muted:#91abc7;
        --white:#eaf7ff;
    }
    html, body, [class*="css"] { font-family:Inter,sans-serif; }
    .stApp {
        background:
          radial-gradient(ellipse at 50% -12%, #123b60 0%, transparent 43%),
          radial-gradient(ellipse at 100% 45%, #09233b 0%, transparent 35%),
          linear-gradient(145deg,#030812,#06101f 58%,#030812);
        color:var(--white);
    }
    [data-testid="stSidebar"] {
        background:linear-gradient(180deg,#07182c,#030914);
        border-right:1px solid #17476a;
    }
    [data-testid="stSidebar"] * { color:#d8efff; }
    h1,h2,h3 { color:#eafaff !important; letter-spacing:-.5px; }
    [data-testid="stMetric"] {
        background:linear-gradient(145deg,#102944,#081526);
        border:1px solid #1a5273; border-radius:15px;
        padding:15px; box-shadow:0 0 24px #00c8ff0b;
    }
    [data-testid="stMetricLabel"] { color:#a5cce8 !important; }
    [data-testid="stMetricValue"] { color:#51e6ff !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color:#174463; border-radius:16px;
    }
    div.stButton > button, div.stDownloadButton > button {
        border:1px solid #28dfff; border-radius:10px;
        background:linear-gradient(110deg,#10417c,#075b7e);
        color:white; font-weight:700; min-height:2.6rem;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        border-color:#b4f8ff; color:white;
        box-shadow:0 0 20px #20dfff44;
    }
    .hn-hero {
        position:relative; overflow:hidden;
        background:linear-gradient(110deg,#102f50,#07182d 62%,#08384a);
        border:1px solid #1b7894; border-radius:20px;
        padding:25px 27px; margin:0 0 17px;
        box-shadow:0 0 35px #00c8ff18,inset 0 0 35px #00c8ff08;
    }
    .hn-hero:after {
        content:""; position:absolute; width:240px;height:240px;
        right:-55px;top:-110px;border:1px solid #3eeaff44;
        border-radius:50%; box-shadow:0 0 0 22px #3eeaff0a,0 0 0 48px #3eeaff08;
    }
    .hn-eyebrow { color:#52eaff; font:700 11px Orbitron,sans-serif; letter-spacing:3px; }
    .hn-title { color:#f0fcff; font:900 clamp(30px,4vw,48px) Orbitron,sans-serif; margin:8px 0 4px; }
    .hn-sub { color:#a9c9e4; font-size:14px; }
    .hn-chip {
        display:inline-block; margin-top:15px; padding:6px 10px;
        border:1px solid #26718e; border-radius:20px;
        color:#8beeff; background:#08253b; font:700 10px Orbitron,sans-serif;
        letter-spacing:1.2px;
    }
    .hn-section {
        color:#65eaff; font:700 13px Orbitron,sans-serif;
        letter-spacing:1.7px; margin:10px 0 12px;
    }
    .hn-panel {
        background:linear-gradient(145deg,#0c2036,#071323);
        border:1px solid #174766; border-radius:16px;
        padding:16px 18px; box-shadow:inset 0 0 24px #0ba8d008;
    }
    .hn-muted { color:#91abc7; font-size:12px; }
    .hn-alert {
        background:linear-gradient(100deg,#3b101e,#220d19);
        border:1px solid #ff405d; border-radius:13px;
        color:#ffdce2; padding:13px 16px; font-weight:800;
        box-shadow:0 0 24px #ff23452b;
        animation:alertGlow 1.25s ease-in-out infinite alternate;
    }
    .hn-ok {
        background:linear-gradient(100deg,#0c342c,#09251f);
        border:1px solid #20b982; border-radius:13px;
        color:#a8ffe0; padding:13px 16px; font-weight:800;
    }
    @keyframes alertGlow {
        from { box-shadow:0 0 8px #ff23451a; }
        to { box-shadow:0 0 27px #ff23456b; }
    }
    .hn-footer { text-align:center; padding:24px 4px 8px; color:#7698b6; font-size:11px; letter-spacing:1px; }
    [data-testid="stDataFrame"] { border:1px solid #174463; border-radius:12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- SIMULATION DATA ----------
SCENARIOS = ["Normal usage", "Possible leak", "Brief spike", "Custom readings"]
SEED_DATA = {
    "Normal usage": [
        .22,.31,.28,.39,.24,.35,.19,.42,.30,.27,
        .38,.23,.32,.26,.41,.29,.34,.21,.37,.30,
    ],
    "Possible leak": [
        .22,.30,.25,.36,.29,.33,.21,.40,.27,.35,
        .31,.24,.38,.28,.34,1.25,1.42,1.51,1.63,1.72,
    ],
    "Brief spike": [
        .22,.30,.25,.36,.29,.33,.21,.40,1.85,.35,
        .31,.24,.38,.28,.34,.26,.32,.23,.37,.29,
    ],
}
random.seed()


def make_seed_history(values):
    now = datetime.now()
    return [
        {"Timestamp": now - timedelta(seconds=3 * (len(values)-i-1)),
         "Flow (L/min)": float(value)}
        for i, value in enumerate(values)
    ]


def next_simulated_reading(scenario, tick):
    if scenario == "Normal usage":
        return round(random.uniform(.15, .48), 2)
    if scenario == "Possible leak":
        return round(random.uniform(.2, .45), 2) if tick < 2 else round(random.uniform(1.25, 1.85), 2)
    if scenario == "Brief spike":
        return round(random.uniform(1.5, 2.0), 2) if tick % 10 == 0 else round(random.uniform(.15, .45), 2)
    return 0.0


def render_sensor_network(is_alert, current, threshold, average, high_count):
    """Animated concept visualization; these are virtual sensor indicators."""
    state = "critical" if is_alert else "normal"
    label = "CRITICAL FLOW SIGNATURE" if is_alert else "NETWORK NOMINAL"
    nodes = ""
    for idx, name in enumerate(["NODE 01", "NODE 02", "NODE 03", "NODE 04"]):
        delay = idx * .18
        nodes += f"""
          <div class="node {state}" style="--delay:{delay}s">
            <div class="node-core"><span></span></div>
            <div class="node-name">{name}</div>
            <div class="node-state">{'ALERT' if is_alert else 'ONLINE'}</div>
          </div>
        """
    color = "#ff405d" if is_alert else "#39f5a5"
    return f"""
    <html><head><style>
      *{{box-sizing:border-box}}
      body{{margin:0;background:transparent;color:#eaf7ff;font-family:Inter,Arial,sans-serif}}
      .shell{{background:linear-gradient(145deg,#07182b,#06101e);border:1px solid #1a5273;border-radius:17px;padding:17px 18px;overflow:hidden}}
      .top{{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap}}
      .title{{font:700 12px Orbitron,Arial;letter-spacing:1.6px;color:#66eaff}}
      .state{{font:700 10px Orbitron,Arial;letter-spacing:1px;color:{color};border:1px solid {color};padding:6px 9px;border-radius:20px}}
      .track{{position:relative;height:8px;margin:55px 20px 0;background:linear-gradient(90deg,#123c5a,#205f7b,#123c5a);border-radius:20px;box-shadow:0 0 12px #20cfff30}}
      .track:before{{content:"";position:absolute;inset:1px;border-radius:20px;background:repeating-linear-gradient(90deg,transparent 0 22px,#6eeeff 23px 29px,transparent 30px 48px);opacity:.7;animation:flow 1.5s linear infinite}}
      @keyframes flow{{from{{background-position:0 0}}to{{background-position:48px 0}}}}
      .nodes{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:-34px;position:relative}}
      .node{{text-align:center;min-width:0}}
      .node-core{{width:42px;height:42px;border-radius:50%;margin:0 auto 9px;background:#0b263d;border:2px solid {color};display:grid;place-items:center;box-shadow:0 0 13px {color}55}}
      .node-core span{{width:13px;height:13px;border-radius:50%;background:{color};box-shadow:0 0 13px {color}}}
      .critical .node-core{{animation:blink .85s steps(2,start) infinite;animation-delay:var(--delay)}}
      .normal .node-core{{animation:softPulse 2.2s ease-in-out infinite;animation-delay:var(--delay)}}
      @keyframes blink{{to{{opacity:.22;box-shadow:0 0 27px #ff405d}}}}
      @keyframes softPulse{{50%{{box-shadow:0 0 23px #39f5a5aa}}}}
      .node-name{{font:700 9px Orbitron,Arial;letter-spacing:.7px;color:#c4e7f7}}
      .node-state{{font:700 9px Inter,Arial;color:{color};margin-top:4px}}
      .stats{{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;margin-top:24px;padding-top:13px;border-top:1px solid #174463;color:#91abc7;font-size:11px}}
      .stats b{{color:#e7faff}}
      .disclaimer{{margin-top:12px;color:#7698b6;font-size:10px;letter-spacing:.3px}}
    </style></head><body>
      <div class="shell">
        <div class="top"><div class="title">VIRTUAL SENSOR NETWORK // PIPELINE A</div><div class="state">{label}</div></div>
        <div class="track"></div>
        <div class="nodes">{nodes}</div>
        <div class="stats">
          <span>LIVE FLOW <b>{current:.2f} L/min</b></span>
          <span>LIMIT <b>{threshold:.2f} L/min</b></span>
          <span>HIGH SAMPLES <b>{high_count}</b></span>
          <span>MEAN <b>{average:.2f} L/min</b></span>
        </div>
        <div class="disclaimer">VIRTUAL INDICATORS — CONCEPTUAL SOFTWARE VISUALIZATION, NOT CONNECTED HARDWARE</div>
      </div>
    </body></html>
    """


def render_audio_alarm(is_alert):
    """Browser-side opt-in alarm. Audio starts only after a user gesture."""
    alert_js = "true" if is_alert else "false"
    html = f"""
    <html><body style="margin:0;background:transparent;font-family:Inter,Arial,sans-serif">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;background:#08182a;border:1px solid {'#a72c43' if is_alert else '#174766'};border-radius:13px;padding:12px 14px;color:#eaf7ff">
        <div>
          <div style="font-size:11px;font-weight:800;letter-spacing:1.3px;color:{'#ff7185' if is_alert else '#70eaff'}">
            {'CRITICAL AUDIO ALERT' if is_alert else 'ACOUSTIC ALERT SYSTEM'}
          </div>
          <div id="audioStatus" style="font-size:11px;color:#9bbbd5;margin-top:4px">
            {'Abnormal sustained high-flow pattern detected.' if is_alert else 'No active critical alert.'}
          </div>
        </div>
        <button id="arm" style="border:1px solid #35dfff;background:#0c3655;color:#eafaff;border-radius:9px;padding:9px 12px;font-weight:700;cursor:pointer">
          ENABLE SOUND
        </button>
        <button id="mute" style="border:1px solid #55718a;background:#14283c;color:#d9efff;border-radius:9px;padding:9px 12px;font-weight:700;cursor:pointer">
          MUTE
        </button>
      </div>
      <script>
        const alertActive = {alert_js};
        let ctx = null, armed = false, muted = false, timer = null;
        const status = document.getElementById('audioStatus');
        const arm = document.getElementById('arm');
        const mute = document.getElementById('mute');

        function beep() {{
          if (!ctx || ctx.state !== 'running' || !armed || muted || !alertActive) return;
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(880, ctx.currentTime);
          gain.gain.setValueAtTime(0.0001, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.16, ctx.currentTime + 0.015);
          gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.20);
          osc.connect(gain); gain.connect(ctx.destination);
          osc.start(); osc.stop(ctx.currentTime + 0.21);
        }}
        arm.addEventListener('click', async () => {{
          try {{
            if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
            await ctx.resume();
            armed = true;
            arm.textContent = 'SOUND ENABLED';
            status.textContent = alertActive ? 'Alarm armed — repeating alert beeps active.' : 'Alarm armed — sound will play only during a critical alert.';
            if (alertActive) {{ beep(); if (!timer) timer = setInterval(beep, 1100); }}
          }} catch(e) {{
            status.textContent = 'Audio unavailable in this browser. Check browser sound permissions.';
          }}
        }});
        mute.addEventListener('click', () => {{
          muted = !muted;
          mute.textContent = muted ? 'UNMUTE' : 'MUTE';
          if (muted) status.textContent = 'Alarm muted.';
          else status.textContent = alertActive ? 'Alarm unmuted — critical alert active.' : 'Alarm unmuted — monitoring.';
        }});
        if (alertActive) {{
          status.textContent += ' Enable sound to hear the warning.';
        }}
      </script>
    </body></html>
    """
    components.html(html, height=86, scrolling=False)


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown(
        """
        <div style="padding:8px 0 18px">
          <div style="font:900 23px Orbitron,sans-serif;color:#50eaff">💧 HYDRANEXUS</div>
          <div style="font:700 9px Orbitron,sans-serif;color:#91b9d8;letter-spacing:1.4px">WATER INTELLIGENCE SYSTEM</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### CONTROL DECK")
    scenario = st.selectbox("Monitoring scenario", SCENARIOS)
    st.markdown("### DETECTION ENGINE")
    threshold = st.slider("High-flow threshold (L/min)", .1, 5.0, 1.0, .1)
    consecutive = st.slider("Consecutive high readings", 1, 10, 3)
    st.caption("Alert condition: the required number of consecutive readings must be strictly above the threshold.")
    st.divider()
    auto_update = st.toggle(
        "Automatic simulated updates",
        value=True,
        disabled=(scenario == "Custom readings"),
    )
    st.caption("Simulation mode only. No physical sensor is connected.")

# ---------- INPUT / SIMULATED HISTORY ----------
if scenario == "Custom readings":
    custom_text = st.text_input(
        "Enter flow readings (L/min), separated by commas",
        value="0.2, 0.3, 1.4, 1.5, 1.6",
    )
    try:
        readings = [float(x.strip()) for x in custom_text.split(",") if x.strip()]
        if not readings:
            raise ValueError("Enter at least one reading.")
        if any(not math.isfinite(x) or x < 0 for x in readings):
            raise ValueError("Readings must be finite, non-negative numbers.")
    except ValueError as error:
        st.error(f"Invalid custom readings: {error}")
        st.stop()

    history = [
        {"Timestamp": datetime.now() - timedelta(seconds=3*(len(readings)-i-1)),
         "Flow (L/min)": value}
        for i, value in enumerate(readings)
    ]
else:
    if st.session_state.get("hydra_scenario") != scenario:
        st.session_state.hydra_scenario = scenario
        st.session_state.hydra_history = make_seed_history(SEED_DATA[scenario])
        st.session_state.hydra_tick = 0
        st.session_state.hydra_last_refresh = -1

    if "hydra_history" not in st.session_state:
        st.session_state.hydra_history = make_seed_history(SEED_DATA[scenario])
        st.session_state.hydra_tick = 0
        st.session_state.hydra_last_refresh = -1

    if auto_update:
        refresh_count = st_autorefresh(
            interval=3000, limit=None, key="hydranexus_auto_refresh"
        )
        if refresh_count != st.session_state.hydra_last_refresh:
            if st.session_state.hydra_last_refresh != -1:
                st.session_state.hydra_tick += 1
                value = next_simulated_reading(scenario, st.session_state.hydra_tick)
                st.session_state.hydra_history.append(
                    {"Timestamp": datetime.now(), "Flow (L/min)": value}
                )
                st.session_state.hydra_history = st.session_state.hydra_history[-60:]
            st.session_state.hydra_last_refresh = refresh_count

    if not auto_update and st.button("↻ Generate next simulated reading"):
        st.session_state.hydra_tick += 1
        value = next_simulated_reading(scenario, st.session_state.hydra_tick)
        st.session_state.hydra_history.append(
            {"Timestamp": datetime.now(), "Flow (L/min)": value}
        )
        st.session_state.hydra_history = st.session_state.hydra_history[-60:]
        st.rerun()

    history = st.session_state.hydra_history
    readings = [row["Flow (L/min)"] for row in history]

# ---------- DETECTION ----------
try:
    possible_leak = bool(detect_possible_leak(
        readings, threshold=threshold, consecutive=consecutive
    ))
except ValueError as error:
    st.error(f"Detection error: {error}")
    st.stop()

data = pd.DataFrame(history)
data["Timestamp"] = pd.to_datetime(data["Timestamp"])
data["Above threshold"] = data["Flow (L/min)"] > threshold
data["Reading number"] = range(1, len(data)+1)

average_flow = float(data["Flow (L/min)"].mean())
peak_flow = float(data["Flow (L/min)"].max())
current_flow = float(data["Flow (L/min)"].iloc[-1])
high_count = int(data["Above threshold"].sum())

# ---------- HERO ----------
st.markdown(
    """
    <div class="hn-hero">
      <div class="hn-eyebrow">DETECT · ANALYZE · CONSERVE // SYSTEM ONLINE</div>
      <div class="hn-title">HYDRANEXUS</div>
      <div class="hn-sub">Intelligent Water Monitoring · Predictive Flow Analytics · Anomaly Intelligence</div>
      <div class="hn-chip">WAKANDA CONTROL INTERFACE // PROTOTYPE BUILD</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "PROTOTYPE DATA NOTICE — Readings are simulated or manually entered. "
    "Virtual sensor indicators and audio alerts are software demonstrations; "
    "no physical sensor is connected. A high-flow alert is not proof of a leak."
)

# ---------- COMMAND STATUS ----------
st.markdown('<div class="hn-section">01 // SYSTEM CONDITION</div>', unsafe_allow_html=True)
if possible_leak:
    st.markdown(
        '<div class="hn-alert">🔴 CRITICAL — SUSTAINED HIGH-FLOW PATTERN DETECTED · INVESTIGATION REQUIRED</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="hn-ok">🟢 SYSTEM NOMINAL — NO SUSTAINED HIGH-FLOW PATTERN DETECTED</div>',
        unsafe_allow_html=True,
    )

render_audio_alarm(possible_leak)

# ---------- METRICS ----------
st.markdown('<div class="hn-section">02 // TELEMETRY</div>', unsafe_allow_html=True)
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Current flow", f"{current_flow:.2f} L/min")
m2.metric("Average flow", f"{average_flow:.2f} L/min")
m3.metric("Peak flow", f"{peak_flow:.2f} L/min")
m4.metric("Total readings", len(readings))
m5.metric("High readings", f"{high_count} / {len(readings)}")

# ---------- VIRTUAL SENSOR NETWORK ----------
st.markdown('<div class="hn-section">03 // DISTRIBUTED SENSOR NETWORK</div>', unsafe_allow_html=True)
components.html(
    render_sensor_network(possible_leak, current_flow, threshold, average_flow, high_count),
    height=265,
    scrolling=False,
)

# ---------- LIVE MONITORING ----------
st.markdown('<div class="hn-section">04 // LIVE FLOW MONITORING</div>', unsafe_allow_html=True)
left, right = st.columns([2.2, 1])
with left:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["Timestamp"], y=data["Flow (L/min)"],
        mode="lines+markers", name="Water flow",
        line=dict(color="#22d3ee", width=3, shape="spline"),
        marker=dict(size=5, color="#67e8f9", line=dict(color="#082f49", width=1)),
        fill="tozeroy", fillcolor="rgba(34,211,238,0.09)",
        hovertemplate="Time: %{x|%H:%M:%S}<br>Flow: %{y:.2f} L/min<extra></extra>",
    ))
    fig.add_hline(
        y=threshold, line_dash="dash", line_color="#ff667d",
        annotation_text=f"Threshold {threshold:.1f} L/min",
        annotation_position="top left",
    )
    fig.update_layout(
        title="WATER FLOW SIGNATURE",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,16,32,.65)",
        font=dict(color="#cdeaff"), height=365,
        margin=dict(l=15,r=15,t=55,b=15),
        xaxis_title="Time", yaxis_title="Flow (L/min)", hovermode="x unified",
        xaxis=dict(gridcolor="#16314a",zerolinecolor="#16314a"),
        yaxis=dict(gridcolor="#16314a",zerolinecolor="#16314a",rangemode="tozero"),
    )
    st.plotly_chart(fig, width="stretch")
with right:
    gauge_color = "#ff405d" if current_flow > threshold else "#22d3ee"
    gauge_max = max(2.0, threshold*2, peak_flow*1.15)
    gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=current_flow,
        number={"suffix":" L/min","font":{"color":"#e4f6ff","size":25}},
        title={"text":"LIVE FLOW RATE","font":{"color":"#7ddfff","size":15}},
        gauge={
            "axis":{"range":[0,gauge_max],"tickcolor":"#9abbd5"},
            "bar":{"color":gauge_color}, "bgcolor":"#0b1a2b",
            "borderwidth":1,"bordercolor":"#164365",
            "steps":[{"range":[0,gauge_max],"color":"#102a43"}],
            "threshold":{"line":{"color":"#ff667d","width":4},"thickness":.8,"value":threshold},
        },
    ))
    gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font={"color":"#cdeaff"},
        height=365, margin=dict(l=15,r=15,t=60,b=15),
    )
    st.plotly_chart(gauge, width="stretch")

# ---------- ANALYTICS ----------
st.markdown('<div class="hn-section">05 // INTELLIGENCE & ANALYTICS</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    distribution = px.histogram(
        data, x="Flow (L/min)", nbins=10, title="FLOW DISTRIBUTION",
        color_discrete_sequence=["#22d3ee"],
    )
    distribution.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(5,16,32,.65)",
        font=dict(color="#cdeaff"),height=310,
        margin=dict(l=15,r=15,t=55,b=15),
        xaxis=dict(gridcolor="#16314a"),yaxis=dict(gridcolor="#16314a"),
    )
    st.plotly_chart(distribution, width="stretch")
with c2:
    trend = px.area(
        data,x="Reading number",y="Flow (L/min)",title="SEQUENTIAL READING ANALYSIS",
        color_discrete_sequence=["#4f8cff"],
    )
    trend.add_hline(y=threshold,line_dash="dash",line_color="#ff667d")
    trend.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(5,16,32,.65)",
        font=dict(color="#cdeaff"),height=310,
        margin=dict(l=15,r=15,t=55,b=15),
        xaxis=dict(gridcolor="#16314a"),yaxis=dict(gridcolor="#16314a",rangemode="tozero"),
    )
    st.plotly_chart(trend, width="stretch")

# ---------- SENSOR INSTALLATION CONCEPT ----------
st.markdown('<div class="hn-section">06 // HARDWARE INTEGRATION BLUEPRINT</div>', unsafe_allow_html=True)
sensor_col, info_col = st.columns([1.5,1])
with sensor_col:
    st.markdown(
        """
        <div class="hn-panel">
          <svg viewBox="0 0 680 245" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto">
            <defs>
              <linearGradient id="pipehn" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#8db6d3"/><stop offset="50%" stop-color="#315979"/><stop offset="100%" stop-color="#17344f"/>
              </linearGradient>
              <filter id="glowhn"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
            </defs>
            <path d="M35 145 H645" stroke="url(#pipehn)" stroke-width="48" stroke-linecap="round"/>
            <path d="M35 132 H645" stroke="#9ccde8" stroke-width="3" opacity=".7"/>
            <path d="M35 158 H645" stroke="#061222" stroke-width="3"/>
            <g fill="#5ba4d0" stroke="#a7dfff" stroke-width="2">
              <rect x="80" y="115" width="18" height="60" rx="4"/><rect x="580" y="115" width="18" height="60" rx="4"/>
            </g>
            <g filter="url(#glowhn)">
              <rect x="283" y="66" width="114" height="58" rx="13" fill="#132b44" stroke="#2ce4ff" stroke-width="2"/>
              <path d="M305 66 L320 42 H360 L375 66" fill="#174e78" stroke="#2ce4ff" stroke-width="2"/>
              <rect x="318" y="20" width="44" height="24" rx="7" fill="#1264ad" stroke="#a1f5ff" stroke-width="2"/>
              <circle cx="340" cy="94" r="12" fill="#0a1d31" stroke="#35e7ff" stroke-width="2"/>
              <path d="M334 94 L340 87 L346 94 L340 101Z" fill="#51edff"/>
            </g>
            <path d="M340 20 V8 H450" fill="none" stroke="#35dfff" stroke-width="2"/>
            <text x="458" y="12" fill="#65e8ff" font-size="14" font-weight="700">FLOW SENSOR</text>
            <text x="45" y="91" fill="#9ac9e9" font-size="12">FLOW DIRECTION →</text>
            <path d="M45 101 H155 M143 92 L155 101 L143 110" fill="none" stroke="#35dfff" stroke-width="2"/>
            <text x="25" y="218" fill="#789cb9" font-size="11">CONCEPTUAL HARDWARE LAYOUT — NOT A CONNECTED DEVICE</text>
          </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )
with info_col:
    st.markdown(
        """
        <div class="hn-panel">
          <div style="font:700 12px Orbitron;color:#65eaff;letter-spacing:1px;margin-bottom:12px">INTEGRATION PIPELINE</div>
          <p>01 &nbsp; Flow sensor measures water movement.</p>
          <p>02 &nbsp; Controller acquires sensor signals.</p>
          <p>03 &nbsp; Software processes timestamped readings.</p>
          <p>04 &nbsp; Detection engine evaluates patterns.</p>
          <p>05 &nbsp; Alert interface notifies an operator.</p>
          <hr style="border-color:#174766">
          <div class="hn-muted">Physical sensor and controller integration are planned future enhancements.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- EVENT LOG & EXPORT ----------
st.markdown('<div class="hn-section">07 // EVENT LOG & DATA EXPORT</div>', unsafe_allow_html=True)
recent = data.tail(12).sort_values("Timestamp",ascending=False).copy()
recent_display = recent[["Reading number","Timestamp","Flow (L/min)","Above threshold"]].copy()
recent_display["Timestamp"] = recent_display["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
st.dataframe(recent_display,width="stretch",hide_index=True)

csv_data = data[["Reading number","Timestamp","Flow (L/min)","Above threshold"]].to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇ EXPORT TELEMETRY AS CSV",
    data=csv_data,
    file_name="hydranexus_readings.csv",
    mime="text/csv",
)

st.markdown(
    """
    <div class="hn-footer">
      HYDRANEXUS // DETECT. ANALYZE. CONSERVE.<br>
      WATER INTELLIGENCE COMMAND INTERFACE · SOFTWARE PROTOTYPE
    </div>
    """,
    unsafe_allow_html=True,
)
