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
    page_title="HYDRANEXUS 2050 | Nexus Command",
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

    /* ===== HYDRANEXUS 2050 VISUAL SYSTEM ===== */
    @keyframes gridDrift {
        from { background-position: 0 0, 0 0; }
        to { background-position: 0 46px, 46px 0; }
    }
    @keyframes scanSweep {
        0% { transform: translateY(-120%); opacity: 0; }
        12% { opacity: .35; }
        88% { opacity: .18; }
        100% { transform: translateY(520%); opacity: 0; }
    }
    @keyframes orbitSpin { to { transform: rotate(360deg); } }
    @keyframes orbitReverse { to { transform: rotate(-360deg); } }
    @keyframes breathe {
        0%,100% { opacity:.55; filter:drop-shadow(0 0 5px #35e7ff); }
        50% { opacity:1; filter:drop-shadow(0 0 15px #35e7ff); }
    }
    @keyframes riseIn {
        from { opacity:0; transform:translateY(12px); }
        to { opacity:1; transform:translateY(0); }
    }
    .stApp {
        background-image:
          linear-gradient(rgba(35,190,230,.035) 1px, transparent 1px),
          linear-gradient(90deg, rgba(35,190,230,.035) 1px, transparent 1px),
          radial-gradient(ellipse at 50% -12%, #123b60 0%, transparent 43%),
          radial-gradient(ellipse at 100% 45%, #09233b 0%, transparent 35%),
          linear-gradient(145deg,#030812,#06101f 58%,#030812) !important;
        background-size: 46px 46px,46px 46px,auto,auto,auto;
        animation:gridDrift 24s linear infinite;
    }
    .stApp:before {
        content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
        background:linear-gradient(180deg,transparent 0%,rgba(53,231,255,.035) 50%,transparent 100%);
        height:24%; animation:scanSweep 12s linear infinite;
    }
    [data-testid="stHeader"] { background:rgba(3,8,18,.72); backdrop-filter:blur(16px); }
    [data-testid="stSidebar"] {
        background:linear-gradient(180deg,rgba(7,24,44,.97),rgba(3,9,20,.98)) !important;
        border-right:1px solid rgba(53,231,255,.32);
        box-shadow:12px 0 45px rgba(0,190,255,.06);
    }
    [data-testid="stSidebar"] > div { background:transparent; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color:#b8d8ed; letter-spacing:.35px;
    }
    [data-testid="stMetric"] {
        position:relative; overflow:hidden;
        background:linear-gradient(145deg,rgba(16,41,68,.94),rgba(5,17,32,.94)) !important;
        border:1px solid rgba(53,231,255,.34) !important;
        border-radius:15px !important; padding:17px 16px !important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,.04),0 8px 28px rgba(0,0,0,.22),0 0 20px rgba(0,200,255,.045);
        transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease;
        animation:riseIn .55s ease both;
    }
    [data-testid="stMetric"]:hover {
        transform:translateY(-4px); border-color:#58edff !important;
        box-shadow:0 12px 34px rgba(0,200,255,.13);
    }
    [data-testid="stMetricLabel"] { color:#9fc8e5 !important; font-size:.78rem !important; letter-spacing:1px; text-transform:uppercase; }
    [data-testid="stMetricValue"] { color:#70efff !important; font-family:Orbitron,Inter,sans-serif; text-shadow:0 0 15px rgba(53,231,255,.25); }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background:linear-gradient(145deg,rgba(10,29,49,.72),rgba(5,15,28,.78));
        border:1px solid rgba(44,151,190,.35) !important;
        border-radius:17px !important; box-shadow:0 12px 34px rgba(0,0,0,.14);
    }
    div.stButton > button, div.stDownloadButton > button {
        border:1px solid rgba(53,231,255,.75) !important; border-radius:10px !important;
        background:linear-gradient(115deg,#123d70,#075b70 65%,#087c83) !important;
        color:#f1fdff !important; font-weight:800 !important; letter-spacing:.5px;
        min-height:2.7rem; box-shadow:0 0 18px rgba(0,210,255,.10);
        transition:all .2s ease;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        transform:translateY(-2px); border-color:#c5fbff !important;
        box-shadow:0 0 25px rgba(32,223,255,.32),inset 0 0 16px rgba(32,223,255,.08);
    }
    .stSelectbox [data-baseweb="select"] > div,
    .stTextInput input, .stNumberInput input {
        background:rgba(7,25,43,.92) !important; border-color:#245778 !important; color:#eafaff !important;
    }
    .stSlider [data-baseweb="slider"] div[role="slider"] { box-shadow:0 0 12px #35e7ff; }
    .stToggle [data-testid="stWidgetLabel"] p { color:#c5e8f7; }
    .stPlotlyChart, [data-testid="stDataFrame"] {
        border:1px solid rgba(40,133,172,.34); border-radius:15px;
        background:rgba(5,17,31,.55); padding:5px;
        box-shadow:0 10px 28px rgba(0,0,0,.15);
    }
    .hn-hero {
        position:relative; isolation:isolate; overflow:hidden;
        background:
          radial-gradient(circle at 82% 48%,rgba(28,205,255,.18),transparent 23%),
          linear-gradient(112deg,rgba(12,43,72,.98),rgba(5,18,34,.98) 57%,rgba(5,52,66,.96));
        border:1px solid rgba(53,231,255,.58); border-radius:22px;
        padding:30px 32px; margin:4px 0 18px;
        box-shadow:0 0 45px rgba(0,195,255,.12),inset 0 0 45px rgba(0,195,255,.055);
        animation:riseIn .7s ease both;
    }
    .hn-hero:before {
        content:""; position:absolute; inset:0; z-index:-1; opacity:.34;
        background-image:linear-gradient(rgba(70,220,255,.12) 1px,transparent 1px),linear-gradient(90deg,rgba(70,220,255,.12) 1px,transparent 1px);
        background-size:28px 28px; mask-image:linear-gradient(90deg,black,transparent 88%);
    }
    .hn-hero:after {
        content:""; position:absolute; width:220px;height:220px;right:7%;top:50%;
        transform:translateY(-50%); border:1px solid rgba(69,232,255,.35);
        border-radius:50%; box-shadow:0 0 0 16px rgba(62,234,255,.045),0 0 0 34px rgba(62,234,255,.035),0 0 0 55px rgba(62,234,255,.025),inset 0 0 35px rgba(62,234,255,.12);
        animation:orbitSpin 32s linear infinite;
    }
    .hn-title { text-shadow:0 0 24px rgba(53,231,255,.28); }
    .hn-chip { box-shadow:0 0 18px rgba(53,231,255,.10); }
    .hn-section {
        display:flex; align-items:center; gap:12px;
        color:#75edff !important; font:800 12px Orbitron,sans-serif;
        letter-spacing:2px; margin:20px 0 13px; text-shadow:0 0 12px rgba(53,231,255,.22);
    }
    .hn-section:after { content:""; height:1px; flex:1; background:linear-gradient(90deg,rgba(53,231,255,.55),transparent); }
    .hn-panel { border:1px solid rgba(53,231,255,.28); box-shadow:inset 0 0 28px rgba(11,168,208,.045),0 10px 28px rgba(0,0,0,.16); }
    .hn-alert { border-width:1px; box-shadow:0 0 28px rgba(255,35,69,.18),inset 0 0 20px rgba(255,35,69,.06); }
    .hn-ok { box-shadow:0 0 22px rgba(32,185,130,.10),inset 0 0 18px rgba(32,185,130,.05); }
    .hn-footer { border-top:1px solid rgba(53,231,255,.18); margin-top:24px; }
    [data-testid="stDataFrame"] { background:rgba(5,17,31,.75); }
    ::-webkit-scrollbar { width:9px; height:9px; }
    ::-webkit-scrollbar-track { background:#030b16; }
    ::-webkit-scrollbar-thumb { background:linear-gradient(#1c7897,#123653); border-radius:10px; }
    @media (max-width: 760px) {
        .hn-hero { padding:23px 19px; }
        .hn-hero:after { opacity:.25; right:-90px; }
        .hn-title { font-size:30px !important; }
    }


    /* ===== NEXUS COMMAND DECK: STRUCTURAL REDESIGN ===== */
    .block-container {max-width: 1500px; padding-top: 1.4rem; padding-bottom: 3rem;}
    .nx-topbar {
      display:flex; justify-content:space-between; align-items:center; gap:18px;
      padding:10px 15px; margin:0 0 16px; border:1px solid #1c506b;
      border-radius:12px; background:linear-gradient(90deg,#071827,#0b263b 55%,#071827);
      font:700 10px Orbitron,sans-serif; letter-spacing:1.4px; color:#9fc8dd;
    }
    .nx-live {color:#5af0bd; text-shadow:0 0 12px #39f5a5;}
    .nx-hero-grid {
      display:grid; grid-template-columns:1.45fr .75fr; gap:18px; align-items:stretch;
      margin:0 0 16px;
    }
    .nx-hero-main {
      position:relative; overflow:hidden; min-height:245px; padding:28px 30px;
      border:1px solid #247b9b; border-radius:20px;
      background:radial-gradient(circle at 85% 45%,#0b5870 0%,transparent 28%),
      linear-gradient(120deg,#102f4a,#071525 64%,#092b39);
      box-shadow:0 16px 55px #0008,inset 0 0 40px #20dfff0c;
    }
    .nx-hero-main:after {
      content:""; position:absolute; width:340px; height:340px; right:-100px; top:-50px;
      border:1px solid #55eaff33; border-radius:50%;
      box-shadow:0 0 0 22px #55eaff0b,0 0 0 48px #55eaff08,0 0 0 78px #55eaff05;
      pointer-events:none;
    }
    .nx-kicker {font:700 10px Orbitron,sans-serif; color:#60eaff; letter-spacing:3px;}
    .nx-brand {font:900 clamp(32px,5vw,58px) Orbitron,sans-serif; color:#f0fcff;
      letter-spacing:1px; line-height:1.15; margin:13px 0 8px; text-shadow:0 0 25px #35e7ff55;}
    .nx-description {font-size:13px; color:#a7c6db; max-width:620px; line-height:1.7;}
    .nx-tags {display:flex; flex-wrap:wrap; gap:8px; margin-top:22px;}
    .nx-tag {padding:7px 10px; border:1px solid #28637c; border-radius:5px;
      background:#08243a; color:#a5eaff; font:700 9px Orbitron,sans-serif; letter-spacing:1px;}
    .nx-core {
      min-height:245px; display:flex; flex-direction:column; justify-content:center; align-items:center;
      text-align:center; padding:20px; border:1px solid #1d617d; border-radius:20px;
      background:linear-gradient(155deg,#0b2034,#06111e); position:relative; overflow:hidden;
    }
    .nx-orbit {width:132px;height:132px;border:1px solid #35dfff88;border-radius:50%;
      display:grid;place-items:center; position:relative; margin-bottom:12px;
      box-shadow:0 0 35px #16dfff24,inset 0 0 25px #16dfff18;}
    .nx-orbit:before,.nx-orbit:after {content:"";position:absolute;border:1px dashed #42dfff66;border-radius:50%;inset:10px;animation:orbitSpin 18s linear infinite;}
    .nx-orbit:after {inset:-9px;border-style:solid;border-color:#35e7ff33;animation:orbitReverse 24s linear infinite;}
    .nx-orbit-core {width:66px;height:66px;border-radius:50%;display:grid;place-items:center;
      background:radial-gradient(circle,#1d819d,#0b2c43 70%);color:#a9f8ff;
      font:900 22px Orbitron,sans-serif;box-shadow:0 0 28px #20dfff66;}
    .nx-core-label {font:700 10px Orbitron,sans-serif;letter-spacing:2px;color:#65eaff;}
    .nx-core-state {font-size:12px;color:#a6c5d9;margin-top:6px;}
    .nx-section-title {font:800 12px Orbitron,sans-serif;letter-spacing:2px;color:#6beaff;
      margin:17px 0 11px; display:flex;align-items:center;gap:12px;}
    .nx-section-title:after {content:"";height:1px;flex:1;background:linear-gradient(90deg,#27708d,transparent);}
    .nx-mini-card {background:linear-gradient(145deg,#0d263e,#071421);border:1px solid #1b506d;
      border-radius:13px;padding:13px 15px;min-height:84px;}
    .nx-mini-label {font:700 9px Orbitron,sans-serif;color:#91b8d0;letter-spacing:1.2px;}
    .nx-mini-value {font:800 22px Orbitron,sans-serif;color:#65eaff;margin-top:8px;}
    .nx-mini-foot {font-size:10px;color:#7397af;margin-top:3px;}
    .nx-alert-card {border:1px solid #ff536d;background:linear-gradient(110deg,#351321,#180d1a);
      padding:17px 19px;border-radius:14px;color:#ffe4e9;box-shadow:0 0 28px #ff405d20;}
    .nx-safe-card {border:1px solid #23b985;background:linear-gradient(110deg,#0d332b,#091d1b);
      padding:17px 19px;border-radius:14px;color:#c5ffeb;}
    .nx-info-card {border:1px solid #1d536e;background:linear-gradient(145deg,#0b2034,#071421);
      border-radius:14px;padding:17px 18px;height:100%;}
    .nx-info-label {font:700 10px Orbitron,sans-serif;color:#69eaff;letter-spacing:1.4px;margin-bottom:9px;}
    .nx-info-copy {font-size:12px;color:#a5c0d4;line-height:1.75;}
    .stTabs [data-baseweb="tab-list"] {gap:7px;border-bottom:1px solid #19435c;}
    .stTabs [data-baseweb="tab"] {background:#091a2b;border:1px solid #173d56;border-radius:9px 9px 0 0;
      padding:10px 16px;color:#9bbbd0;font:700 10px Orbitron,sans-serif;letter-spacing:.8px;}
    .stTabs [aria-selected="true"] {background:#10354d !important;color:#71edff !important;border-color:#2b9ab7 !important;}
    .nx-footer {text-align:center;border-top:1px solid #1a455d;padding:22px 5px 5px;margin-top:30px;
      color:#7194aa;font:700 9px Orbitron,sans-serif;letter-spacing:1.5px;}
    @media(max-width:850px){.nx-hero-grid{grid-template-columns:1fr}.nx-hero-main:after{opacity:.25}}

    @keyframes nexusScan { 0% { transform:translateX(-110%); } 100% { transform:translateX(110%); } }
    .nx-hero-main { position:relative; }
    .nx-hero-main:after { content:""; position:absolute; left:0; bottom:-12px; height:2px; width:45%;
      background:linear-gradient(90deg,transparent,#42eaff,transparent); animation:nexusScan 5s linear infinite; }
    .nx-mini-card { transition:transform .25s ease,border-color .25s ease,box-shadow .25s ease; }
    .nx-mini-card:hover { transform:translateY(-4px); border-color:#4ceaff; box-shadow:0 0 22px #22dfff30; }
    @media (prefers-reduced-motion: reduce) { *, *:before, *:after { animation:none !important; transition:none !important; } }
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



def render_holo_pipeline(is_alert, current, threshold, average, high_count):
    """Animated holographic pipe network. All nodes are illustrative software graphics."""
    state = "CRITICAL" if is_alert else "NOMINAL"
    accent = "#ff4968" if is_alert else "#35e7ff"
    glow = "rgba(255,73,104,.55)" if is_alert else "rgba(53,231,255,.42)"
    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      *{{box-sizing:border-box}} body{{margin:0;background:transparent;color:#eafaff;font-family:Inter,Arial,sans-serif}}
      html,body{{width:100%;min-height:100%;overflow:hidden}}
      .frame{{position:relative;overflow:hidden;border:1px solid #1d7894;border-radius:19px;padding:17px 18px 18px;
        background:radial-gradient(ellipse at 50% 45%,#0b3450 0%,#07192b 55%,#040d19 100%);box-shadow:0 0 32px {glow},inset 0 0 35px #16cfff0c}}
      .frame:before{{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(transparent 49%,#35e7ff0b 50%,transparent 51%);background-size:100% 7px;opacity:.5}}
      .head{{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;position:relative;z-index:2}}
      .eyebrow{{font:800 11px Orbitron,Arial;letter-spacing:2px;color:#71edff}}
      .pill{{font:800 9px Orbitron,Arial;letter-spacing:1.4px;color:{accent};border:1px solid {accent};padding:6px 10px;border-radius:20px;box-shadow:0 0 15px {glow}}}
      .stage{{position:relative;margin-top:13px;margin-bottom:10px;padding-bottom:4px}}
      svg{{width:100%;height:auto;display:block;overflow:visible}}
      .pipe{{fill:none;stroke:#1b5575;stroke-width:18;stroke-linecap:round;opacity:.75}}
      .pipeInner{{fill:none;stroke:#28c8ee;stroke-width:3;stroke-linecap:round;stroke-dasharray:12 15;animation:water 1s linear infinite;filter:drop-shadow(0 0 5px #27dfff)}}
      .branch{{fill:none;stroke:#24769a;stroke-width:8;stroke-linecap:round}}
      .branchFlow{{fill:none;stroke:#50eaff;stroke-width:2;stroke-dasharray:5 12;animation:water .8s linear infinite}}
      .sensor{{transform-box:fill-box;transform-origin:center;animation:sensorPulse 2s ease-in-out infinite;filter:drop-shadow(0 0 8px {accent})}}
      .sensor:nth-of-type(2){{animation-delay:.35s}} .sensor:nth-of-type(3){{animation-delay:.7s}} .sensor:nth-of-type(4){{animation-delay:1.05s}}
      .orbit{{fill:none;stroke:{accent};stroke-width:1.5;stroke-dasharray:4 7;transform-box:fill-box;transform-origin:center;animation:spin 7s linear infinite}}
      .ping{{fill:none;stroke:{accent};stroke-width:2;transform-box:fill-box;transform-origin:center;animation:ping 2s ease-out infinite}}
      .packet{{fill:#c4fbff;filter:drop-shadow(0 0 6px #6cf4ff);offset-path:path('M 55 130 C 220 130 240 75 390 75 S 560 150 720 130');animation:travel 5s linear infinite}}
      .packet.p2{{animation-delay:-2.5s;fill:#49f3d0}}
      .scan{{stroke:#7af5ff;stroke-width:1.5;opacity:.6;animation:scan 4s ease-in-out infinite}}
      .nodeLabel{{font:700 10px Orbitron,Arial;fill:#bfefff;letter-spacing:1px}}
      .nodeSub{{font:600 8px Inter,Arial;fill:#79a9c6;letter-spacing:1px}}
      .readout{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:8px;position:relative;z-index:2}}
      .cell{{background:#071a2c;border:1px solid #1b506c;border-radius:10px;padding:9px 10px;min-width:0}}
      .cell span{{display:block;color:#78a9c5;font:700 8px Orbitron,Arial;letter-spacing:1px}}
      .cell b{{display:block;color:#e9fbff;font:800 15px Orbitron,Arial;margin-top:5px;white-space:nowrap}}
      .foot{{color:#739bb7;font-size:9px;letter-spacing:.5px;margin-top:13px;padding-top:4px;display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}}
      @keyframes water{{to{{stroke-dashoffset:-54}}}} @keyframes spin{{to{{transform:rotate(360deg)}}}}
      @keyframes sensorPulse{{0%,100%{{transform:scale(.94);opacity:.78}}50%{{transform:scale(1.12);opacity:1}}}}
      @keyframes ping{{0%{{transform:scale(.7);opacity:.8}}100%{{transform:scale(2.5);opacity:0}}}}
      @keyframes travel{{0%{{offset-distance:0%;opacity:0}}8%{{opacity:1}}92%{{opacity:1}}100%{{offset-distance:100%;opacity:0}}}}
      @keyframes scan{{0%,100%{{opacity:.1}}50%{{opacity:.85}}}}
      @media(max-width:600px){{.readout{{grid-template-columns:repeat(2,1fr)}}.nodeLabel{{font-size:8px}}}}
      @media(prefers-reduced-motion:reduce){{*,*:before,*:after{{animation:none!important}}}}
    </style></head><body>
    <div class="frame"><div class="head"><div class="eyebrow">NEXUS HOLOGRAPHIC PIPE GRID / SECTOR 07</div><div class="pill">● {state} // SIMULATION</div></div>
    <div class="stage"><svg viewBox="0 0 780 245" role="img" aria-label="Animated conceptual water pipeline with virtual sensor nodes">
      <defs><radialGradient id="core"><stop offset="0" stop-color="#d9ffff"/><stop offset=".35" stop-color="{accent}"/><stop offset="1" stop-color="#08769a"/></radialGradient></defs>
      <path class="pipe" d="M55 130 C220 130 240 75 390 75 S560 150 720 130"/><path class="pipeInner" d="M55 130 C220 130 240 75 390 75 S560 150 720 130"/>
      <path class="branch" d="M225 116 L225 190 M515 112 L515 190"/><path class="branchFlow" d="M225 116 L225 190 M515 112 L515 190"/>
      <path class="scan" d="M390 25 L390 210"/><path class="scan" d="M30 75 L750 75"/>
      <g class="sensor"><circle class="ping" cx="115" cy="126" r="17"/><circle class="orbit" cx="115" cy="126" r="23"/><circle cx="115" cy="126" r="13" fill="url(#core)"/><circle cx="115" cy="126" r="4" fill="#fff"/><text class="nodeLabel" x="115" y="166" text-anchor="middle">SENSOR 01</text><text class="nodeSub" x="115" y="180" text-anchor="middle">INLET</text></g>
      <g class="sensor"><circle class="ping" cx="315" cy="91" r="17"/><circle class="orbit" cx="315" cy="91" r="23"/><circle cx="315" cy="91" r="13" fill="url(#core)"/><circle cx="315" cy="91" r="4" fill="#fff"/><text class="nodeLabel" x="315" y="48" text-anchor="middle">SENSOR 02</text><text class="nodeSub" x="315" y="36" text-anchor="middle">MIDLINE</text></g>
      <g class="sensor"><circle class="ping" cx="515" cy="119" r="17"/><circle class="orbit" cx="515" cy="119" r="23"/><circle cx="515" cy="119" r="13" fill="url(#core)"/><circle cx="515" cy="119" r="4" fill="#fff"/><text class="nodeLabel" x="515" y="164" text-anchor="middle">SENSOR 03</text><text class="nodeSub" x="515" y="178" text-anchor="middle">JUNCTION</text></g>
      <g class="sensor"><circle class="ping" cx="690" cy="133" r="17"/><circle class="orbit" cx="690" cy="133" r="23"/><circle cx="690" cy="133" r="13" fill="url(#core)"/><circle cx="690" cy="133" r="4" fill="#fff"/><text class="nodeLabel" x="690" y="176" text-anchor="middle">SENSOR 04</text><text class="nodeSub" x="690" y="190" text-anchor="middle">OUTLET</text></g>
      <circle class="packet" r="5"/><circle class="packet p2" r="3.5"/>
      <text x="34" y="224" class="nodeSub">FLOW VECTOR // CONCEPTUAL PARTICLE SIMULATION</text><text x="746" y="224" text-anchor="end" class="nodeSub">PIPELINE A → D</text>
    </svg></div>
    <div class="readout"><div class="cell"><span>LIVE FLOW</span><b>{current:.2f} L/min</b></div><div class="cell"><span>THRESHOLD</span><b>{threshold:.2f} L/min</b></div><div class="cell"><span>AVERAGE</span><b>{average:.2f} L/min</b></div><div class="cell"><span>HIGH SAMPLES</span><b>{high_count}</b></div></div>
    <div class="foot"><span>● MOTION ENGINE ACTIVE</span><span>VIRTUAL NODES · NOT PHYSICAL SENSOR CONNECTIONS</span></div></div></body></html>"""


def render_audio_alarm(is_alert):
    """Opt-in browser alarm with adjustable, bounded intensity."""
    alert_js = "true" if is_alert else "false"
    html = f"""
    <html><body style="margin:0;background:transparent;font-family:Arial,sans-serif">
    <style>
    @keyframes pulse {{50%{{box-shadow:0 0 24px #ff405d99}}}}
    .alarm{{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;background:linear-gradient(100deg,#101a30,#241326);border:1px solid {'#ff405d' if is_alert else '#174766'};border-radius:13px;padding:12px 14px;color:#eaf7ff;animation:{'pulse 1.2s infinite' if is_alert else 'none'}}}
    button{{border:1px solid #35dfff;background:#0c3655;color:#eafaff;border-radius:9px;padding:9px 12px;font-weight:800;cursor:pointer}}
    input{{accent-color:#ff536d;width:100px}}
    </style>
    <div class="alarm">
      <div><b style="font-size:11px;letter-spacing:1px;color:{'#ff7185' if is_alert else '#70eaff'}">{'▲ PRIORITY AUDIO ALERT' if is_alert else 'ACOUSTIC MONITOR / STANDBY'}</b>
      <div id="status" style="font-size:11px;color:#b4c9dc;margin-top:5px">{'Sustained high-flow pattern flagged.' if is_alert else 'No active critical alert.'}</div></div>
      <label style="font-size:10px">INTENSITY <input id="level" type="range" min="5" max="24" value="18"></label>
      <button id="arm">ENABLE ALARM</button><button id="mute">MUTE</button>
    </div>
    <script>
    const active=__ALERT__; let ctx=null,armed=false,muted=false,timer=null,level=.15;
    const status=document.getElementById('status'),arm=document.getElementById('arm'),mute=document.getElementById('mute');
    document.getElementById('level').addEventListener('input',e=>level=Number(e.target.value)/100);
    function tone(freq,duration,delay=0){{
      if(!ctx||ctx.state!=='running'||!armed||muted||!active)return;
      const o=ctx.createOscillator(),g=ctx.createGain(),t=ctx.currentTime+delay;
      o.type='sawtooth';o.frequency.setValueAtTime(freq,t);g.gain.setValueAtTime(.0001,t);
      g.gain.exponentialRampToValueAtTime(level,t+.025);g.gain.exponentialRampToValueAtTime(.0001,t+duration);
      o.connect(g);g.connect(ctx.destination);o.start(t);o.stop(t+duration+.02);
    }}
    function cycle(){{if(active&&armed&&!muted){{
      tone(660,.16,0);tone(880,.16,.19);tone(1100,.20,.38);
      tone(880,.16,.78);tone(1100,.20,.97);tone(1320,.22,1.16);
    }}}}
    arm.onclick=async()=>{{try{{if(!ctx)ctx=new(window.AudioContext||window.webkitAudioContext)();await ctx.resume();armed=true;arm.textContent='ALARM ARMED';status.textContent=active?'Repeating three-tone warning armed.':'Armed; sound is reserved for critical alerts.';if(active){{cycle();if(!timer)timer=setInterval(cycle,2100);}}}}catch(e){{status.textContent='Audio unavailable; check browser permissions.';}}}};
    mute.onclick=()=>{{muted=!muted;mute.textContent=muted?'UNMUTE':'MUTE';status.textContent=muted?'Audio muted. Visual alert remains active.':'Audio restored.';if(!muted)cycle();}};
    if(active)status.textContent+=' Enable alarm to hear the warning.';
    </script></body></html>"""
    html=html.replace("__ALERT__",alert_js)
    components.html(html,height=105,scrolling=False)


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
        value=False,
        disabled=(scenario == "Custom readings"),
        help="When enabled, Streamlit refreshes the dashboard periodically. Keep it off for uninterrupted animations.",
    )
    st.caption("For smooth, uninterrupted animations, leave automatic updates OFF and use the manual reading button. Simulation only; no physical sensor is connected.")

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
            interval=10000, limit=None, key="hydranexus_auto_refresh"
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


# ---------- NEXUS COMMAND DECK ----------
status_color = "#ff536d" if possible_leak else "#39f5a5"
status_text = "ANOMALY SIGNATURE" if possible_leak else "NOMINAL OPERATION"
status_symbol = "!" if possible_leak else "✓"

st.markdown(
    f"""
    <div class="nx-topbar">
      <span>HYDRANEXUS <span style="color:#4de6ff">//</span> NEXUS COMMAND DECK</span>
      <span>PROTOTYPE BUILD 01 · 2050 UI CONCEPT</span>
      <span class="nx-live">● SYSTEM ONLINE</span>
    </div>
    <div class="nx-hero-grid">
      <div class="nx-hero-main">
        <div class="nx-kicker">WATER INTELLIGENCE / DISTRIBUTED MONITORING</div>
        <div class="nx-brand">HYDRANEXUS</div>
        <div class="nx-description">
          A flow-signature intelligence interface designed to identify sustained
          high-flow patterns, inspect telemetry and support water-conservation decisions.
        </div>
        <div class="nx-tags">
          <span class="nx-tag">DETECT</span><span class="nx-tag">ANALYZE</span>
          <span class="nx-tag">CONSERVE</span><span class="nx-tag">SIMULATION MODE</span>
        </div>
      </div>
      <div class="nx-core">
        <div class="nx-orbit"><div class="nx-orbit-core">{status_symbol}</div></div>
        <div class="nx-core-label">NEXUS CORE STATUS</div>
        <div style="font:800 13px Orbitron;color:{status_color};margin-top:8px">{status_text}</div>
        <div class="nx-core-state">Flow intelligence engine · Active</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "PROTOTYPE DATA NOTICE — Readings are simulated or manually entered. "
    "The virtual sensor network is a software visualization, not connected hardware. "
    "A high-flow alert indicates a pattern requiring investigation; it does not prove a leak."
)

st.markdown('<div class="nx-section-title">LIVE SYSTEM SNAPSHOT</div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="nx-mini-card"><div class="nx-mini-label">CURRENT FLOW</div><div class="nx-mini-value">{current_flow:.2f}<span style="font-size:11px"> L/min</span></div><div class="nx-mini-foot">Latest simulated/manual sample</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="nx-mini-card"><div class="nx-mini-label">AVERAGE FLOW</div><div class="nx-mini-value">{average_flow:.2f}<span style="font-size:11px"> L/min</span></div><div class="nx-mini-foot">Across {len(readings)} readings</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="nx-mini-card"><div class="nx-mini-label">PEAK FLOW</div><div class="nx-mini-value">{peak_flow:.2f}<span style="font-size:11px"> L/min</span></div><div class="nx-mini-foot">Maximum observed sample</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="nx-mini-card"><div class="nx-mini-label">HIGH SAMPLES</div><div class="nx-mini-value">{high_count}<span style="font-size:11px"> / {len(readings)}</span></div><div class="nx-mini-foot">Above {threshold:.2f} L/min threshold</div></div>', unsafe_allow_html=True)

st.markdown('<div class="nx-section-title">COMMAND WORKSPACES</div>', unsafe_allow_html=True)
tab_overview, tab_telemetry, tab_intel, tab_network, tab_events, tab_sim, tab_diag, tab_ops = st.tabs([
    "◈ OVERVIEW", "⌁ TELEMETRY", "✳ INTELLIGENCE", "◎ SENSOR NETWORK",
    "▤ EVENT LOG", "⟁ SIMULATION LAB", "⌬ DIAGNOSTICS", "◉ CONTROL ROOM"
])

# Shared chart constructors
def style_plot(fig, height=350):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,16,32,.72)",
        font=dict(color="#cdeaff"), height=height,
        margin=dict(l=18, r=18, t=55, b=18),
        xaxis=dict(gridcolor="#16314a", zerolinecolor="#16314a"),
        yaxis=dict(gridcolor="#16314a", zerolinecolor="#16314a", rangemode="tozero"),
        title_font=dict(family="Orbitron", size=13, color="#72eaff"),
        hoverlabel=dict(bgcolor="#0b263b", font_color="#eafaff"),
    )
    return fig

flow_fig = go.Figure()
flow_fig.add_trace(go.Scatter(
    x=data["Timestamp"], y=data["Flow (L/min)"], mode="lines+markers",
    name="Flow signature", line=dict(color="#29d9f2", width=3, shape="spline"),
    marker=dict(size=5, color="#8af3ff"), fill="tozeroy",
    fillcolor="rgba(34,211,238,.11)",
    hovertemplate="%{x|%H:%M:%S}<br><b>%{y:.2f} L/min</b><extra></extra>",
))
flow_fig.add_hline(y=threshold, line_dash="dash", line_color="#ff647b",
                   annotation_text=f"LIMIT {threshold:.2f} L/min")
flow_fig.update_layout(title="LIVE FLOW SIGNATURE", xaxis_title="Timestamp",
                       yaxis_title="Flow rate (L/min)", hovermode="x unified")
flow_fig = style_plot(flow_fig, 390)

gauge_color = "#ff536d" if current_flow > threshold else "#25d8e8"
gauge_max = max(2.0, threshold * 2, peak_flow * 1.15)
gauge = go.Figure(go.Indicator(
    mode="gauge+number", value=current_flow,
    number={"suffix": " L/min", "font": {"color": "#e4f6ff", "size": 25}},
    title={"text": "CURRENT FLOW RATE", "font": {"color": "#72eaff", "size": 13}},
    gauge={
        "axis": {"range": [0, gauge_max], "tickcolor": "#9abbd5"},
        "bar": {"color": gauge_color}, "bgcolor": "#0b1a2b",
        "borderwidth": 1, "bordercolor": "#164365",
        "steps": [{"range": [0, gauge_max], "color": "#102a43"}],
        "threshold": {"line": {"color": "#ff667d", "width": 4},
                      "thickness": .8, "value": threshold},
    },
))
gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": "#cdeaff"},
                    height=330, margin=dict(l=15, r=15, t=55, b=10))

with tab_overview:
    st.markdown('<div class="nx-section-title">01 / OPERATIONAL OVERVIEW</div>', unsafe_allow_html=True)
    if possible_leak:
        st.markdown(
            '<div class="nx-alert-card"><b>▲ CRITICAL FLOW PATTERN</b><br>'
            'Sustained high-flow readings meet the configured detection condition. '
            'Inspect the readings and investigate the source.</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="nx-safe-card"><b>✓ SYSTEM NOMINAL</b><br>'
            'No sustained high-flow pattern currently meets the configured alert condition.</div>',
            unsafe_allow_html=True)
    render_audio_alarm(possible_leak)
    st.markdown('<div class="nx-section-title">HOLOGRAPHIC LIVE PIPELINE</div>', unsafe_allow_html=True)
    components.html(render_holo_pipeline(possible_leak, current_flow, threshold, average_flow, high_count), height=500, scrolling=False)
    a, b = st.columns([1.7, 1])
    with a:
        st.plotly_chart(flow_fig, width="stretch", key="flow_chart_overview")
    with b:
        st.plotly_chart(gauge, width="stretch", key="flow_gauge_overview")
    x, y = st.columns(2)
    with x:
        st.markdown('<div class="nx-info-card"><div class="nx-info-label">ACTIVE SCENARIO</div>'
                    f'<div style="font:800 17px Orbitron;color:#eafaff">{scenario.upper()}</div>'
                    '<div class="nx-info-copy">Use the control deck to switch between normal usage, '
                    'possible leak, brief spike and custom readings.</div></div>', unsafe_allow_html=True)
    with y:
        st.markdown('<div class="nx-info-card"><div class="nx-info-label">DETECTION CONFIGURATION</div>'
                    f'<div style="font:800 17px Orbitron;color:#eafaff">{threshold:.2f} L/min</div>'
                    f'<div class="nx-info-copy">Threshold · {consecutive} consecutive readings required '
                    'to trigger the sustained high-flow detector.</div></div>', unsafe_allow_html=True)

with tab_telemetry:
    st.markdown('<div class="nx-section-title">02 / TELEMETRY LAB</div>', unsafe_allow_html=True)
    left, right = st.columns([1.6, 1])
    with left:
        st.plotly_chart(flow_fig, width="stretch", key="flow_chart_telemetry")
    with right:
        st.plotly_chart(gauge, width="stretch", key="flow_gauge_telemetry")
    dist = px.histogram(data, x="Flow (L/min)", nbins=12, title="FLOW DISTRIBUTION",
                        color_discrete_sequence=["#31d8ed"])
    dist = style_plot(dist, 300)
    st.plotly_chart(dist, width="stretch", key="reading_distribution")
    st.caption("Telemetry values are derived from the current simulation or manually entered readings.")

with tab_intel:
    st.markdown('<div class="nx-section-title">03 / ANOMALY INTELLIGENCE</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1.1, 1])
    with c1:
        if possible_leak:
            st.markdown('<div class="nx-alert-card"><b>DETECTION RESULT: PATTERN FLAGGED</b><br>'
                        'The detector identified the configured number of consecutive readings '
                        'strictly above the threshold.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="nx-safe-card"><b>DETECTION RESULT: NO SUSTAINED PATTERN</b><br>'
                        'The current sequence does not satisfy the configured consecutive-reading condition.</div>',
                        unsafe_allow_html=True)
        st.markdown('<div class="nx-info-card" style="margin-top:12px"><div class="nx-info-label">RULE CONFIGURATION</div>'
                    f'<div class="nx-info-copy">Threshold: <b>{threshold:.2f} L/min</b><br>'
                    f'Required consecutive samples: <b>{consecutive}</b><br>'
                    f'Samples above threshold: <b>{high_count}</b><br>'
                    f'Current reading: <b>{current_flow:.2f} L/min</b></div></div>',
                    unsafe_allow_html=True)
    with c2:
        trend = px.area(data, x="Reading number", y="Flow (L/min)",
                        title="SEQUENTIAL PATTERN ANALYSIS",
                        color_discrete_sequence=["#558dff"])
        trend.add_hline(y=threshold, line_dash="dash", line_color="#ff647b")
        trend = style_plot(trend, 340)
        st.plotly_chart(trend, width="stretch", key="reading_trend")
    st.markdown('<div class="nx-info-card"><div class="nx-info-label">INTERPRETATION</div>'
                '<div class="nx-info-copy">A brief high reading may be a transient spike. '
                'The detector checks a consecutive sequence above the selected threshold. '
                'A flagged pattern is an alert for investigation, not confirmation of a leak.</div></div>',
                unsafe_allow_html=True)
    st.markdown('<div class="nx-section-title">FUTURE HARDWARE INTEGRATION PIPELINE</div>', unsafe_allow_html=True)
    h1, h2, h3, h4, h5 = st.columns(5)
    steps = [("01", "FLOW SENSOR"), ("02", "CONTROLLER"), ("03", "TELEMETRY"),
             ("04", "DETECTION"), ("05", "OPERATOR ALERT")]
    for col, (num, label) in zip([h1, h2, h3, h4, h5], steps):
        with col:
            st.markdown(f'<div class="nx-mini-card"><div class="nx-mini-label">{num}</div>'
                        f'<div style="font:700 11px Orbitron;color:#bcefff;margin-top:10px">{label}</div></div>',
                        unsafe_allow_html=True)
    st.caption("Conceptual future architecture only. Physical sensor/controller integration is not implemented.")

with tab_network:
    st.markdown('<div class="nx-section-title">04 / DISTRIBUTED VIRTUAL NETWORK</div>', unsafe_allow_html=True)
    components.html(render_holo_pipeline(possible_leak, current_flow, threshold, average_flow, high_count), height=500, scrolling=False)
    st.markdown('<div class="nx-section-title">NODE STATUS MATRIX</div>', unsafe_allow_html=True)
    components.html(
        render_sensor_network(possible_leak, current_flow, threshold, average_flow, high_count),
        height=265, scrolling=False,
    )
    st.markdown('<div class="nx-info-card"><div class="nx-info-label">NETWORK MODEL</div>'
                '<div class="nx-info-copy">Four animated node indicators represent a conceptual '
                'distributed monitoring layout. They are visual elements in this software prototype '
                'and do not represent live physical sensor connections.</div></div>', unsafe_allow_html=True)

with tab_events:
    st.markdown('<div class="nx-section-title">05 / EVENT STREAM & DATA EXPORT</div>', unsafe_allow_html=True)
    recent = data.tail(20).sort_values("Timestamp", ascending=False).copy()
    recent_display = recent[["Reading number", "Timestamp", "Flow (L/min)", "Above threshold"]].copy()
    recent_display["Timestamp"] = recent_display["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(recent_display, width="stretch", hide_index=True)
    csv_data = data[["Reading number", "Timestamp", "Flow (L/min)", "Above threshold"]].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ EXPORT COMPLETE TELEMETRY AS CSV",
        data=csv_data, file_name="hydranexus_readings.csv", mime="text/csv",
        use_container_width=True,
    )
    st.caption(f"{len(data)} records available in the current session.")

with tab_sim:
    st.markdown('<div class="nx-section-title">06 / SCENARIO SIMULATION LAB</div>', unsafe_allow_html=True)
    st.markdown('<div class="nx-info-card"><div class="nx-info-label">MISSION CONTROL</div><div class="nx-info-copy">Use the sidebar scenarios to observe detector behavior. This lab uses software-generated or manually entered readings only.</div></div>', unsafe_allow_html=True)
    phase = "ALERT SIGNATURE" if possible_leak else ("TRANSIENT ACTIVITY" if scenario == "Brief spike" else "BASELINE SIGNATURE")
    phase_color = "#ff536d" if possible_leak else "#35e7ff"
    st.markdown(f"""<div style="margin-top:14px;padding:20px;border:1px solid {phase_color};border-radius:16px;background:linear-gradient(110deg,#0a1b30,#10172a);box-shadow:0 0 25px {phase_color}22">
      <div style="font:800 11px Orbitron;color:{phase_color};letter-spacing:2px">SIMULATION STATE // {phase}</div>
      <div style="font:800 25px Orbitron;color:#effaff;margin-top:12px">{scenario.upper()}</div>
      <div style="height:12px;border-radius:20px;background:#142b42;margin-top:18px;overflow:hidden"><div style="height:100%;width:{min(100, high_count/max(1,len(readings))*100):.1f}%;background:linear-gradient(90deg,#2bdcf4,#ff536d)"></div></div>
      <div style="font-size:11px;color:#9bbbd5;margin-top:9px">Samples above threshold: {high_count}/{len(readings)}</div></div>""", unsafe_allow_html=True)
    st.markdown("**Scenario interpretation**")
    if scenario == "Possible leak": st.warning("This scenario intentionally generates sustained high readings. It is a test signal, not confirmation of a real leak.")
    elif scenario == "Brief spike": st.info("This scenario introduces temporary peaks. Compare them with the consecutive-reading rule.")
    elif scenario == "Custom readings": st.info("Custom values are manually entered test data; verify units and context.")
    else: st.success("Baseline scenario selected.")

with tab_diag:
    st.markdown('<div class="nx-section-title">07 / SYSTEM DIAGNOSTICS</div>', unsafe_allow_html=True)
    d1,d2,d3,d4=st.columns(4)
    d1.metric("SAMPLES IN BUFFER",len(readings)); d2.metric("THRESHOLD",f"{threshold:.2f} L/min")
    d3.metric("RULE WINDOW",f"{consecutive} samples"); d4.metric("ABOVE LIMIT",high_count)
    latest_run=0
    for value in reversed(readings):
        if value>threshold: latest_run+=1
        else: break
    diag_rows=[
      {"Diagnostic":"Input validation","Result":"PASS","Detail":"Numeric, non-negative readings"},
      {"Diagnostic":"Threshold comparison","Result":"ALERT" if current_flow>threshold else "PASS","Detail":f"Latest sample: {current_flow:.2f} L/min"},
      {"Diagnostic":"Consecutive rule","Result":"TRIGGERED" if possible_leak else "NOT TRIGGERED","Detail":f"Latest run: {latest_run}; required: {consecutive}"},
      {"Diagnostic":"Physical sensor link","Result":"NOT CONNECTED","Detail":"Simulated/manual prototype input"},
    ]
    st.dataframe(pd.DataFrame(diag_rows),width="stretch",hide_index=True)
    st.caption("Diagnostics describe software checks only; they do not certify hardware, network connectivity, water quality, or a confirmed leak.")

with tab_ops:
    st.markdown('<div class="nx-section-title">08 / OPERATOR CONTROL ROOM</div>', unsafe_allow_html=True)
    left,right=st.columns([1.15,1])
    with left:
      st.markdown('<div class="nx-info-card"><div class="nx-info-label">OPERATOR RESPONSE PROTOCOL</div><div class="nx-info-copy"><b>01 — OBSERVE</b><br>Review latest flow signature and timestamp.<br><br><b>02 — VALIDATE</b><br>Compare readings with threshold and consecutive-sample rule.<br><br><b>03 — INVESTIGATE</b><br>In a real deployment, verify using installed and calibrated equipment.<br><br><b>04 — RECORD</b><br>Export telemetry and document findings.</div></div>',unsafe_allow_html=True)
    with right:
      st.markdown(f"""<div style="padding:18px;border:1px solid {'#ff536d' if possible_leak else '#39f5a5'};border-radius:15px;background:#08182a">
      <div style="font:800 11px Orbitron;color:#75eaff;letter-spacing:1.5px">COMMAND AUTHORITY</div>
      <div style="font:800 21px Orbitron;color:{'#ff647b' if possible_leak else '#39f5a5'};margin:15px 0">{'REVIEW REQUIRED' if possible_leak else 'MONITORING'}</div>
      <div style="color:#a8c4da;font-size:12px;line-height:1.8">Scenario: {scenario}<br>Current: {current_flow:.2f} L/min<br>Average: {average_flow:.2f} L/min<br>Peak: {peak_flow:.2f} L/min<br>Rule: {consecutive} consecutive samples above {threshold:.2f} L/min</div></div>""",unsafe_allow_html=True)
    st.caption("Conceptual operator workflow only. This prototype does not control external valves, pumps, or infrastructure.")

st.markdown(
    '<div class="nx-footer">HYDRANEXUS // DETECT · ANALYZE · CONSERVE<br>'
    'NEXUS COMMAND DECK · SOFTWARE PROTOTYPE · SIMULATED / MANUAL DATA</div>',
    unsafe_allow_html=True,
)
