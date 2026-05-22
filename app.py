import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import uuid

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG & PATHS
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sunne Hub v12",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB = os.path.join(os.path.dirname(__file__), "database")

def db_path(name): return os.path.join(DB, f"{name}.json")

def load_json(name):
    p = db_path(name)
    if not os.path.exists(p): return []
    with open(p, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return []

def save_json(name, data):
    os.makedirs(DB, exist_ok=True)
    with open(db_path(name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def clean_uc(val):
    if val is None: return ""
    s = str(val).strip()
    if s.endswith(".0"): s = s[:-2]
    return s

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM — REPLICANDO gerador.sunne.com.br
# ─────────────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ══════════════════════════════════════════════════════
   ROOT — Paleta idêntica ao gerador.sunne.com.br
══════════════════════════════════════════════════════ */
:root {
    --s-wine:      #1C0010;
    --s-wine-mid:  #2a0018;
    --s-wine-li:   #3d0024;
    --s-orange:    #F36E21;
    --s-orange-h:  #d45c16;
    --s-bg:        #f9fafb;
    --s-white:     #ffffff;
    --s-border:    #e5e7eb;
    --s-border-md: #d1d5db;
    --s-text:      #111827;
    --s-text-md:   #374151;
    --s-text-sm:   #6b7280;
    --s-text-xs:   #9ca3af;
    --s-green:     #16a34a;
    --s-green-bg:  #f0fdf4;
    --s-red:       #dc2626;
    --s-red-bg:    #fef2f2;
    --s-yellow:    #d97706;
    --s-yellow-bg: #fffbeb;
    --s-blue:      #2563eb;
    --s-blue-bg:   #eff6ff;
    --s-radius:    8px;
    --s-radius-lg: 12px;
    --s-shadow:    0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
    --s-shadow-md: 0 4px 12px rgba(0,0,0,0.08);
}

/* ══════════════════════════════════════════════════════
   GLOBAL RESET
══════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

[data-testid="stAppViewContainer"] {
    background: var(--s-bg) !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
    backdrop-filter: none !important;
}
.main .block-container {
    padding: 28px 32px !important;
    max-width: 1440px !important;
}
* { font-family: 'Inter', system-ui, sans-serif !important; }

/* ══════════════════════════════════════════════════════
   SIDEBAR — Dark wine, exatamente como o portal
══════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--s-wine) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] > div:first-child {
    background: var(--s-wine) !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.85) !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 6px !important;
    color: #fff !important;
    font-size: 13px !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
    margin: 6px 0 !important;
}
/* Expander na sidebar */
[data-testid="stSidebar"] .streamlit-expanderHeader {
    background: transparent !important;
    border: none !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,0.35) !important;
    padding: 10px 20px 6px !important;
}
[data-testid="stSidebar"] .streamlit-expanderContent {
    background: transparent !important;
    border: none !important;
    padding: 0 8px !important;
}
/* Botões de nav na sidebar */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 6px !important;
    color: rgba(255,255,255,0.75) !important;
    text-align: left !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    padding: 9px 14px !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: background 0.15s, color 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.07) !important;
    color: #fff !important;
    transform: none !important;
    box-shadow: none !important;
}
/* Botão Sair */
[data-testid="stSidebar"] .stButton:last-child > button {
    color: rgba(255,255,255,0.45) !important;
    font-size: 13px !important;
}

/* ══════════════════════════════════════════════════════
   TOPOGRAFIA — Limpa, sem Serif pesado
══════════════════════════════════════════════════════ */
h1 { font-size: 22px !important; font-weight: 700 !important; color: var(--s-text) !important; margin-bottom: 2px !important; letter-spacing: -0.3px !important; }
h2 { font-size: 18px !important; font-weight: 600 !important; color: var(--s-text) !important; }
h3 { font-size: 15px !important; font-weight: 600 !important; color: var(--s-text) !important; }
h4 { font-size: 14px !important; font-weight: 600 !important; color: var(--s-text) !important; }
p  { font-size: 14px !important; color: var(--s-text-md) !important; }

/* ══════════════════════════════════════════════════════
   BOTÕES PRINCIPAIS — Laranja sólido
══════════════════════════════════════════════════════ */
.stButton > button {
    background: var(--s-orange) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--s-radius) !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    padding: 8px 18px !important;
    box-shadow: none !important;
    transition: background 0.15s, transform 0.1s !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: var(--s-orange-h) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 10px rgba(243,110,33,0.3) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Variante ghost */
.btn-ghost .stButton > button {
    background: transparent !important;
    color: var(--s-orange) !important;
    border: 1.5px solid var(--s-orange) !important;
    box-shadow: none !important;
}
.btn-ghost .stButton > button:hover {
    background: rgba(243,110,33,0.05) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ══════════════════════════════════════════════════════
   INPUTS
══════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    border-radius: var(--s-radius) !important;
    border: 1.5px solid var(--s-border-md) !important;
    font-size: 13.5px !important;
    color: var(--s-text) !important;
    background: var(--s-white) !important;
    padding: 8px 12px !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--s-orange) !important;
    box-shadow: 0 0 0 3px rgba(243,110,33,0.12) !important;
    outline: none !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
    border-radius: var(--s-radius) !important;
    border: 1.5px solid var(--s-border-md) !important;
    background: var(--s-white) !important;
    font-size: 13.5px !important;
}

/* ══════════════════════════════════════════════════════
   TABS — Estilo portal Sunne
══════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1.5px solid var(--s-border) !important;
    gap: 0 !important;
    padding-bottom: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 0 !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    color: var(--s-text-sm) !important;
    padding: 10px 20px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--s-orange) !important;
    border-bottom: 2.5px solid var(--s-orange) !important;
    font-weight: 600 !important;
}

/* ══════════════════════════════════════════════════════
   DATAFRAME / TABLES
══════════════════════════════════════════════════════ */
.stDataFrame {
    border-radius: var(--s-radius-lg) !important;
    border: 1px solid var(--s-border) !important;
    overflow: hidden !important;
    box-shadow: var(--s-shadow) !important;
}
.stDataFrame thead th {
    background: #f3f4f6 !important;
    color: var(--s-text-sm) !important;
    font-size: 11.5px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    border-bottom: 1px solid var(--s-border) !important;
}

/* ══════════════════════════════════════════════════════
   CARDS — Idênticos ao portal
══════════════════════════════════════════════════════ */
.s-card {
    background: var(--s-white);
    border-radius: var(--s-radius-lg);
    border: 1px solid var(--s-border);
    box-shadow: var(--s-shadow);
    padding: 20px 24px;
    margin-bottom: 16px;
}
.s-card-sm {
    background: var(--s-white);
    border-radius: var(--s-radius);
    border: 1px solid var(--s-border);
    box-shadow: var(--s-shadow);
    padding: 14px 18px;
    margin-bottom: 10px;
}

/* KPI Cards — exatamente como o Dashboard do portal */
.kpi-card {
    background: var(--s-white);
    border-radius: var(--s-radius-lg);
    border: 1px solid var(--s-border);
    box-shadow: var(--s-shadow);
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
}
.kpi-label {
    font-size: 12px;
    font-weight: 500;
    color: var(--s-text-sm);
    margin-bottom: 8px;
    letter-spacing: 0.01em;
}
.kpi-value {
    font-size: 26px;
    font-weight: 700;
    color: var(--s-text);
    line-height: 1.1;
    letter-spacing: -0.5px;
}
.kpi-value .kpi-unit {
    font-size: 14px;
    font-weight: 400;
    color: var(--s-text-sm);
    margin-left: 3px;
}
.kpi-delta {
    font-size: 12px;
    font-weight: 500;
    margin-top: 6px;
    display: flex;
    align-items: center;
    gap: 3px;
}
.kpi-delta.up   { color: var(--s-green); }
.kpi-delta.down { color: var(--s-red); }
.kpi-delta.neu  { color: var(--s-text-xs); }
.kpi-icon {
    position: absolute;
    right: 16px;
    top: 16px;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.9;
}

/* ══════════════════════════════════════════════════════
   STATUS BADGES
══════════════════════════════════════════════════════ */
.badge {
    display: inline-block;
    padding: 3px 9px;
    border-radius: 20px;
    font-size: 11.5px;
    font-weight: 500;
    letter-spacing: 0.01em;
    line-height: 1.5;
}
.badge-open    { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.badge-doing   { background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; }
.badge-blocked { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
.badge-done    { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.badge-cancel  { background: #f9fafb; color: #6b7280; border: 1px solid #e5e7eb; }

/* ══════════════════════════════════════════════════════
   ALERTAS — Estilo barra lateral colorida
══════════════════════════════════════════════════════ */
.s-alert {
    border-radius: var(--s-radius);
    padding: 12px 16px;
    font-size: 13.5px;
    line-height: 1.5;
    margin-bottom: 10px;
    display: flex;
    gap: 10px;
    align-items: flex-start;
}
.s-alert-icon { flex-shrink: 0; margin-top: 1px; }
.s-alert.red    { background: var(--s-red-bg);    border: 1px solid #fecaca; color: #7f1d1d; }
.s-alert.yellow { background: var(--s-yellow-bg); border: 1px solid #fde68a; color: #78350f; }
.s-alert.green  { background: var(--s-green-bg);  border: 1px solid #bbf7d0; color: #14532d; }
.s-alert.blue   { background: var(--s-blue-bg);   border: 1px solid #bfdbfe; color: #1e3a8a; }

/* ══════════════════════════════════════════════════════
   KANBAN
══════════════════════════════════════════════════════ */
.k-col {
    background: #f3f4f6;
    border-radius: var(--s-radius-lg);
    padding: 12px;
    min-height: 380px;
}
.k-col-header {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--s-text-sm);
    padding: 0 4px 10px;
    border-bottom: 1.5px solid var(--s-border);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.k-count {
    background: rgba(0,0,0,0.07);
    border-radius: 20px;
    padding: 1px 8px;
    font-size: 11px;
    font-weight: 600;
}
.k-card {
    background: var(--s-white);
    border-radius: var(--s-radius);
    border: 1px solid var(--s-border);
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    padding: 12px 14px;
    margin-bottom: 8px;
    transition: box-shadow 0.15s, transform 0.1s;
}
.k-card:hover {
    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
    transform: translateY(-1px);
}
.k-card-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--s-text);
    margin-bottom: 6px;
    line-height: 1.4;
}
.k-card-meta {
    font-size: 12px;
    color: var(--s-text-sm);
    line-height: 1.8;
}
.k-card-meta span { color: var(--s-text-md); font-weight: 500; }

/* ══════════════════════════════════════════════════════
   PAGE HEADER
══════════════════════════════════════════════════════ */
.page-h1 {
    font-size: 22px;
    font-weight: 700;
    color: var(--s-text);
    letter-spacing: -0.3px;
    margin-bottom: 2px;
}
.page-sub {
    font-size: 13.5px;
    color: var(--s-text-sm);
    margin-bottom: 24px;
}
.section-label {
    font-size: 15px;
    font-weight: 600;
    color: var(--s-text);
    margin: 20px 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--s-border);
}

/* ══════════════════════════════════════════════════════
   SIDEBAR LOGO
══════════════════════════════════════════════════════ */
.sb-logo {
    padding: 20px 20px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 4px;
}
.sb-logo-name {
    font-size: 22px;
    font-weight: 700;
    color: var(--s-orange) !important;
    letter-spacing: -0.5px;
    font-family: 'Inter', sans-serif !important;
}
.sb-logo-tagline {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3) !important;
    margin-top: 1px;
}
.sb-user {
    padding: 10px 20px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 4px;
}
.sb-user-name {
    font-size: 13px;
    font-weight: 600;
    color: #fff !important;
}
.sb-user-email {
    font-size: 11px;
    color: rgba(255,255,255,0.4) !important;
    margin-top: 1px;
}
.sb-section {
    padding: 10px 20px 4px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.28) !important;
}

/* ══════════════════════════════════════════════════════
   MISC
══════════════════════════════════════════════════════ */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* Divider */
.s-hr { border: none; border-top: 1px solid var(--s-border); margin: 16px 0; }

/* Tag tema */
.tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}
.tag-fat { background: #fff7ed; color: #c2410c; }
.tag-rat { background: #faf5ff; color: #7c3aed; }
.tag-cap { background: #f0fdf4; color: #15803d; }

/* Usina info card (portal-style) */
.usina-banner {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: var(--s-radius-lg);
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 20px;
}
.usina-icon-wrap {
    width: 44px; height: 44px;
    border-radius: 10px;
    background: #fff;
    border: 1px solid #fed7aa;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.usina-name { font-size: 15px; font-weight: 700; color: var(--s-text); }
.usina-info { font-size: 12.5px; color: var(--s-text-sm); margin-top: 2px; }

/* Log terminal */
.log-box {
    background: #0f172a;
    border-radius: var(--s-radius);
    padding: 14px 16px;
    font-family: 'Menlo', 'Consolas', monospace !important;
    font-size: 12px;
    color: #94a3b8;
    max-height: 200px;
    overflow-y: auto;
    line-height: 1.8;
}
.log-box .ok  { color: #4ade80; }
.log-box .err { color: #f87171; }
.log-box .wrn { color: #fbbf24; }
.log-box .inf { color: #60a5fa; }

/* Progress bar */
.pbar-wrap { background: #e5e7eb; border-radius: 99px; overflow: hidden; height: 6px; margin-top: 6px; }
.pbar-fill  { height: 100%; border-radius: 99px; transition: width 0.3s; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SVG ICONS (substitui todos os emojis)
# ─────────────────────────────────────────────────────────────────────────────
ICONS = {
    "dashboard":  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
    "team":       '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "kanban":     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="5" height="14" rx="1"/><rect x="10" y="3" width="5" height="9" rx="1"/><rect x="17" y="3" width="5" height="11" rx="1"/></svg>',
    "receipt":    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16l3-3 3 3 3-3 3 3V4a2 2 0 0 0-2-2z"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="9" x2="16" y2="9"/></svg>',
    "chart":      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "invoice":    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="12" y2="17"/></svg>',
    "audit":      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>',
    "scale":      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="12" y1="2" x2="12" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    "database":   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    "robot":      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="8" width="20" height="14" rx="2"/><path d="M12 2v6"/><circle cx="12" cy="2" r="1"/><line x1="6" y1="15" x2="6" y2="15"/><line x1="12" y1="15" x2="12" y2="15"/><line x1="18" y1="15" x2="18" y2="15"/></svg>',
    "ocr":        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><path d="M9 13h6M9 17h4"/></svg>',
    "sun":        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>',
    "alert":      '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "check":      '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>',
    "clock":      '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg>',
    "logout":     '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16,17 21,12 16,7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
    "upload":     '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16,16 12,12 8,16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>',
    "download":   '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="8,17 12,21 16,17"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.29"/></svg>',
    "plus":       '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
    "lock":       '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    "calendar":   '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "info":       '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "building":   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="9" y1="7" x2="9" y2="7.01"/><line x1="15" y1="7" x2="15" y2="7.01"/><line x1="9" y1="12" x2="9" y2="12.01"/><line x1="15" y1="12" x2="15" y2="12.01"/><path d="M9 17h6"/></svg>',
    "user":       '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "flash":      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polygon points="13,2 3,14 12,14 11,22 21,10 12,10 13,2"/></svg>',
    "conciliation":'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>',
}

def icon(name, size=16, color="currentColor"):
    base = ICONS.get(name, "")
    if not base: return ""
    return base.replace('width="16"', f'width="{size}"').replace('height="16"', f'height="{size}"')


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "logged_in": False, "user": None, "role": None,
        "page": "Dashboard", "pending_task_action": None,
        "tarefas_geradas": False, "trava_task_id": None,
        "trava_target_status": None, "show_new_task": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

init_session()

# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────
USERS = {
    "admin":  {"senha": "sunne2024", "role": "admin",    "nome": "Administrador", "email": "admin@sunne.com.br"},
    "milena": {"senha": "milena123", "role": "analista", "nome": "Milena Braga",   "email": "milena.braga@sunne.com.br"},
    "carlos": {"senha": "carlos123", "role": "analista", "nome": "Carlos Mendes",  "email": "carlos.mendes@sunne.com.br"},
}

def page_login():
    inject_css()
    # Extra CSS específico do login
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: #f3f4f6 !important; }
    .login-wrap {
        max-width: 400px; margin: 80px auto 0;
        background: #fff; border-radius: 14px;
        border: 1px solid #e5e7eb; padding: 40px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; margin-bottom:28px; margin-top:60px;">
            <div style="font-size:32px; font-weight:800; color:#F36E21; letter-spacing:-1px;">sunne</div>
            <div style="font-size:11px; font-weight:600; letter-spacing:0.2em; text-transform:uppercase; color:#9ca3af; margin-top:4px;">Hub v12 · Gestão Solar</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown('<div style="background:#fff; border-radius:14px; border:1px solid #e5e7eb; padding:32px; box-shadow:0 2px 12px rgba(0,0,0,0.06);">', unsafe_allow_html=True)
            st.markdown('<p style="font-size:18px; font-weight:700; color:#111827; margin-bottom:4px;">Acesso à Plataforma</p>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px; color:#6b7280; margin-bottom:20px;">Entre com suas credenciais corporativas</p>', unsafe_allow_html=True)
            user_input = st.text_input("Usuário", placeholder="seu.usuario")
            pass_input = st.text_input("Senha", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Entrar", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if submitted:
                u = USERS.get(user_input.lower())
                if u and u["senha"] == pass_input:
                    st.session_state.logged_in = True
                    st.session_state.user = user_input.lower()
                    st.session_state.role = u["role"]
                    st.session_state.nome = u["nome"]
                    st.session_state.email = u.get("email", "")
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

        st.markdown('<p style="text-align:center; font-size:12px; color:#9ca3af; margin-top:20px;">Acesso restrito · Sunne Energia</p>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MOTOR AUTOMÁTICO DIA 01
# ─────────────────────────────────────────────────────────────────────────────
def gerar_tarefas_mensais():
    tasks = load_json("tasks")
    today = date.today()
    mes_ref = today.strftime("%Y-%m")
    ja_gerado = any(t.get("mes_geracao") == mes_ref for t in tasks)
    if ja_gerado: return

    usinas = load_json("usinas")
    usinas_ativas = [u for u in usinas if u.get("ativa", True)]
    s1 = today.replace(day=1)
    s2 = today.replace(day=8)
    s3 = today.replace(day=15)
    s4 = today.replace(day=22)
    novas = []

    for usina in usinas_ativas:
        base = {"usina_id": usina["id"], "usina_nome": usina["nome"],
                "analista": "milena", "status": "em aberto",
                "mes_geracao": mes_ref, "motivo_bloqueio": ""}
        novas += [
            {**base, "id": str(uuid.uuid4()), "titulo": f"Captura de Fatura UG — {usina['nome']}",
             "macro_tema": "Faturamento", "data_programada": s1.isoformat(),
             "data_limite": (s1+timedelta(days=6)).isoformat(), "semana": 1},
            {**base, "id": str(uuid.uuid4()), "titulo": f"Conciliação de Medição — {usina['nome']}",
             "macro_tema": "Faturamento", "data_programada": s1.isoformat(),
             "data_limite": (s1+timedelta(days=6)).isoformat(), "semana": 1},
            {**base, "id": str(uuid.uuid4()), "titulo": f"Auditoria Técnica UCs — {usina['nome']}",
             "macro_tema": "Rateio", "data_programada": s2.isoformat(),
             "data_limite": (s3+timedelta(days=6)).isoformat(), "semana": 2},
            {**base, "id": str(uuid.uuid4()), "titulo": f"Captura RPA Portal Sunne — {usina['nome']}",
             "analista": "carlos", "macro_tema": "Captura",
             "data_programada": s4.isoformat(), "data_limite": (s4+timedelta(days=7)).isoformat(), "semana": 4},
        ]

    tasks.extend(novas)
    save_json("tasks", tasks)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def is_overdue(task):
    try:
        dl = date.fromisoformat(task.get("data_limite", "2099-12-31"))
        return dl < date.today() and task.get("status") not in ("concluido", "cancelado")
    except: return False

def status_badge(status):
    m = {"em aberto":("badge-open","Em Aberto"), "em andamento":("badge-doing","Em Andamento"),
         "travado":("badge-blocked","Travado"), "concluido":("badge-done","Concluído"), "cancelado":("badge-cancel","Cancelado")}
    cls, label = m.get(status, ("badge-open", status))
    return f'<span class="badge {cls}">{label}</span>'

def page_header(title, subtitle=""):
    st.markdown(f'<div class="page-h1">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-sub">{subtitle}</div>', unsafe_allow_html=True)

def kpi_card(label, value, sub="", delta="", delta_type="neu", icon_name="", icon_bg="#fff7ed", icon_color="#F36E21"):
    icon_html = ""
    if icon_name:
        ico = ICONS.get(icon_name, "")
        ico_styled = ico.replace('stroke="currentColor"', f'stroke="{icon_color}"') if ico else ""
        icon_html = f'<div class="kpi-icon" style="background:{icon_bg};">{ico_styled}</div>'

    delta_html = ""
    if delta:
        arrow = "▲" if delta_type == "up" else ("▼" if delta_type == "down" else "")
        delta_html = f'<div class="kpi-delta {delta_type}">{arrow} {delta}</div>'

    sub_html = f'<div style="font-size:12px; color:#6b7280; margin-top:4px;">{sub}</div>' if sub else ""

    return f"""
    <div class="kpi-card">
        {icon_html}
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
        {delta_html}
    </div>"""


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
NAV = {
    "CENTRAL DE COMANDO":        [("Dashboard", "dashboard"), ("Gestão da Equipe", "team")],
    "ESTEIRA":                   [("Atividades", "kanban")],
    "FATURAMENTO & BI":          [("Conciliação de Medição", "conciliation"), ("Inteligência Financeira", "chart"), ("Faturas das UGs", "invoice")],
    "ENGENHARIA DE RATEIOS":     [("Auditoria Técnica", "audit"), ("Simulador de Cotas", "scale")],
    "BASES DE SUPORTE":          [("Geradores", "user"), ("Usinas", "building"), ("Geração (Livro-Caixa)", "flash"), ("Backoffice", "database")],
    "AUTOMAÇÕES":                [("Captura RPA", "robot"), ("OCR HubSpot", "ocr")],
}

def render_sidebar():
    with st.sidebar:
        nome = st.session_state.get("nome", "Usuário")
        email = st.session_state.get("email", "")
        role = st.session_state.get("role", "analista")

        st.markdown(f"""
        <div class="sb-logo">
            <div class="sb-logo-name">sunne</div>
            <div class="sb-logo-tagline">Hub v12 · BI & Automação</div>
        </div>
        <div class="sb-user">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="width:32px;height:32px;border-radius:50%;background:#F36E21;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;flex-shrink:0;">
                    {nome[0].upper()}
                </div>
                <div>
                    <div class="sb-user-name">{nome}</div>
                    <div class="sb-user-email">{email}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for section, pages in NAV.items():
            if section == "CENTRAL DE COMANDO" and role != "admin":
                pages = [("Dashboard", "dashboard")]

            st.markdown(f'<div class="sb-section">{section}</div>', unsafe_allow_html=True)
            for label, ico_name in pages:
                active = st.session_state.page == label
                bg = "rgba(243,110,33,0.15)" if active else "transparent"
                color = "#F36E21" if active else "rgba(255,255,255,0.75)"
                fw = "600" if active else "400"
                ico_svg = ICONS.get(ico_name, "")
                ico_colored = ico_svg.replace('stroke="currentColor"', f'stroke="{color}"') if ico_svg else ""
                st.markdown(f"""
                <div style="padding:2px 12px;">
                    <div onclick="" style="display:flex;align-items:center;gap:9px;padding:9px 12px;
                         border-radius:6px;background:{bg};cursor:pointer;color:{color};
                         font-size:13.5px;font-weight:{fw}; transition:all 0.15s;">
                        <span style="opacity:0.85;flex-shrink:0;">{ico_colored}</span>
                        <span>{label}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                # Botão real oculto (hack Streamlit)
                if st.button(label, key=f"nav_{label}", use_container_width=True):
                    st.session_state.page = label
                    st.rerun()

        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
        st.markdown('<hr style="border-color:rgba(255,255,255,0.08);margin:0 20px;">', unsafe_allow_html=True)
        st.markdown('<div style="padding:8px 12px;">', unsafe_allow_html=True)
        if st.button(f"Sair", key="logout_btn", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def page_dashboard():
    page_header("Dashboard", "Visão geral")

    tasks = load_json("tasks")
    usinas = load_json("usinas")
    geracao = load_json("geracao_usinas")
    mes_atual = date.today().strftime("%Y-%m")

    total_tasks = len(tasks)
    concluidas = len([t for t in tasks if t["status"] == "concluido"])
    atrasadas  = len([t for t in tasks if is_overdue(t)])
    travadas   = len([t for t in tasks if t["status"] == "travado"])
    usinas_at  = len([u for u in usinas if u.get("ativa", True)])
    pct_concl  = round(concluidas/total_tasks*100) if total_tasks else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(kpi_card("Cobranças Emitidas", total_tasks, "tarefas no mês",
                             icon_name="receipt", icon_bg="#fff7ed", icon_color="#F36E21"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Concluídas", concluidas, f"{pct_concl}% do total",
                             delta=f"+{pct_concl}% conclusão", delta_type="up" if pct_concl>50 else "neu",
                             icon_name="check", icon_bg="#f0fdf4", icon_color="#16a34a"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Inadimplência", atrasadas, "tarefas vencidas",
                             delta=f"{atrasadas} atrasadas" if atrasadas else "Tudo em dia",
                             delta_type="down" if atrasadas>0 else "up",
                             icon_name="alert", icon_bg="#fef2f2", icon_color="#dc2626"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Travadas", travadas, "aguardam desbloqueio",
                             icon_name="lock", icon_bg="#faf5ff", icon_color="#7c3aed"), unsafe_allow_html=True)
    with c5:
        st.markdown(kpi_card("Usinas Ativas", usinas_at, "em operação",
                             icon_name="sun", icon_bg="#fff7ed", icon_color="#F36E21"), unsafe_allow_html=True)

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1.2])

    with col_a:
        st.markdown('<div class="section-label">Alertas Críticos</div>', unsafe_allow_html=True)
        alertas = []
        usinas_com_ger = {g["usina_id"] for g in geracao if g.get("mes_ref","").startswith(mes_atual[:7])}
        for u in usinas:
            if u.get("ativa") and u["id"] not in usinas_com_ger:
                alertas.append(("red", f"Sem geração registrada: <strong>{u['nome']}</strong>"))
        for t in tasks:
            if is_overdue(t):
                alertas.append(("yellow", f"Tarefa vencida: <strong>{t['titulo'][:50]}</strong>"))
        for u in usinas:
            try:
                dr = date.fromisoformat(u.get("data_ultimo_rateio","2020-01-01"))
                dias = (date.today()-dr).days
                if dias>90: alertas.append(("yellow", f"Rateio desatualizado ({dias}d): <strong>{u['nome']}</strong>"))
            except: pass

        if not alertas:
            st.markdown('<div class="s-alert green"><div class="s-alert-icon">' + ICONS["check"].replace('stroke="currentColor"','stroke="#16a34a"') + '</div><div>Nenhum alerta crítico. Sistema operando normalmente.</div></div>', unsafe_allow_html=True)
        else:
            for tipo, msg in alertas[:6]:
                ico = ICONS["alert"].replace('stroke="currentColor"', f'stroke="{"#dc2626" if tipo=="red" else "#d97706"}"')
                st.markdown(f'<div class="s-alert {tipo}"><div class="s-alert-icon">{ico}</div><div>{msg}</div></div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-label">Minha Agenda de Hoje</div>', unsafe_allow_html=True)
        user = st.session_state.get("user", "")
        hoje = date.today().isoformat()
        minhas = [t for t in tasks if t.get("analista")==user and t.get("status") not in ("concluido","cancelado")]
        hoje_t = [t for t in minhas if t.get("data_programada")==hoje]
        atras_t = [t for t in minhas if t.get("data_limite","9999")<hoje]
        agenda = sorted(hoje_t + [t for t in atras_t if t not in hoje_t], key=lambda x: x.get("data_limite","9999"))

        if not agenda:
            st.markdown('<div class="s-alert green"><div class="s-alert-icon">' + ICONS["check"].replace('stroke="currentColor"','stroke="#16a34a"') + '</div><div>Nenhuma tarefa para hoje.</div></div>', unsafe_allow_html=True)
        else:
            for t in agenda[:6]:
                ov = is_overdue(t)
                bdr = "#fecaca" if ov else "#e5e7eb"
                st.markdown(f"""
                <div class="s-card-sm" style="border-left:3px solid {'#dc2626' if ov else '#F36E21'}; margin-bottom:8px;">
                    <div style="font-size:13px; font-weight:600; color:#111827; margin-bottom:5px;">{t['titulo'][:55]}</div>
                    <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap; font-size:12px; color:#6b7280;">
                        <span>{t.get('usina_nome','—')[:28]}</span>
                        <span>Limite: {t.get('data_limite','—')}</span>
                        {status_badge(t['status'])}
                        {'<span class="badge badge-blocked">Atrasada</span>' if ov else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Receita Mensal (Visão Caixa)
    st.markdown('<div class="section-label">Receita Mensal (Visão Caixa)</div>', unsafe_allow_html=True)
    historico = load_json("historico_analises")
    if historico:
        df_h = pd.DataFrame(historico)
        df_h["mes_ref"] = pd.to_datetime(df_h["mes_ref"])
        df_h = df_h.sort_values("mes_ref")
        df_h["label"] = df_h["mes_ref"].dt.strftime("%b/%y")

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_h["label"], y=df_h["recebimento_bruto"],
                             name="Emitido", marker_color="#3b82f6", opacity=0.85, text=None))
        fig.add_trace(go.Bar(x=df_h["label"], y=df_h["recebimento_liquido"],
                             name="Recebido", marker_color="#F36E21", opacity=0.85))
        fig.update_layout(
            barmode="group", plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=12, color="#374151"),
            height=280, margin=dict(l=10, r=10, t=10, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            yaxis=dict(gridcolor="#f3f4f6", showgrid=True, tickprefix="R$", tickfont=dict(size=11)),
            xaxis=dict(gridcolor="#f3f4f6", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown('<div class="s-alert blue"><div>' + ICONS["info"].replace('stroke="currentColor"','stroke="#2563eb"') + '</div><div style="margin-left:8px;">Nenhum histórico de análises cadastrado ainda.</div></div>', unsafe_allow_html=True)

    # Agenda 7 dias
    st.markdown('<div class="section-label">Próximos 7 Dias — Agenda Operacional</div>', unsafe_allow_html=True)
    eventos = ["Envio Faturas Grupo A", "Reunião Operacional", "Auditoria USI001",
               "Deadline Conciliação", "Relatório BI", "Captura RPA", "Revisão Rateios"]
    cols = st.columns(7)
    for i, ev in enumerate(eventos):
        dt = (date.today() + timedelta(days=i)).strftime("%d/%m")
        is_today = i == 0
        with cols[i]:
            border = "#F36E21" if is_today else "#e5e7eb"
            bg = "#fff7ed" if is_today else "#fff"
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {border};border-radius:10px;padding:12px;text-align:center;min-height:80px;">
                <div style="font-size:11px;font-weight:700;color:#F36E21;">{dt}</div>
                <div style="font-size:11.5px;color:#374151;margin-top:6px;line-height:1.4;font-weight:500;">{ev}</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: GESTÃO DA EQUIPE
# ─────────────────────────────────────────────────────────────────────────────
def page_gestao_equipe():
    if st.session_state.role != "admin":
        st.error("Acesso restrito ao Administrador.")
        return
    page_header("Gestão da Equipe", "Desempenho operacional por analista")

    tasks = load_json("tasks")
    analistas = list({t.get("analista","") for t in tasks if t.get("analista")})
    if not analistas:
        st.info("Nenhuma tarefa cadastrada ainda.")
        return

    rows = []
    for an in analistas:
        t_an = [t for t in tasks if t.get("analista")==an]
        concl = [t for t in t_an if t["status"]=="concluido"]
        andam = [t for t in t_an if t["status"]=="em andamento"]
        atras = [t for t in t_an if is_overdue(t)]
        trav  = [t for t in t_an if t["status"]=="travado"]
        slas = []
        for t in concl:
            try:
                dp = date.fromisoformat(t.get("data_programada",date.today().isoformat()))
                dl = date.fromisoformat(t.get("data_limite",date.today().isoformat()))
                slas.append((dl-dp).days)
            except: pass
        sla_med = round(sum(slas)/len(slas),1) if slas else 0
        nome_an = USERS.get(an,{}).get("nome",an)
        rows.append({"Analista":nome_an,"Total":len(t_an),"Concluídas":len(concl),
                     "Em Andamento":len(andam),"Atrasadas":len(atras),"Travadas":len(trav),"SLA Médio (d)":sla_med})

    df = pd.DataFrame(rows)

    c1,c2,c3 = st.columns(3)
    with c1: st.markdown(kpi_card("Analistas Ativos", len(analistas)), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Total Tarefas", len(tasks), "todas as equipes"), unsafe_allow_html=True)
    with c3:
        tot_concl = len([t for t in tasks if t["status"]=="concluido"])
        pct = round(tot_concl/len(tasks)*100) if tasks else 0
        st.markdown(kpi_card("Taxa Conclusão", f"{pct}%", "global", delta=f"{pct}% do mês", delta_type="up"), unsafe_allow_html=True)

    st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

    fig = go.Figure()
    cats = ["Concluídas","Em Andamento","Atrasadas","Travadas"]
    colors = ["#22c55e","#F36E21","#ef4444","#8b5cf6"]
    for cat,cor in zip(cats,colors):
        fig.add_trace(go.Bar(name=cat, x=df["Analista"], y=df[cat],
                             marker_color=cor, text=df[cat], textposition="auto",
                             textfont=dict(size=11)))
    fig.update_layout(barmode="group", plot_bgcolor="white", paper_bgcolor="white",
                      font=dict(family="Inter",size=12), height=340,
                      margin=dict(l=10,r=10,t=20,b=10),
                      legend=dict(orientation="h",yanchor="bottom",y=1.02),
                      yaxis=dict(gridcolor="#f3f4f6"),xaxis=dict(gridcolor="transparent"))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    st.markdown('<div class="section-label">SLA por Analista</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: KANBAN
# ─────────────────────────────────────────────────────────────────────────────
KANBAN_STATUS = ["em aberto","em andamento","travado","concluido","cancelado"]
KANBAN_LABELS = {"em aberto":"Em Aberto","em andamento":"Em Andamento",
                 "travado":"Travado","concluido":"Concluído","cancelado":"Cancelado"}
TEMA_COLORS  = {"Faturamento":("#fff7ed","#c2410c"),"Rateio":("#faf5ff","#7c3aed"),"Captura":("#f0fdf4","#15803d")}

def page_atividades():
    page_header("Atividades", "Esteira operacional mensal — gerencie e monitore o fluxo de trabalho")

    tasks = load_json("tasks")
    usinas = load_json("usinas")
    analistas_list = list(USERS.keys())

    # Filtros
    c1,c2,c3,c4 = st.columns([1,1,1,1])
    with c1: tema_filtro = st.selectbox("Macro-tema", ["Todos","Faturamento","Rateio","Captura"])
    with c2: analista_filtro = st.selectbox("Analista", ["Todos"]+analistas_list)
    with c3: semana_filtro = st.selectbox("Semana", ["Todas","1","2","3","4"])
    with c4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Nova Tarefa", key="new_task_btn"):
            st.session_state.show_new_task = True

    if st.session_state.get("show_new_task"):
        with st.expander("Criar Nova Tarefa", expanded=True):
            with st.form("form_nova_tarefa"):
                c1,c2 = st.columns(2)
                with c1:
                    titulo = st.text_input("Título")
                    usina_opts = {u["nome"]:u["id"] for u in usinas}
                    usina_sel = st.selectbox("Usina", list(usina_opts.keys()))
                    analista_sel = st.selectbox("Analista", analistas_list)
                with c2:
                    tema_sel = st.selectbox("Macro-tema", ["Faturamento","Rateio","Captura"])
                    data_prog = st.date_input("Data Programada", value=date.today())
                    data_lim  = st.date_input("Data Limite", value=date.today()+timedelta(days=7))
                if st.form_submit_button("Criar"):
                    nova = {"id":str(uuid.uuid4()),"titulo":titulo,"usina_id":usina_opts.get(usina_sel,""),
                            "usina_nome":usina_sel,"analista":analista_sel,"status":"em aberto",
                            "macro_tema":tema_sel,"data_programada":data_prog.isoformat(),
                            "data_limite":data_lim.isoformat(),"mes_geracao":date.today().strftime("%Y-%m"),
                            "motivo_bloqueio":"","semana":1}
                    tasks.append(nova)
                    save_json("tasks",tasks)
                    st.session_state.show_new_task = False
                    st.rerun()

    # Filtrar
    filtered = [t for t in tasks
                if (tema_filtro=="Todos" or t.get("macro_tema")==tema_filtro)
                and (analista_filtro=="Todos" or t.get("analista")==analista_filtro)
                and (semana_filtro=="Todas" or str(t.get("semana",""))==semana_filtro)]

    # Modal trava governança
    if st.session_state.get("trava_task_id"):
        st.markdown('<div class="s-alert red"><strong>Trava de Governança —</strong> Justificativa obrigatória para continuar.</div>', unsafe_allow_html=True)
        motivo = st.text_area("Motivo do Travamento / Cancelamento (mín. 10 caracteres):", key="motivo_trava")
        target = st.session_state.get("trava_target_status","travado")
        c1,c2 = st.columns([1,4])
        with c1:
            if st.button("Confirmar", key="confirm_trava"):
                if len(motivo.strip()) < 10:
                    st.error("Motivo muito curto.")
                else:
                    for t in tasks:
                        if t["id"]==st.session_state.trava_task_id:
                            t["status"]=target; t["motivo_bloqueio"]=motivo.strip()
                    save_json("tasks",tasks)
                    st.session_state.trava_task_id=None
                    st.rerun()
        with c2:
            if st.button("Cancelar", key="cancel_trava"):
                st.session_state.trava_task_id=None; st.rerun()
        st.markdown("---")

    # Board
    cols = st.columns(5)
    for i, status in enumerate(KANBAN_STATUS):
        with cols[i]:
            cards = [t for t in filtered if t.get("status")==status]
            col_accents = {"em aberto":"#3b82f6","em andamento":"#F36E21","travado":"#ef4444","concluido":"#22c55e","cancelado":"#9ca3af"}
            acc = col_accents.get(status,"#9ca3af")
            st.markdown(f"""
            <div class="k-col" style="border-top:3px solid {acc};">
                <div class="k-col-header">
                    {KANBAN_LABELS[status]}
                    <span class="k-count">{len(cards)}</span>
                </div>
            """, unsafe_allow_html=True)

            for task in cards:
                ov = is_overdue(task)
                tema_bg, tema_clr = TEMA_COLORS.get(task.get("macro_tema",""),("#f3f4f6","#374151"))
                ana_nome = USERS.get(task.get("analista",""),{}).get("nome", task.get("analista","—"))
                st.markdown(f"""
                <div class="k-card" style="{'border-left:3px solid #dc2626;' if ov else ''}">
                    <div class="k-card-title">{task['titulo'][:52]}</div>
                    <div class="k-card-meta">
                        {task.get('usina_nome','—')[:26]}<br>
                        <span>{ana_nome}</span><br>
                        Limite: {task.get('data_limite','—')}
                    </div>
                    <div style="margin-top:8px;display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                        <span class="tag" style="background:{tema_bg};color:{tema_clr};">{task.get('macro_tema','—')}</span>
                        {status_badge(task['status'])}
                        {'<span class="badge badge-blocked">Vencida</span>' if ov else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                outros = [s for s in KANBAN_STATUS if s!=status]
                label_map = {"em aberto":"Abrir","em andamento":"Iniciar","travado":"Travar","concluido":"Feito","cancelado":"Cancelar"}
                bc = st.columns(len(outros))
                for j, ns in enumerate(outros):
                    with bc[j]:
                        if st.button(label_map.get(ns,ns), key=f"mv_{task['id']}_{ns}", use_container_width=True):
                            if ns in ("travado","cancelado"):
                                st.session_state.trava_task_id = task["id"]
                                st.session_state.trava_target_status = ns
                                st.rerun()
                            else:
                                for t in tasks:
                                    if t["id"]==task["id"]: t["status"]=ns
                                save_json("tasks",tasks); st.rerun()
                st.markdown('<hr style="border-color:#f3f4f6;margin:6px 0;">', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CONCILIAÇÃO
# ─────────────────────────────────────────────────────────────────────────────
def page_conciliacao():
    page_header("Conciliação de Medição", "Semana 1 · Cruzamento Extrato Detalhado vs Medição Sunne — Regra Fatura Unificada")

    st.markdown("""
    <div class="s-alert blue">
    <div class="s-alert-icon">""" + ICONS["info"].replace('stroke="currentColor"','stroke="#2563eb"') + """</div>
    <div><strong>Fluxo:</strong> Faça upload do Extrato Detalhado (Excel) e da Tabela Detalhada de Medição Sunne.
    O sistema aplica a Regra da Fatura Unificada e exibe divergências de caixa.</div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### Extrato Detalhado")
        extrato_file = st.file_uploader("Upload Extrato (Excel)", type=["xlsx","xls"], key="extrato_up")
    with c2:
        st.markdown("#### Medição Sunne")
        medicao_file = st.file_uploader("Upload Medição Sunne (Excel)", type=["xlsx","xls"], key="medicao_up")

    mes_ref = st.text_input("Mês de Referência (AAAA-MM)", value=date.today().strftime("%Y-%m"))

    if extrato_file and medicao_file:
        if st.button("Executar Conciliação"):
            with st.spinner("Processando..."):
                try:
                    df_ext = pd.read_excel(extrato_file, dtype=str)
                    df_med = pd.read_excel(medicao_file, sheet_name="Tabela Detalhada", dtype=str)
                    df_ext.columns = [c.strip() for c in df_ext.columns]
                    df_med.columns = [c.strip() for c in df_med.columns]
                    if "UC" in df_ext.columns: df_ext["UC"] = df_ext["UC"].apply(clean_uc)
                    if "UC" in df_med.columns: df_med["UC"] = df_med["UC"].apply(clean_uc)

                    if "Status" in df_ext.columns:
                        df_pago = df_ext[df_ext["Status"].str.lower().str.contains("pago",na=False)].copy()
                    else:
                        df_pago = df_ext.copy()
                    if "Competência" in df_pago.columns:
                        df_pago = df_pago[df_pago["Competência"].astype(str).str.startswith(mes_ref)]

                    def calc_ajustado(row):
                        try:
                            unif = str(row.get("Fatura Unificada","")).lower()
                            total = float(str(row.get("Total a Pagar",0)).replace(",",".").replace("R$","").strip() or 0)
                            boleto = float(str(row.get("Total a Pagar Boleto Concessionária",0)).replace(",",".").replace("R$","").strip() or 0)
                            return total - boleto if unif in ("true","sim","1","yes") else total
                        except: return 0.0

                    df_pago["Valor Ajustado"] = df_pago.apply(calc_ajustado, axis=1)
                    df_merged = df_pago.merge(df_med[["UC"]+[c for c in df_med.columns if c!="UC"]], on="UC", how="left", suffixes=("_ext","_med"))
                    chave_med = [c for c in df_merged.columns if "_med" in c]
                    divergencias = df_merged[df_merged[chave_med[0]].isna()].copy() if chave_med else df_merged.copy()

                    total_pago = df_pago["Valor Ajustado"].sum()
                    valor_div  = divergencias["Valor Ajustado"].sum() if "Valor Ajustado" in divergencias.columns else 0

                    c1,c2,c3 = st.columns(3)
                    with c1: st.markdown(kpi_card("Faturas Pagas", len(df_pago), f"R$ {total_pago:,.2f}"), unsafe_allow_html=True)
                    with c2: st.markdown(kpi_card("Divergências", len(divergencias), "ausentes na Medição"), unsafe_allow_html=True)
                    with c3: st.markdown(kpi_card("Valor Divergente", f"R$ {valor_div:,.2f}", "não repassado"), unsafe_allow_html=True)

                    if len(divergencias):
                        st.markdown('<div class="s-alert red"><div>' + ICONS["alert"].replace('stroke="currentColor"','stroke="#dc2626"') + '</div><div style="margin-left:8px;"><strong>Divergências de Caixa Detectadas</strong> — Faturas pagas ausentes no repasse da Medição Sunne.</div></div>', unsafe_allow_html=True)
                        cols_show = ["UC","Valor Ajustado"]+[c for c in ["Nome","Competência","Status"] if c in divergencias.columns]
                        st.dataframe(divergencias[cols_show].head(50), use_container_width=True)
                    else:
                        st.markdown('<div class="s-alert green"><div>' + ICONS["check"].replace('stroke="currentColor"','stroke="#16a34a"') + '</div><div style="margin-left:8px;">Nenhuma divergência. Extrato e Medição conciliados.</div></div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Erro: {e}")
    else:
        st.markdown("""
        <div class="s-card" style="text-align:center;padding:60px 20px;">
            <div style="font-size:36px;color:#e5e7eb;margin-bottom:12px;">""" + ICONS["conciliation"].replace('stroke="currentColor"','stroke="#d1d5db"').replace('width="16"','width="40"').replace('height="16"','height="40"') + """</div>
            <div style="font-size:15px;font-weight:600;color:#374151;">Aguardando arquivos para análise</div>
            <div style="font-size:13px;color:#9ca3af;margin-top:6px;">Faça upload do Extrato Detalhado e da Medição Sunne</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: INTELIGÊNCIA FINANCEIRA (BI)
# ─────────────────────────────────────────────────────────────────────────────
def page_bi():
    page_header("Inteligência Financeira", "Módulo BI Investidor · Geração vs Recebimento Anual")

    historico = load_json("historico_analises")
    usinas = load_json("usinas")
    usina_opts = {u["nome"]:u["id"] for u in usinas}

    col_sel, col_btn = st.columns([3,1])
    with col_sel: usina_sel = st.selectbox("Usina", list(usina_opts.keys()), key="bi_usina")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        export_click = st.button("Exportar PDF", key="export_pdf")

    usina_id = usina_opts.get(usina_sel,"")
    df_hist = pd.DataFrame([h for h in historico if h.get("usina_id")==usina_id])

    if df_hist.empty:
        st.info("Nenhum histórico para esta usina.")
        return

    df_hist["mes_ref"] = pd.to_datetime(df_hist["mes_ref"])
    df_hist = df_hist.sort_values("mes_ref")
    df_hist["mes_label"] = df_hist["mes_ref"].dt.strftime("%b/%Y")

    total_ger = df_hist["geracao_kwh"].sum()
    total_bruto = df_hist["recebimento_bruto"].sum()
    total_liq = df_hist["recebimento_liquido"].sum()
    total_ded = total_bruto - total_liq

    # KPI row — estilo Balanço Energético do portal
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi_card("Energia Injetada", f"{total_ger:,.0f}", "kWh no período", icon_name="flash", icon_bg="#fff7ed", icon_color="#F36E21"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Recebimento Bruto", f"R$ {total_bruto:,.0f}", "acumulado", icon_name="chart", icon_bg="#f0fdf4", icon_color="#16a34a"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Deduções", f"R$ {total_ded:,.0f}", "admin + Sunne + banco", icon_name="receipt", icon_bg="#fef2f2", icon_color="#dc2626"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Recebimento Líquido", f"R$ {total_liq:,.0f}", "net investidor", delta=f"{round(total_liq/total_bruto*100) if total_bruto else 0}% margem líquida", delta_type="up", icon_name="scale", icon_bg="#eff6ff", icon_color="#2563eb"), unsafe_allow_html=True)

    st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

    # Gráfico combinado — barras + linha (idêntico ao portal)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Geração Injetada (kWh)", x=df_hist["mes_label"], y=df_hist["geracao_kwh"],
                         marker_color="#F36E21", opacity=0.8, yaxis="y",
                         hovertemplate="%{x}: %{y:,.0f} kWh<extra></extra>"))
    fig.add_trace(go.Scatter(name="Recebimento Líquido (R$)", x=df_hist["mes_label"], y=df_hist["recebimento_liquido"],
                             mode="lines+markers", line=dict(color="#1C0010", width=2.5),
                             marker=dict(size=7, color="#1C0010"), yaxis="y2",
                             hovertemplate="%{x}: R$ %{y:,.2f}<extra></extra>"))
    fig.update_layout(
        title=dict(text=f"Desempenho Anual — {usina_sel}", font=dict(size=15,family="Inter",color="#111827")),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter",size=12,color="#374151"),
        height=380, margin=dict(l=10,r=10,t=50,b=20),
        yaxis=dict(title="Geração (kWh)", titlefont=dict(color="#F36E21",size=12),
                   tickfont=dict(color="#F36E21",size=11), gridcolor="#f3f4f6", showgrid=True),
        yaxis2=dict(title="Recebimento Líquido (R$)", titlefont=dict(color="#1C0010",size=12),
                    tickfont=dict(color="#1C0010",size=11), overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h",yanchor="bottom",y=1.02,x=0,font=dict(size=12)),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # Tabela detalhada — header laranja como no portal
    st.markdown('<div class="section-label">Detalhamento Mensal</div>', unsafe_allow_html=True)
    df_show = df_hist[["mes_label","geracao_kwh","recebimento_bruto","taxa_admin","taxa_sunne","tarifa_bancaria","recebimento_liquido"]].copy()
    df_show.columns = ["Mês","Geração (kWh)","Bruto (R$)","Taxa Admin","Taxa Sunne","Tarifa Banco","Líquido (R$)"]
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    # Export PDF
    if export_click:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            buf = BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=30)
            styles = getSampleStyleSheet()
            elems = []
            elems.append(Paragraph(f"Relatório BI — {usina_sel}", styles["Title"]))
            elems.append(Paragraph(f"Gerado em: {date.today().strftime('%d/%m/%Y')}", styles["Normal"]))
            elems.append(Spacer(1,20))
            kpi_data = [["Indicador","Valor"],
                        ["Geração Total (kWh)", f"{total_ger:,.0f}"],
                        ["Recebimento Bruto (R$)", f"{total_bruto:,.2f}"],
                        ["Deduções (R$)", f"{total_ded:,.2f}"],
                        ["Recebimento Líquido (R$)", f"{total_liq:,.2f}"]]
            t_kpi = Table(kpi_data, colWidths=[250,200])
            t_kpi.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1C0010")),
                ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#FDF9F7")]),
                ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#E5D5DC")),
                ("FONTSIZE",(0,0),(-1,-1),10),("PADDING",(0,0),(-1,-1),8),
            ]))
            elems.append(t_kpi)
            elems.append(Spacer(1,20))
            table_data = [["Mês","Geração kWh","Bruto R$","Adm R$","Sunne R$","Banco R$","Líquido R$"]]
            for _,row in df_show.iterrows():
                table_data.append([str(v) for v in row.values])
            t_det = Table(table_data, repeatRows=1)
            t_det.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#F36E21")),
                ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#FDF9F7")]),
                ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#E5D5DC")),
                ("FONTSIZE",(0,0),(-1,-1),8),("PADDING",(0,0),(-1,-1),6),
            ]))
            elems.append(t_det)
            doc.build(elems)
            st.download_button("Baixar PDF", data=buf.getvalue(),
                               file_name=f"bi_{usina_sel}_{date.today()}.pdf", mime="application/pdf")
        except ImportError:
            st.error("ReportLab não instalado. Execute: pip install reportlab")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: FATURAS UGs
# ─────────────────────────────────────────────────────────────────────────────
def page_faturas_ugs():
    page_header("Faturas das UGs", "Semana 1 · Controle de Faturamento Grupo A e B")

    usinas = load_json("usinas")
    tab_a, tab_b = st.tabs(["Grupo A", "Grupo B"])

    for tab, grupo in [(tab_a,"A"),(tab_b,"B")]:
        with tab:
            ug = [u for u in usinas if u.get("grupo")==grupo]
            st.markdown(f'<p style="font-size:13px;color:#6b7280;margin-bottom:14px;">{len(ug)} usinas no Grupo {grupo}</p>', unsafe_allow_html=True)
            if not ug:
                st.info(f"Nenhuma usina no Grupo {grupo}.")
                continue
            for u in ug:
                emitida = u.get("ativa")
                bdr = "#bbf7d0" if emitida else "#fde68a"
                bg  = "#f0fdf4" if emitida else "#fffbeb"
                status_txt = "Emitida" if emitida else "Pendente"
                status_clr = "#15803d" if emitida else "#92400e"
                st.markdown(f"""
                <div class="s-card-sm" style="background:{bg};border:1px solid {bdr};">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <div style="font-weight:600;font-size:14px;color:#111827;">{u['nome']}</div>
                            <div style="font-size:12px;color:#6b7280;margin-top:3px;">{u.get('concessionaria','—')} · {u.get('estado','—')} · {u.get('potencia_kwp',0)} kWp</div>
                        </div>
                        <span class="badge {'badge-done' if emitida else 'badge-doing'}">{status_txt}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            with c1: arq = st.file_uploader(f"Upload Faturas Grupo {grupo}", type=["pdf","xlsx"], key=f"fat_{grupo}")
            with c2:
                if arq and st.button(f"Processar Grupo {grupo}", key=f"proc_{grupo}"):
                    st.success(f"Faturas Grupo {grupo} processadas.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: AUDITORIA TÉCNICA
# ─────────────────────────────────────────────────────────────────────────────
def page_auditoria():
    page_header("Auditoria Técnica", "Semanas 2–3 · Saúde das UCs e Usinas — Análise histórica 3 meses")

    usinas = load_json("usinas")
    backoffice = load_json("backoffice")
    geracao = load_json("geracao_usinas")
    tasks = load_json("tasks")

    usina_opts = {u["nome"]:u["id"] for u in usinas}
    usina_sel = st.selectbox("Selecionar Usina", list(usina_opts.keys()), key="audit_usina")
    usina_id  = usina_opts.get(usina_sel,"")
    usina_data = next((u for u in usinas if u["id"]==usina_id), {})

    if usina_id:
        st.markdown(f"""
        <div class="usina-banner">
            <div class="usina-icon-wrap">{ICONS['sun'].replace('stroke="currentColor"','stroke="#F36E21"').replace('width="18"','width="22"').replace('height="18"','height="22"')}</div>
            <div>
                <div class="usina-name">{usina_sel}</div>
                <div class="usina-info">{usina_data.get('concessionaria','—')} · {usina_data.get('estado','—')} · {usina_data.get('potencia_kwp',0)} kWp · Grupo {usina_data.get('grupo','—')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    bf_usina  = [b for b in backoffice if b.get("usina_id")==usina_id]
    gen_usina = [g for g in geracao if g.get("usina_id")==usina_id]
    meses_3   = sorted(set(b.get("mes_ref","") for b in bf_usina))[-3:]
    alertas_c = []
    alertas_a = []

    for uc_nome in set(b.get("nome_beneficiario","") for b in bf_usina):
        uc_data = [b for b in bf_usina if b.get("nome_beneficiario")==uc_nome]
        if not uc_data: continue
        latest = sorted(uc_data, key=lambda x: x.get("mes_ref",""))[-1]
        saldo = latest.get("saldo_solar",0)
        consumos = [b.get("consumo_total",0) for b in uc_data]
        consumo_med = sum(consumos)/len(consumos) if consumos else 0
        if saldo > 3*consumo_med and consumo_med>0:
            alertas_a.append(f"Excesso de Saldo — {uc_nome}: Saldo {saldo:.0f} kWh / 3× consumo médio ({consumo_med:.0f} kWh). Reduzir cota.")
        meses_uc = sorted(uc_data, key=lambda x: x.get("mes_ref",""))
        sub3 = sum(1 for m in meses_uc[-3:] if m.get("creditos_utilizados",0) < m.get("consumo_total",0)-m.get("disponibilidade",100))
        if sub3>=3:
            alertas_a.append(f"Sub-atendimento — {uc_nome}: Créditos insuficientes por 3 meses consecutivos. Aumentar cota.")

    if meses_3:
        cons3m = sum(sum(b.get("consumo_total",0) for b in bf_usina if b.get("mes_ref")==m) for m in meses_3)
        ger3m  = sum(g.get("injetado_kwh",0) for g in gen_usina if g.get("mes_ref") in meses_3)
        if ger3m>0 and cons3m>ger3m:
            alertas_c.append(f"Usina Saturada — Consumo total 3M ({cons3m:,.0f} kWh) > Geração Injetada ({ger3m:,.0f} kWh). Superalocação detectada.")

    try:
        dr = date.fromisoformat(usina_data.get("data_ultimo_rateio","2020-01-01"))
        dias_def = (date.today()-dr).days
        if dias_def>90: alertas_a.append(f"Defasagem de Rateio — Último rateio há {dias_def} dias (limite: 90d). Atualização necessária.")
    except: pass

    col_alrt, col_hist = st.columns([1,1])
    with col_alrt:
        st.markdown('<div class="section-label">Diagnóstico</div>', unsafe_allow_html=True)
        if alertas_c:
            for a in alertas_c:
                st.markdown(f'<div class="s-alert red"><div class="s-alert-icon">{ICONS["alert"].replace(chr(34)+"currentColor"+chr(34), chr(34)+"#dc2626"+chr(34))}</div><div>{a}</div></div>', unsafe_allow_html=True)
            mes_ref = date.today().strftime("%Y-%m")
            ja_existe = any(t.get("titulo","").startswith("Atualizar Rateio Obrigatório") and t.get("usina_id")==usina_id and t.get("mes_geracao")==mes_ref for t in tasks)
            if not ja_existe:
                s4 = date.today().replace(day=22)
                tasks.append({"id":str(uuid.uuid4()), "titulo":f"Atualizar Rateio Obrigatório — {usina_sel}",
                              "usina_id":usina_id,"usina_nome":usina_sel,"analista":"milena","status":"em aberto",
                              "macro_tema":"Rateio","data_programada":s4.isoformat(),
                              "data_limite":(s4+timedelta(days=7)).isoformat(),"mes_geracao":mes_ref,"motivo_bloqueio":"","semana":4})
                save_json("tasks",tasks)
                st.markdown('<div class="s-alert yellow"><div class="s-alert-icon">' + ICONS["flash"].replace('stroke="currentColor"','stroke="#d97706"') + '</div><div>Tarefa "Atualizar Rateio Obrigatório" gerada automaticamente na Semana 4.</div></div>', unsafe_allow_html=True)
        if alertas_a:
            for a in alertas_a:
                st.markdown(f'<div class="s-alert yellow"><div class="s-alert-icon">{ICONS["alert"].replace(chr(34)+"currentColor"+chr(34), chr(34)+"#d97706"+chr(34))}</div><div>{a}</div></div>', unsafe_allow_html=True)
        if not alertas_c and not alertas_a:
            st.markdown('<div class="s-alert green"><div class="s-alert-icon">' + ICONS["check"].replace('stroke="currentColor"','stroke="#16a34a"') + '</div><div>Usina dentro dos parâmetros técnicos. Nenhuma intervenção necessária.</div></div>', unsafe_allow_html=True)

    with col_hist:
        st.markdown('<div class="section-label">Historico Backoffice</div>', unsafe_allow_html=True)
        if bf_usina:
            df_bf = pd.DataFrame(bf_usina)
            df_bf["uc"] = df_bf["uc"].apply(clean_uc)
            st.dataframe(df_bf, use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="s-alert blue"><div>' + ICONS["info"].replace('stroke="currentColor"','stroke="#2563eb"') + '</div><div style="margin-left:8px;">Nenhum histórico cadastrado para esta usina.</div></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SIMULADOR DE COTAS
# ─────────────────────────────────────────────────────────────────────────────
def page_simulador():
    page_header("Simulador de Cotas", "Rebalanceamento preditivo de rateio entre UCs e Usinas")

    usinas = load_json("usinas")
    geradores = load_json("geradores")
    usina_opts = {u["nome"]:u["id"] for u in usinas}

    col_sel, _ = st.columns([2,3])
    with col_sel: usina_sel = st.selectbox("Usina", list(usina_opts.keys()), key="sim_usina")
    usina_id = usina_opts.get(usina_sel,"")
    ger_usina = [g for g in geradores if g.get("usina_id")==usina_id]

    if not ger_usina:
        st.info("Nenhum gerador cadastrado para esta usina.")
        return

    usina_pot = next((u["potencia_kwp"] for u in usinas if u["id"]==usina_id), 100.0)
    ger_est   = usina_pot * 120
    total_cotas = sum(g.get("cota_percent",0) for g in ger_usina)

    st.markdown(f"""
    <div style="display:flex;gap:16px;margin-bottom:16px;flex-wrap:wrap;">
        <div class="s-card-sm" style="flex:1;min-width:160px;">
            <div class="kpi-label">Geração Estimada</div>
            <div class="kpi-value">{ger_est:,.0f} <span class="kpi-unit">kWh/mês</span></div>
        </div>
        <div class="s-card-sm" style="flex:1;min-width:160px;">
            <div class="kpi-label">Soma das Cotas</div>
            <div class="kpi-value" style="color:{'#16a34a' if abs(total_cotas-100)<0.1 else '#dc2626'}">{total_cotas:.1f}<span class="kpi-unit">%</span></div>
        </div>
        <div class="s-card-sm" style="flex:1;min-width:160px;">
            <div class="kpi-label">Geradores</div>
            <div class="kpi-value">{len(ger_usina)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cotas_novas = {}
    for g in ger_usina:
        c1,c2,c3 = st.columns([2,1,1])
        with c1: st.markdown(f'<div style="padding:10px 0;font-weight:500;font-size:14px;">{g["nome"]}</div>', unsafe_allow_html=True)
        with c2: nova = st.number_input(f"% cota", min_value=0.0, max_value=100.0, value=float(g.get("cota_percent",0)), step=0.5, key=f"cota_{g['id']}", label_visibility="collapsed")
        with c3:
            kwh_est = ger_est*nova/100
            st.markdown(f'<div style="padding:10px 0;font-size:13px;color:#6b7280;">≈ {kwh_est:,.0f} kWh</div>', unsafe_allow_html=True)
        cotas_novas[g["id"]] = nova

    nova_soma = sum(cotas_novas.values())
    ok = abs(nova_soma-100)<0.5
    st.markdown(f'<div style="font-weight:700;font-size:15px;color:{"#16a34a" if ok else "#dc2626"};margin:12px 0;">Soma total: {nova_soma:.1f}%</div>', unsafe_allow_html=True)

    if st.button("Salvar Cotas"):
        if not ok: st.error("As cotas devem somar 100% (±0.5%).")
        else:
            for g in geradores:
                if g["usina_id"]==usina_id and g["id"] in cotas_novas:
                    g["cota_percent"] = cotas_novas[g["id"]]
            save_json("geradores",geradores)
            st.success("Cotas atualizadas.")
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: GERADORES
# ─────────────────────────────────────────────────────────────────────────────
def page_geradores():
    page_header("Geradores", "Cadastro e gestão de geradores vinculados às usinas")

    geradores = load_json("geradores")
    usinas = load_json("usinas")
    usina_map = {u["id"]:u["nome"] for u in usinas}
    tab_lista, tab_novo = st.tabs(["Geradores Cadastrados", "Novo Gerador"])

    with tab_lista:
        if not geradores:
            st.info("Nenhum gerador cadastrado.")
        else:
            df = pd.DataFrame(geradores)
            df["Usina"] = df["usina_id"].map(usina_map)
            cols_show = ["id","nome","cpf_cnpj","Usina","cota_percent","ativo"]
            st.dataframe(df[[c for c in cols_show if c in df.columns]], use_container_width=True, hide_index=True)

    with tab_novo:
        with st.form("form_gerador"):
            c1,c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome / Razão Social")
                cpf_cnpj = st.text_input("CPF / CNPJ")
            with c2:
                usina_opts = {u["nome"]:u["id"] for u in usinas}
                usina_sel = st.selectbox("Usina", list(usina_opts.keys()))
                cota = st.number_input("Cota (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
            if st.form_submit_button("Cadastrar"):
                geradores.append({"id":f"GER{len(geradores)+1:03d}","nome":nome,"cpf_cnpj":cpf_cnpj,
                                  "usina_id":usina_opts.get(usina_sel,""),"cota_percent":cota,"ativo":True})
                save_json("geradores",geradores)
                st.success("Gerador cadastrado.")
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: USINAS
# ─────────────────────────────────────────────────────────────────────────────
def page_usinas():
    page_header("Usinas", "Cadastro e monitoramento das usinas de geração solar")

    usinas = load_json("usinas")
    tab_lista, tab_novo = st.tabs(["Usinas Cadastradas", "Nova Usina"])

    with tab_lista:
        if not usinas:
            st.info("Nenhuma usina cadastrada.")
        else:
            for u in usinas:
                ativa = u.get("ativa")
                bg  = "#f0fdf4" if ativa else "#fef2f2"
                bdr = "#bbf7d0" if ativa else "#fecaca"
                st.markdown(f"""
                <div class="s-card-sm" style="background:{bg};border:1px solid {bdr};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <div style="font-weight:700;font-size:14px;">{u['nome']}</div>
                            <div style="font-size:12px;color:#6b7280;margin-top:4px;line-height:1.8;">
                                {u.get('estado','—')} · {u.get('concessionaria','—')} · {u.get('potencia_kwp',0)} kWp · Grupo {u.get('grupo','—')}<br>
                                Último rateio: {u.get('data_ultimo_rateio','—')}
                            </div>
                        </div>
                        <span class="badge {'badge-done' if ativa else 'badge-blocked'}">{'Ativa' if ativa else 'Inativa'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab_novo:
        with st.form("form_usina"):
            c1,c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome da Usina")
                conc = st.text_input("Concessionária")
                uf   = st.text_input("UF", max_chars=2)
            with c2:
                pot  = st.number_input("Potência (kWp)", min_value=0.0, value=100.0, step=10.0)
                grp  = st.selectbox("Grupo", ["A","B"])
                drateio = st.date_input("Último Rateio", value=date.today())
            if st.form_submit_button("Cadastrar"):
                usinas.append({"id":f"USI{len(usinas)+1:03d}","nome":nome,"potencia_kwp":pot,
                               "concessionaria":conc,"estado":uf.upper(),"ativa":True,
                               "data_ultimo_rateio":drateio.isoformat(),"grupo":grp})
                save_json("usinas",usinas)
                st.success("Usina cadastrada.")
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: GERAÇÃO LIVRO-CAIXA
# ─────────────────────────────────────────────────────────────────────────────
def page_geracao():
    page_header("Geração — Livro-Caixa", "Registro de geração mensal por usina com Upsert automático")

    geracao = load_json("geracao_usinas")
    usinas  = load_json("usinas")
    tab_view, tab_add = st.tabs(["Histórico", "Lançar Geração"])

    with tab_view:
        if not geracao:
            st.info("Nenhum lançamento.")
        else:
            usina_map = {u["id"]:u["nome"] for u in usinas}
            df = pd.DataFrame(geracao)
            df["Usina"] = df["usina_id"].map(usina_map)
            df = df[["Usina","mes_ref","geracao_kwh","injetado_kwh"]].sort_values(["Usina","mes_ref"],ascending=False)
            df.columns = ["Usina","Mês Ref.","Geração (kWh)","Injetado (kWh)"]
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_add:
        usina_opts = {u["nome"]:u["id"] for u in usinas}
        with st.form("form_geracao"):
            c1,c2 = st.columns(2)
            with c1:
                us_sel = st.selectbox("Usina", list(usina_opts.keys()))
                mes_ref = st.text_input("Mês Ref. (AAAA-MM)", value=date.today().strftime("%Y-%m"))
            with c2:
                ger_kwh = st.number_input("Geração Total (kWh)", min_value=0.0, value=0.0, step=100.0)
                inj_kwh = st.number_input("Injetado na Rede (kWh)", min_value=0.0, value=0.0, step=100.0)
            if st.form_submit_button("Salvar / Atualizar"):
                uid = usina_opts.get(us_sel,"")
                found = False
                for g in geracao:
                    if g["usina_id"]==uid and g["mes_ref"]==mes_ref:
                        g["geracao_kwh"]=ger_kwh; g["injetado_kwh"]=inj_kwh; found=True; break
                if not found:
                    geracao.append({"usina_id":uid,"mes_ref":mes_ref,"geracao_kwh":ger_kwh,"injetado_kwh":inj_kwh})
                save_json("geracao_usinas",geracao)
                st.success("Lançado/atualizado.")
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: BACKOFFICE
# ─────────────────────────────────────────────────────────────────────────────
def page_backoffice():
    page_header("Backoffice", "Histórico cumulativo de consumo por UC — Base de Auditoria Técnica")

    backoffice = load_json("backoffice")
    usinas = load_json("usinas")
    tab_view, tab_add, tab_up = st.tabs(["Histórico","Lançar","Upload Excel"])

    with tab_view:
        if not backoffice:
            st.info("Nenhum registro.")
        else:
            df = pd.DataFrame(backoffice)
            df["uc"] = df["uc"].apply(clean_uc)
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_add:
        usina_opts = {u["nome"]:u["id"] for u in usinas}
        with st.form("form_backoffice"):
            c1,c2 = st.columns(2)
            with c1:
                uc = st.text_input("UC (sem .0)")
                nome_ben = st.text_input("Nome Beneficiário")
                us_sel = st.selectbox("Usina", list(usina_opts.keys()))
                mes_ref = st.text_input("Mês Ref.", value=date.today().strftime("%Y-%m"))
            with c2:
                cons_tot = st.number_input("Consumo Total (kWh)", min_value=0.0, value=0.0)
                cred_util = st.number_input("Créditos Utilizados (kWh)", min_value=0.0, value=0.0)
                saldo_sol = st.number_input("Saldo Solar (kWh)", min_value=0.0, value=0.0)
                tipo_lig = st.selectbox("Tipo Ligação", ["trifasico","bifasico","monofasico"])
            if st.form_submit_button("Salvar"):
                uid = usina_opts.get(us_sel,"")
                disp = 100.0 if tipo_lig=="trifasico" else (30.0 if tipo_lig=="monofasico" else 50.0)
                novo = {"uc":clean_uc(uc),"nome_beneficiario":nome_ben,"usina_id":uid,"mes_ref":mes_ref,
                        "consumo_total":cons_tot,"creditos_utilizados":cred_util,"saldo_solar":saldo_sol,
                        "consumo_compensavel":cons_tot-disp,"disponibilidade":disp,"tipo_ligacao":tipo_lig}
                found=False
                for b in backoffice:
                    if b["uc"]==clean_uc(uc) and b["mes_ref"]==mes_ref:
                        b.update(novo); found=True; break
                if not found: backoffice.append(novo)
                save_json("backoffice",backoffice)
                st.success("Salvo.")
                st.rerun()

    with tab_up:
        arquivo = st.file_uploader("Upload planilha (Excel)", type=["xlsx","xls"])
        if arquivo and st.button("Importar"):
            try:
                df = pd.read_excel(arquivo, dtype=str)
                df.columns = [c.strip().lower().replace(" ","_") for c in df.columns]
                if "uc" in df.columns: df["uc"] = df["uc"].apply(clean_uc)
                for r in df.to_dict("records"):
                    key = (r.get("uc",""), r.get("mes_ref",""))
                    found=False
                    for b in backoffice:
                        if (b.get("uc",""),b.get("mes_ref",""))==key:
                            b.update(r); found=True; break
                    if not found: backoffice.append(r)
                save_json("backoffice",backoffice)
                st.success(f"{len(df)} registros importados.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CAPTURA RPA
# ─────────────────────────────────────────────────────────────────────────────
def page_captura_rpa():
    page_header("Captura RPA", "Automação de captura no Portal Sunne · Semana 4")

    st.markdown('<div class="s-alert blue"><div class="s-alert-icon">' + ICONS["info"].replace('stroke="currentColor"','stroke="#2563eb"') + '</div><div>Este módulo conecta-se ao Portal Sunne via Selenium/Playwright para captura automatizada de faturas e dados de geração.</div></div>', unsafe_allow_html=True)

    usinas = load_json("usinas")
    usinas_ativas = [u for u in usinas if u.get("ativa")]

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-label">Configuração do Job</div>', unsafe_allow_html=True)
        usinas_sel = st.multiselect("Selecionar Usinas", [u["nome"] for u in usinas_ativas], default=[u["nome"] for u in usinas_ativas])
        tipo_cap = st.selectbox("Tipo", ["Faturas do Mês","Geração Mensal","Extrato Completo"])
        mes_cap = st.text_input("Mês de Referência", value=date.today().strftime("%Y-%m"))

    with c2:
        st.markdown('<div class="section-label">Status do Agent</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="s-card">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <div style="width:8px;height:8px;background:#22c55e;border-radius:50%;box-shadow:0 0 6px #22c55e;"></div>
                <div style="font-weight:600;font-size:14px;">RPA Agent Online</div>
            </div>
            <div style="font-size:13px;color:#6b7280;line-height:2;">
                Portal: sunne.com.br<br>
                Auth: Session OAuth2<br>
                Queue: 0 jobs pendentes<br>
                Último job: —
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

    if st.button("Iniciar Captura RPA"):
        if not usinas_sel:
            st.warning("Selecione ao menos uma usina.")
        else:
            prog = st.progress(0)
            txt  = st.empty()
            import time
            for i, u in enumerate(usinas_sel):
                txt.markdown(f'<div class="s-alert blue"><div>' + ICONS["info"].replace('stroke="currentColor"','stroke="#2563eb"') + f'</div><div style="margin-left:8px;">Processando: <strong>{u}</strong>...</div></div>', unsafe_allow_html=True)
                time.sleep(0.4)
                prog.progress((i+1)/len(usinas_sel))
            txt.markdown('<div class="s-alert green"><div>' + ICONS["check"].replace('stroke="currentColor"','stroke="#16a34a"') + '</div><div style="margin-left:8px;">Captura RPA concluída com sucesso.</div></div>', unsafe_allow_html=True)
            prog.empty()

            # Log simulado
            st.markdown(f"""
            <div class="log-box">
                <div class="inf">[{datetime.now().strftime('%H:%M:%S')}] Iniciando captura em {len(usinas_sel)} usinas...</div>
                {"".join(f'<div class="ok">[{datetime.now().strftime("%H:%M:%S")}] {u}: OK</div>' for u in usinas_sel)}
                <div class="ok">[{datetime.now().strftime('%H:%M:%S')}] Captura finalizada.</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: OCR HUBSPOT
# ─────────────────────────────────────────────────────────────────────────────
def page_ocr_hubspot():
    page_header("OCR HubSpot", "Leitura automatizada de documentos via API HubSpot")

    st.markdown('<div class="s-alert blue"><div class="s-alert-icon">' + ICONS["info"].replace('stroke="currentColor"','stroke="#2563eb"') + '</div><div>Integração HubSpot — conecte sua API Key para extração automática de dados de contratos, laudos e faturas enviados por clientes.</div></div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-label">Configuração da API</div>', unsafe_allow_html=True)
        with st.expander("Credenciais HubSpot"):
            api_key = st.text_input("HubSpot API Key", type="password", placeholder="pat-na1-...")
            portal_id = st.text_input("Portal ID", placeholder="12345678")
            if st.button("Testar Conexão"):
                if api_key: st.success("Conexão estabelecida (simulação).")
                else: st.error("Informe a API Key.")

        st.markdown('<div class="section-label" style="margin-top:12px;">Upload de Documento</div>', unsafe_allow_html=True)
        doc_file = st.file_uploader("PDF ou imagem", type=["pdf","png","jpg","jpeg"])
        tipo_doc = st.selectbox("Tipo", ["Fatura de Energia","Contrato de Adesão","Laudo Técnico","Extrato Bancário","Outro"])

    with c2:
        st.markdown('<div class="section-label">Status da Integração</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="s-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid #f3f4f6;">
                <span style="font-size:13px;color:#6b7280;">Status API</span>
                <span class="badge badge-blocked">Key Expirada</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f9fafb;">
                <span style="font-size:13px;color:#6b7280;">Docs processados</span>
                <span style="font-size:13px;font-weight:500;">47</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f9fafb;">
                <span style="font-size:13px;color:#6b7280;">Precisão média OCR</span>
                <span style="font-size:13px;font-weight:500;">96,2%</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;">
                <span style="font-size:13px;color:#6b7280;">Último processado</span>
                <span style="font-size:13px;font-weight:500;">14/05/2025</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if doc_file:
            st.markdown('<div class="s-alert green"><div>' + ICONS["check"].replace('stroke="currentColor"','stroke="#16a34a"') + '</div><div style="margin-left:8px;">Documento recebido. Aguardando envio à API.</div></div>', unsafe_allow_html=True)
            if st.button("Enviar ao HubSpot CRM"):
                st.success("Dados enviados ao HubSpot.")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────
ROUTE_MAP = {
    "Dashboard":               page_dashboard,
    "Gestão da Equipe":        page_gestao_equipe,
    "Atividades":              page_atividades,
    "Conciliação de Medição":  page_conciliacao,
    "Inteligência Financeira": page_bi,
    "Faturas das UGs":         page_faturas_ugs,
    "Auditoria Técnica":       page_auditoria,
    "Simulador de Cotas":      page_simulador,
    "Geradores":               page_geradores,
    "Usinas":                  page_usinas,
    "Geração (Livro-Caixa)":   page_geracao,
    "Backoffice":              page_backoffice,
    "Captura RPA":             page_captura_rpa,
    "OCR HubSpot":             page_ocr_hubspot,
}

def main():
    inject_css()
    if not st.session_state.logged_in:
        page_login()
        return

    if not st.session_state.get("tarefas_geradas"):
        gerar_tarefas_mensais()
        st.session_state.tarefas_geradas = True

    render_sidebar()
    page = st.session_state.page
    fn = ROUTE_MAP.get(page)
    if fn:
        fn()
    else:
        st.markdown(f"### Módulo em desenvolvimento: {page}")

if __name__ == "__main__":
    main()
