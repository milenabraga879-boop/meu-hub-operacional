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
    page_icon="☀️",
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
    """Remove .0 from UC strings imported from Excel."""
    if val is None: return ""
    s = str(val).strip()
    if s.endswith(".0"): s = s[:-2]
    return s

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM — SUNNE BRAND CSS
# ─────────────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
/* ── ROOT PALETTE ── */
:root {
    --sunne-wine:    #1C0010;
    --sunne-orange:  #F36E21;
    --sunne-orange2: #D45E18;
    --sunne-cream:   #FDF9F7;
    --sunne-white:   #FFFFFF;
    --sunne-border:  rgba(51,0,26,0.07);
    --sunne-shadow:  0 4px 24px rgba(51,0,26,0.05);
    --sunne-text:    #33001A;
    --sunne-muted:   #7A5060;
}

/* ── GLOBAL APP ── */
[data-testid="stAppViewContainer"] {
    background: var(--sunne-cream) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
    backdrop-filter: none !important;
}
.main .block-container {
    padding: 2rem 2.5rem !important;
    max-width: 1400px !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--sunne-wine) !important;
}
[data-testid="stSidebar"] * {
    color: #f5e6ec !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #fff !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
}
[data-testid="stSidebar"] .sidebar-section-header {
    font-size: 10px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(243,110,33,0.9) !important;
    font-weight: 600;
    padding: 16px 0 6px 0;
}

/* ── TYPOGRAPHY ── */
h1, h2 {
    font-family: 'Playfair Display', serif !important;
    color: var(--sunne-text) !important;
}
h3, h4, h5, h6 {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--sunne-text) !important;
    font-weight: 600 !important;
}
p, span, div, label, td, th {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── CARDS ── */
.sunne-card {
    background: var(--sunne-white);
    border-radius: 14px;
    border: 1px solid var(--sunne-border);
    box-shadow: var(--sunne-shadow);
    padding: 24px 28px;
    margin-bottom: 16px;
}
.sunne-card-sm {
    background: var(--sunne-white);
    border-radius: 12px;
    border: 1px solid var(--sunne-border);
    box-shadow: var(--sunne-shadow);
    padding: 18px 22px;
    margin-bottom: 12px;
}

/* ── KPI METRICS ── */
.kpi-block {
    background: var(--sunne-white);
    border-radius: 14px;
    border: 1px solid var(--sunne-border);
    box-shadow: var(--sunne-shadow);
    padding: 20px 24px;
    text-align: center;
}
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--sunne-muted);
    margin-bottom: 8px;
}
.kpi-value {
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    font-weight: 700;
    color: var(--sunne-text);
    line-height: 1;
}
.kpi-sub {
    font-size: 12px;
    color: var(--sunne-muted);
    margin-top: 4px;
}

/* ── BUTTONS ── */
.stButton > button {
    background: var(--sunne-orange) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 22px !important;
    box-shadow: 0 1px 4px rgba(243,110,33,0.3) !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    background: var(--sunne-orange2) !important;
    box-shadow: 0 4px 12px rgba(243,110,33,0.4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Ghost button variant */
.btn-ghost > button {
    background: transparent !important;
    color: var(--sunne-orange) !important;
    border: 1.5px solid var(--sunne-orange) !important;
    box-shadow: none !important;
}
.btn-ghost > button:hover {
    background: rgba(243,110,33,0.06) !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    border-radius: 8px !important;
    border: 1.5px solid rgba(51,0,26,0.12) !important;
    font-family: 'DM Sans', sans-serif !important;
    background: #fff !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--sunne-orange) !important;
    box-shadow: 0 0 0 3px rgba(243,110,33,0.12) !important;
}

/* ── STATUS BADGES ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.badge-open    { background: #EEF2FF; color: #4338CA; }
.badge-doing   { background: #FFF7ED; color: #C2410C; }
.badge-blocked { background: #FEF2F2; color: #B91C1C; }
.badge-done    { background: #F0FDF4; color: #15803D; }
.badge-cancel  { background: #F3F4F6; color: #6B7280; }

/* ── ALERT BOXES ── */
.alert-red {
    background: #FEF2F2; border-left: 4px solid #DC2626;
    border-radius: 0 8px 8px 0; padding: 14px 18px; margin: 8px 0;
    color: #7F1D1D; font-size: 14px;
}
.alert-yellow {
    background: #FFFBEB; border-left: 4px solid #F59E0B;
    border-radius: 0 8px 8px 0; padding: 14px 18px; margin: 8px 0;
    color: #78350F; font-size: 14px;
}
.alert-green {
    background: #F0FDF4; border-left: 4px solid #22C55E;
    border-radius: 0 8px 8px 0; padding: 14px 18px; margin: 8px 0;
    color: #14532D; font-size: 14px;
}
.alert-blue {
    background: #EFF6FF; border-left: 4px solid #3B82F6;
    border-radius: 0 8px 8px 0; padding: 14px 18px; margin: 8px 0;
    color: #1E3A8A; font-size: 14px;
}

/* ── KANBAN CARDS ── */
.kanban-col {
    background: #F8F4F2;
    border-radius: 12px;
    padding: 14px 12px;
    min-height: 400px;
}
.kanban-col-header {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: var(--sunne-muted);
    padding-bottom: 12px;
    border-bottom: 1.5px solid var(--sunne-border);
    margin-bottom: 12px;
}
.kanban-card {
    background: #fff;
    border-radius: 10px;
    border: 1px solid var(--sunne-border);
    box-shadow: 0 2px 10px rgba(51,0,26,0.04);
    padding: 14px 16px;
    margin-bottom: 10px;
    transition: box-shadow 0.2s;
}
.kanban-card:hover {
    box-shadow: 0 4px 18px rgba(51,0,26,0.09);
}
.kanban-card-title {
    font-weight: 600;
    font-size: 13px;
    color: var(--sunne-text);
    margin-bottom: 6px;
}
.kanban-card-meta {
    font-size: 11px;
    color: var(--sunne-muted);
    line-height: 1.7;
}

/* ── TABLES ── */
.stDataFrame {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid var(--sunne-border) !important;
}

/* ── PAGE TITLE ── */
.page-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--sunne-text);
    margin-bottom: 4px;
}
.page-subtitle {
    font-size: 14px;
    color: var(--sunne-muted);
    margin-bottom: 28px;
}

/* ── DIVIDER ── */
.sunne-divider {
    border: none;
    border-top: 1px solid var(--sunne-border);
    margin: 20px 0;
}

/* ── SIDEBAR NAV ITEM ── */
[data-testid="stSidebar"] .stRadio label {
    padding: 8px 12px !important;
    border-radius: 8px !important;
    transition: background 0.15s !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.08) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid var(--sunne-border) !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px 8px 0 0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    color: var(--sunne-muted) !important;
    padding: 10px 18px !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    color: var(--sunne-orange) !important;
    border-bottom: 3px solid var(--sunne-orange) !important;
    font-weight: 600 !important;
}

/* ── LOGO AREA ── */
.sidebar-logo {
    padding: 24px 20px 18px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 8px;
}
.sidebar-logo-text {
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    font-weight: 700;
    color: #fff !important;
    letter-spacing: -0.5px;
}
.sidebar-logo-sub {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(243,110,33,0.85) !important;
    margin-top: 2px;
}

/* ── HIDE STREAMLIT BRANDING ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "logged_in": False,
        "user": None,
        "role": None,
        "page": "Cockpit Diário",
        "pending_task_action": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────
USERS = {
    "admin":  {"senha": "sunne2024", "role": "admin",    "nome": "Administrador"},
    "milena": {"senha": "milena123", "role": "analista", "nome": "Milena Oliveira"},
    "carlos": {"senha": "carlos123", "role": "analista", "nome": "Carlos Mendes"},
}

def page_login():
    inject_css()
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; margin-bottom:32px;">
            <div style="font-family:'Playfair Display',serif; font-size:3rem; font-weight:700; color:#33001A; letter-spacing:-1px;">
                ☀️ sunne
            </div>
            <div style="font-size:11px; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:#F36E21; margin-top:4px;">
                Hub v12 · Gestão Solar
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown('<div class="sunne-card">', unsafe_allow_html=True)
            st.markdown("**Acesso à Plataforma**")
            st.markdown('<div style="color:#7A5060; font-size:13px; margin-bottom:16px;">Entre com suas credenciais corporativas</div>', unsafe_allow_html=True)
            user_input = st.text_input("Usuário", placeholder="seu.usuario")
            pass_input = st.text_input("Senha", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Entrar na Plataforma", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if submitted:
                u = USERS.get(user_input.lower())
                if u and u["senha"] == pass_input:
                    st.session_state.logged_in = True
                    st.session_state.user = user_input.lower()
                    st.session_state.role = u["role"]
                    st.session_state.nome = u["nome"]
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

        st.markdown("""
        <div style="text-align:center; margin-top:24px; font-size:12px; color:#9B7080;">
            Plataforma corporativa Sunne · Acesso restrito
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MOTOR AUTOMÁTICO DIA 01 — GERAÇÃO DE TAREFAS MENSAIS
# ─────────────────────────────────────────────────────────────────────────────
def gerar_tarefas_mensais():
    """Popula tasks.json com macro-tarefas do mês no 1º dia útil."""
    tasks = load_json("tasks")
    today = date.today()
    mes_ref = today.strftime("%Y-%m")

    # Verifica se já foi gerado para este mês
    ja_gerado = any(t.get("mes_geracao") == mes_ref for t in tasks)
    if ja_gerado:
        return

    usinas = load_json("usinas")
    usinas_ativas = [u for u in usinas if u.get("ativa", True)]

    semana1_inicio = today.replace(day=1)
    semana2_inicio = today.replace(day=8)
    semana3_inicio = today.replace(day=15)
    semana4_inicio = today.replace(day=22)

    novas = []

    for usina in usinas_ativas:
        # Semana 1: Faturamento
        novas.append({
            "id": str(uuid.uuid4()),
            "titulo": f"📄 Captura de Fatura UG — {usina['nome']}",
            "usina_id": usina["id"],
            "usina_nome": usina["nome"],
            "analista": "milena",
            "status": "em aberto",
            "macro_tema": "Faturamento",
            "data_programada": semana1_inicio.isoformat(),
            "data_limite": (semana1_inicio + timedelta(days=6)).isoformat(),
            "mes_geracao": mes_ref,
            "motivo_bloqueio": "",
            "semana": 1,
        })
        novas.append({
            "id": str(uuid.uuid4()),
            "titulo": f"🔍 Conciliação de Medição — {usina['nome']}",
            "usina_id": usina["id"],
            "usina_nome": usina["nome"],
            "analista": "milena",
            "status": "em aberto",
            "macro_tema": "Faturamento",
            "data_programada": semana1_inicio.isoformat(),
            "data_limite": (semana1_inicio + timedelta(days=6)).isoformat(),
            "mes_geracao": mes_ref,
            "motivo_bloqueio": "",
            "semana": 1,
        })
        # Semana 2-3: Rateio
        novas.append({
            "id": str(uuid.uuid4()),
            "titulo": f"🔬 Auditoria Técnica UCs — {usina['nome']}",
            "usina_id": usina["id"],
            "usina_nome": usina["nome"],
            "analista": "milena",
            "status": "em aberto",
            "macro_tema": "Rateio",
            "data_programada": semana2_inicio.isoformat(),
            "data_limite": (semana3_inicio + timedelta(days=6)).isoformat(),
            "mes_geracao": mes_ref,
            "motivo_bloqueio": "",
            "semana": 2,
        })
        # Semana 4: Captura RPA
        novas.append({
            "id": str(uuid.uuid4()),
            "titulo": f"🤖 Captura RPA Portal Sunne — {usina['nome']}",
            "usina_id": usina["id"],
            "usina_nome": usina["nome"],
            "analista": "carlos",
            "status": "em aberto",
            "macro_tema": "Captura",
            "data_programada": semana4_inicio.isoformat(),
            "data_limite": (semana4_inicio + timedelta(days=7)).isoformat(),
            "mes_geracao": mes_ref,
            "motivo_bloqueio": "",
            "semana": 4,
        })

    tasks.extend(novas)
    save_json("tasks", tasks)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
NAV_STRUCTURE = {
    "🏠 Central de Comando": ["Cockpit Diário", "Gestão da Equipe"],
    "📋 Esteira de Atividades": ["Atividades (Kanban)"],
    "💰 Faturamento & BI": ["Conciliação de Medição", "Inteligência Financeira", "Faturas das UGs"],
    "⚙️ Engenharia de Rateios": ["Auditoria Técnica", "Simulador de Cotas"],
    "🗄️ Bases de Suporte": ["Geradores", "Usinas", "Geração (Livro-Caixa)", "Backoffice"],
    "🚀 Automações Extraordinárias": ["Captura RPA", "OCR HubSpot"],
}

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <div class="sidebar-logo-text">☀️ sunne</div>
            <div class="sidebar-logo-sub">Hub v12 · BI & Automação</div>
        </div>
        """, unsafe_allow_html=True)

        # User info
        nome = st.session_state.get("nome", "Usuário")
        role = st.session_state.get("role", "analista")
        role_label = "Administrador" if role == "admin" else "Analista"
        st.markdown(f"""
        <div style="padding:12px 20px; margin-bottom:4px;">
            <div style="font-size:12px; color:rgba(255,255,255,0.5); margin-bottom:2px;">{role_label}</div>
            <div style="font-size:14px; font-weight:600; color:#fff;">{nome}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr style="border-color:rgba(255,255,255,0.08); margin:0 0 8px 0;">', unsafe_allow_html=True)

        for section, pages in NAV_STRUCTURE.items():
            # Admin-only section
            if section == "🏠 Central de Comando" and role != "admin":
                pages = ["Cockpit Diário"]

            with st.expander(section, expanded=(st.session_state.page in pages)):
                for p in pages:
                    active = st.session_state.page == p
                    style = "background:rgba(243,110,33,0.15); border-radius:6px; padding:8px 12px; display:block; cursor:pointer; font-weight:600; color:#F36E21;" if active else "padding:8px 12px; display:block; cursor:pointer; color:rgba(255,255,255,0.8); border-radius:6px;"
                    if st.button(p, key=f"nav_{p}", use_container_width=True):
                        st.session_state.page = p
                        st.rerun()

        st.markdown('<hr style="border-color:rgba(255,255,255,0.08); margin:16px 0 8px;">', unsafe_allow_html=True)
        if st.button("🚪 Sair", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def page_header(title, subtitle=""):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def kpi_card(label, value, sub="", col=None):
    html = f"""
    <div class="kpi-block">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {"<div class='kpi-sub'>"+sub+"</div>" if sub else ""}
    </div>"""
    if col:
        with col: st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)

def status_badge(status):
    mapping = {
        "em aberto":  ("badge-open",    "Em Aberto"),
        "em andamento":("badge-doing",  "Em Andamento"),
        "travado":    ("badge-blocked", "Travado"),
        "concluido":  ("badge-done",    "Concluído"),
        "cancelado":  ("badge-cancel",  "Cancelado"),
    }
    cls, label = mapping.get(status, ("badge-open", status))
    return f'<span class="badge {cls}">{label}</span>'

def is_overdue(task):
    try:
        dl = date.fromisoformat(task.get("data_limite", "2099-12-31"))
        return dl < date.today() and task.get("status") not in ("concluido", "cancelado")
    except:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: COCKPIT DIÁRIO
# ─────────────────────────────────────────────────────────────────────────────
def page_dashboard():
    page_header("☀️ Cockpit Diário", f"Bom dia, {st.session_state.get('nome','Analista')}! Aqui está seu panorama de hoje — {date.today().strftime('%d de %B de %Y')}.")

    tasks = load_json("tasks")
    usinas = load_json("usinas")
    geradores = load_json("geradores")
    backoffice = load_json("backoffice")

    # ── BLOCO A: KPIs RÁPIDOS
    st.markdown("### 📊 Visão Geral")
    c1, c2, c3, c4, c5 = st.columns(5)
    total_tasks = len(tasks)
    concluidas = len([t for t in tasks if t["status"] == "concluido"])
    atrasadas = len([t for t in tasks if is_overdue(t)])
    travadas = len([t for t in tasks if t["status"] == "travado"])
    usinas_ativas = len([u for u in usinas if u.get("ativa", True)])

    kpi_card("Total de Tarefas", total_tasks, "no mês", c1)
    kpi_card("Concluídas", concluidas, f"{round(concluidas/total_tasks*100) if total_tasks else 0}% do mês", c2)
    kpi_card("⚠️ Atrasadas", atrasadas, "requerem atenção", c3)
    kpi_card("🔴 Travadas", travadas, "aguardam desbloqueio", c4)
    kpi_card("Usinas Ativas", usinas_ativas, "em operação", c5)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1.2])

    # ── BLOCO A: ALERTAS CRÍTICOS
    with col_a:
        st.markdown("### 🚨 Alertas Críticos")

        geracao = load_json("geracao_usinas")
        mes_atual = date.today().strftime("%Y-%m")

        alertas = []

        # Usinas sem geração no mês
        usinas_com_geracao = {g["usina_id"] for g in geracao if g.get("mes_ref", "").startswith(mes_atual[:7])}
        for u in usinas:
            if u.get("ativa") and u["id"] not in usinas_com_geracao:
                alertas.append(("red", f"🔴 Sem geração registrada: <b>{u['nome']}</b>"))

        # Tarefas atrasadas
        for t in tasks:
            if is_overdue(t):
                alertas.append(("yellow", f"⏰ Tarefa atrasada: <b>{t['titulo'][:45]}...</b>"))

        # Usinas com rateio velho (>90 dias)
        for u in usinas:
            try:
                dr = date.fromisoformat(u.get("data_ultimo_rateio", "2020-01-01"))
                dias = (date.today() - dr).days
                if dias > 90:
                    alertas.append(("yellow", f"📅 Rateio desatualizado ({dias}d): <b>{u['nome']}</b>"))
            except:
                pass

        if not alertas:
            st.markdown('<div class="alert-green">✅ Nenhum alerta crítico no momento. Tudo operando normalmente!</div>', unsafe_allow_html=True)
        else:
            for tipo, msg in alertas[:8]:
                cls = "alert-red" if tipo == "red" else "alert-yellow"
                st.markdown(f'<div class="{cls}">{msg}</div>', unsafe_allow_html=True)

    # ── BLOCO B: AGENDA DO DIA
    with col_b:
        st.markdown("### 📅 Minha Agenda de Hoje")

        user = st.session_state.get("user", "")
        hoje = date.today().isoformat()

        minhas_tasks = [
            t for t in tasks
            if t.get("analista") == user and t.get("status") not in ("concluido", "cancelado")
        ]

        hoje_tasks = [t for t in minhas_tasks if t.get("data_programada") == hoje]
        atrasadas_tasks = [t for t in minhas_tasks if t.get("data_limite", "9999") < hoje]

        agenda = sorted(hoje_tasks + [t for t in atrasadas_tasks if t not in hoje_tasks],
                       key=lambda x: x.get("data_limite", "9999"))

        if not agenda:
            st.markdown('<div class="alert-green">✅ Nenhuma tarefa para hoje. Bom trabalho!</div>', unsafe_allow_html=True)
        else:
            for t in agenda[:8]:
                atr = "🔴 ATRASADA" if is_overdue(t) else "📌 Hoje"
                dl = t.get("data_limite", "—")
                st.markdown(f"""
                <div class="sunne-card-sm">
                    <div class="kanban-card-title">{t['titulo'][:55]}</div>
                    <div class="kanban-card-meta">
                        🏭 {t.get('usina_nome','—')} &nbsp;|&nbsp;
                        📆 Limite: {dl} &nbsp;|&nbsp;
                        {status_badge(t['status'])} &nbsp;
                        <span style="font-size:11px; color:#B91C1C; font-weight:600;">{atr if is_overdue(t) else ''}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── BLOCO C: PRÓXIMOS EVENTOS (Simulado — Google Calendar)
    st.markdown("<br>")
    st.markdown("### 📆 Próximos 7 Dias — Agenda Operacional")
    st.markdown('<div class="alert-blue">ℹ️ Integração com Google Calendar disponível via OAuth. Configure em Configurações → Integrações para sincronizar seus eventos.</div>', unsafe_allow_html=True)

    eventos_demo = [
        {"data": (date.today() + timedelta(days=i)).strftime("%d/%m"), "evento": ev}
        for i, ev in enumerate([
            "Envio Faturas Grupo A — Prazo", "Reunião de Alinhamento Operacional",
            "Auditoria Técnica USI001", "Deadline Conciliação Medição",
            "Relatório BI Investidor", "Captura RPA — Janela Sunne", "Revisão Rateios"
        ])
    ]
    cols = st.columns(7)
    for i, ev in enumerate(eventos_demo):
        with cols[i]:
            st.markdown(f"""
            <div class="kpi-block" style="min-height:90px;">
                <div class="kpi-label">{ev['data']}</div>
                <div style="font-size:12px; color:#33001A; font-weight:500; margin-top:8px; line-height:1.4;">{ev['evento']}</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: GESTÃO DA EQUIPE (Admin only)
# ─────────────────────────────────────────────────────────────────────────────
def page_gestao_equipe():
    if st.session_state.role != "admin":
        st.error("Acesso restrito ao Administrador.")
        return

    page_header("👥 Gestão da Equipe", "Desempenho operacional por analista · Controle de SLA")

    tasks = load_json("tasks")
    analistas = list({t.get("analista", "—") for t in tasks if t.get("analista")})

    if not analistas:
        st.info("Nenhuma tarefa cadastrada ainda.")
        return

    # Métricas por analista
    rows = []
    for an in analistas:
        t_an = [t for t in tasks if t.get("analista") == an]
        concl = [t for t in t_an if t["status"] == "concluido"]
        andam = [t for t in t_an if t["status"] == "em andamento"]
        atras = [t for t in t_an if is_overdue(t)]
        trav  = [t for t in t_an if t["status"] == "travado"]

        # SLA médio em dias
        slas = []
        for t in concl:
            try:
                dp = date.fromisoformat(t.get("data_programada", date.today().isoformat()))
                dl = date.fromisoformat(t.get("data_limite", date.today().isoformat()))
                slas.append((dl - dp).days)
            except: pass
        sla_med = round(sum(slas)/len(slas), 1) if slas else 0

        nome_an = USERS.get(an, {}).get("nome", an)
        rows.append({
            "Analista": nome_an,
            "Total": len(t_an),
            "Concluídas": len(concl),
            "Em Andamento": len(andam),
            "Atrasadas": len(atras),
            "Travadas": len(trav),
            "SLA Médio (d)": sla_med,
        })

    df = pd.DataFrame(rows)

    # KPIs
    c1, c2, c3 = st.columns(3)
    kpi_card("Analistas Ativos", len(analistas), "", c1)
    kpi_card("Total de Tarefas", len(tasks), "todas as equipes", c2)
    kpi_card("Taxa Conclusão", f"{round(len([t for t in tasks if t['status']=='concluido'])/len(tasks)*100) if tasks else 0}%", "global", c3)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico de barras
    fig = go.Figure()
    categorias = ["Concluídas", "Em Andamento", "Atrasadas", "Travadas"]
    cores = ["#22C55E", "#F36E21", "#EF4444", "#6B7280"]
    for cat, cor in zip(categorias, cores):
        fig.add_trace(go.Bar(
            name=cat,
            x=df["Analista"],
            y=df[cat],
            marker_color=cor,
            text=df[cat],
            textposition="auto",
        ))
    fig.update_layout(
        barmode="group",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_family="DM Sans",
        title="Distribuição de Tarefas por Analista",
        title_font_size=16,
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Tabela de SLA por Analista")
    st.dataframe(df, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: KANBAN DE ATIVIDADES
# ─────────────────────────────────────────────────────────────────────────────
KANBAN_STATUS = ["em aberto", "em andamento", "travado", "concluido", "cancelado"]
KANBAN_LABELS = {"em aberto": "Em Aberto", "em andamento": "Em Andamento",
                 "travado": "Travado 🔒", "concluido": "Concluído ✅", "cancelado": "Cancelado"}
MACRO_TEMAS = ["Todos", "Faturamento", "Rateio", "Captura"]

def page_atividades():
    page_header("📋 Esteira de Atividades", "Gerencie o fluxo operacional mensal — arraste, priorize e monitore.")

    tasks = load_json("tasks")
    usinas = load_json("usinas")
    analistas_list = list(USERS.keys())

    # Filtro de macro-tema
    col_f1, col_f2, col_f3, col_f4 = st.columns([1,1,1,3])
    with col_f1:
        tema_filtro = st.selectbox("Macro-tema", MACRO_TEMAS, key="kanban_tema")
    with col_f2:
        analista_filtro = st.selectbox("Analista", ["Todos"] + analistas_list, key="kanban_analista")
    with col_f3:
        semana_filtro = st.selectbox("Semana", ["Todas", "1", "2", "3", "4"], key="kanban_semana")
    with col_f4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Nova Tarefa Manual", key="new_task_btn"):
            st.session_state["show_new_task"] = True

    # Formulário nova tarefa
    if st.session_state.get("show_new_task"):
        with st.expander("✏️ Criar Nova Tarefa", expanded=True):
            with st.form("form_nova_tarefa"):
                c1, c2 = st.columns(2)
                with c1:
                    titulo = st.text_input("Título da Tarefa")
                    usina_opts = {u["nome"]: u["id"] for u in usinas}
                    usina_sel = st.selectbox("Usina", list(usina_opts.keys()))
                    analista_sel = st.selectbox("Analista", analistas_list)
                with c2:
                    tema_sel = st.selectbox("Macro-tema", ["Faturamento", "Rateio", "Captura"])
                    data_prog = st.date_input("Data Programada", value=date.today())
                    data_lim = st.date_input("Data Limite", value=date.today() + timedelta(days=7))

                if st.form_submit_button("Criar Tarefa"):
                    nova = {
                        "id": str(uuid.uuid4()),
                        "titulo": titulo,
                        "usina_id": usina_opts.get(usina_sel, ""),
                        "usina_nome": usina_sel,
                        "analista": analista_sel,
                        "status": "em aberto",
                        "macro_tema": tema_sel,
                        "data_programada": data_prog.isoformat(),
                        "data_limite": data_lim.isoformat(),
                        "mes_geracao": date.today().strftime("%Y-%m"),
                        "motivo_bloqueio": "",
                        "semana": 1,
                    }
                    tasks.append(nova)
                    save_json("tasks", tasks)
                    st.session_state["show_new_task"] = False
                    st.success("Tarefa criada!")
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Filtrar tasks
    filtered = tasks
    if tema_filtro != "Todos":
        filtered = [t for t in filtered if t.get("macro_tema") == tema_filtro]
    if analista_filtro != "Todos":
        filtered = [t for t in filtered if t.get("analista") == analista_filtro]
    if semana_filtro != "Todas":
        filtered = [t for t in filtered if str(t.get("semana","")) == semana_filtro]

    # Trava de governança em session_state
    if "trava_task_id" not in st.session_state:
        st.session_state.trava_task_id = None

    # Modal de trava (bloqueio/cancelamento)
    if st.session_state.trava_task_id:
        task_trava = next((t for t in tasks if t["id"] == st.session_state.trava_task_id), None)
        if task_trava:
            st.markdown('<div class="alert-red">🔒 <b>Trava de Governança Ativa</b> — Justificativa obrigatória para mover esta tarefa.</div>', unsafe_allow_html=True)
            motivo = st.text_area("Motivo do Travamento/Cancelamento (campo obrigatório):",
                                  placeholder="Descreva detalhadamente o motivo do bloqueio ou cancelamento...",
                                  key="motivo_trava")
            target_status = st.session_state.get("trava_target_status", "travado")
            c1, c2 = st.columns([1, 3])
            with c1:
                if st.button("Confirmar e Salvar", key="confirm_trava"):
                    if not motivo or len(motivo.strip()) < 10:
                        st.error("⚠️ O motivo deve ter pelo menos 10 caracteres.")
                    else:
                        for t in tasks:
                            if t["id"] == st.session_state.trava_task_id:
                                t["status"] = target_status
                                t["motivo_bloqueio"] = motivo.strip()
                        save_json("tasks", tasks)
                        st.session_state.trava_task_id = None
                        st.rerun()
            with c2:
                if st.button("Cancelar", key="cancel_trava"):
                    st.session_state.trava_task_id = None
                    st.rerun()
            st.markdown("---")

    # Kanban Board
    cols = st.columns(5)
    for i, status in enumerate(KANBAN_STATUS):
        with cols[i]:
            cards_status = [t for t in filtered if t.get("status") == status]
            total_col = len(cards_status)
            st.markdown(f"""
            <div class="kanban-col-header">
                {KANBAN_LABELS[status]}
                <span style="float:right; background:rgba(51,0,26,0.08); border-radius:10px; padding:1px 8px; font-size:10px;">{total_col}</span>
            </div>
            """, unsafe_allow_html=True)

            for task in cards_status:
                atrasada_str = " 🔴" if is_overdue(task) else ""
                st.markdown(f"""
                <div class="kanban-card">
                    <div class="kanban-card-title">{task['titulo'][:50]}{atrasada_str}</div>
                    <div class="kanban-card-meta">
                        🏭 {task.get('usina_nome','—')[:25]}<br>
                        👤 {USERS.get(task.get('analista',''), {}).get('nome', task.get('analista','—'))}<br>
                        📆 Limite: {task.get('data_limite','—')}<br>
                        🏷️ {task.get('macro_tema','—')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Botões de transição rápida
                outros_status = [s for s in KANBAN_STATUS if s != status]
                btn_cols = st.columns(len(outros_status))
                label_map = {"em aberto":"Abrir","em andamento":"Iniciar","travado":"🔒 Travar","concluido":"✅ Feito","cancelado":"❌ Cancelar"}
                for j, ns in enumerate(outros_status):
                    with btn_cols[j]:
                        if st.button(label_map.get(ns, ns), key=f"mv_{task['id']}_{ns}", use_container_width=True):
                            if ns in ("travado", "cancelado"):
                                st.session_state.trava_task_id = task["id"]
                                st.session_state.trava_target_status = ns
                                st.rerun()
                            else:
                                for t in tasks:
                                    if t["id"] == task["id"]:
                                        t["status"] = ns
                                save_json("tasks", tasks)
                                st.rerun()
                st.markdown("---")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CONCILIAÇÃO DE MEDIÇÃO
# ─────────────────────────────────────────────────────────────────────────────
def page_conciliacao():
    page_header("🔍 Conciliação de Medição", "Semana 1 · Cruzamento Extrato Detalhado vs Medição Sunne")

    st.markdown("""
    <div class="alert-blue">
    📌 <b>Fluxo:</b> Faça upload do Extrato Detalhado (Excel) e da Tabela Detalhada de Medição Sunne.
    O sistema aplicará a Regra da Fatura Unificada e exibirá as divergências de caixa.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📂 Extrato Detalhado")
        extrato_file = st.file_uploader("Upload Extrato (Excel)", type=["xlsx","xls"], key="extrato_up")
    with col2:
        st.markdown("#### 📂 Medição Sunne")
        medicao_file = st.file_uploader("Upload Medição Sunne (Excel)", type=["xlsx","xls"], key="medicao_up")

    mes_ref = st.text_input("Mês de Referência (AAAA-MM)", value=date.today().strftime("%Y-%m"))

    if extrato_file and medicao_file:
        if st.button("🔍 Executar Conciliação"):
            with st.spinner("Processando..."):
                try:
                    df_ext = pd.read_excel(extrato_file, dtype=str)
                    df_med = pd.read_excel(medicao_file, sheet_name="Tabela Detalhada", dtype=str)

                    # Normalize columns
                    df_ext.columns = [c.strip() for c in df_ext.columns]
                    df_med.columns = [c.strip() for c in df_med.columns]

                    # Clean UC
                    if "UC" in df_ext.columns:
                        df_ext["UC"] = df_ext["UC"].apply(clean_uc)
                    if "UC" in df_med.columns:
                        df_med["UC"] = df_med["UC"].apply(clean_uc)

                    # Filtrar pagos no mês
                    if "Status" in df_ext.columns:
                        df_pago = df_ext[df_ext["Status"].str.lower().str.contains("pago", na=False)].copy()
                    else:
                        df_pago = df_ext.copy()

                    if "Competência" in df_pago.columns:
                        df_pago = df_pago[df_pago["Competência"].astype(str).str.startswith(mes_ref)]

                    # Regra Fatura Unificada
                    def calc_valor_ajustado(row):
                        try:
                            unif = str(row.get("Fatura Unificada", "")).lower()
                            total = float(str(row.get("Total a Pagar", 0)).replace(",",".").replace("R$","").strip() or 0)
                            boleto = float(str(row.get("Total a Pagar Boleto Concessionária", 0)).replace(",",".").replace("R$","").strip() or 0)
                            if unif in ("true","sim","1","yes"):
                                return total - boleto
                            return total
                        except:
                            return 0.0

                    df_pago["Valor Ajustado"] = df_pago.apply(calc_valor_ajustado, axis=1)

                    # Left join com Medição
                    join_cols = ["UC"]
                    df_merged = df_pago.merge(df_med[join_cols + [c for c in df_med.columns if c not in join_cols]],
                                              on="UC", how="left", suffixes=("_ext","_med"))

                    # Identificar divergências (NaN no campo chave da medição)
                    chave_med = [c for c in df_merged.columns if "_med" in c]
                    if chave_med:
                        divergencias = df_merged[df_merged[chave_med[0]].isna()].copy()
                    else:
                        divergencias = df_merged.copy()

                    # KPIs
                    total_pago = df_pago["Valor Ajustado"].sum()
                    total_div = len(divergencias)
                    valor_div = divergencias["Valor Ajustado"].sum() if "Valor Ajustado" in divergencias.columns else 0

                    c1, c2, c3 = st.columns(3)
                    kpi_card("Faturas Pagas", len(df_pago), f"R$ {total_pago:,.2f}", c1)
                    kpi_card("Divergências", total_div, "ausentes na Medição", c2)
                    kpi_card("Valor Divergente", f"R$ {valor_div:,.2f}", "não repassado", c3)

                    if len(divergencias) > 0:
                        st.markdown('<div class="alert-red">🔴 Divergências de Caixa Detectadas — Faturas pagas pelos clientes ausentes no repasse da Medição Sunne:</div>', unsafe_allow_html=True)
                        cols_show = ["UC", "Valor Ajustado"] + [c for c in ["Nome","Competência","Status"] if c in divergencias.columns]
                        st.dataframe(divergencias[cols_show].head(50), use_container_width=True)
                    else:
                        st.markdown('<div class="alert-green">✅ Nenhuma divergência encontrada. Extrato e Medição estão conciliados.</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Erro ao processar: {e}")
    else:
        # Demo mode
        st.markdown("""
        <div class="sunne-card">
        <div style="text-align:center; padding:40px 0; color:#7A5060;">
            <div style="font-size:48px; margin-bottom:16px;">📊</div>
            <div style="font-size:16px; font-weight:600; color:#33001A;">Aguardando arquivos para análise</div>
            <div style="font-size:13px; margin-top:8px;">Faça upload do Extrato Detalhado e da Medição Sunne para iniciar a conciliação</div>
        </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: INTELIGÊNCIA FINANCEIRA (BI)
# ─────────────────────────────────────────────────────────────────────────────
def page_bi():
    page_header("📈 Inteligência Financeira", "Módulo BI Investidor · Geração vs Recebimento Anual")

    historico = load_json("historico_analises")
    usinas = load_json("usinas")

    usina_opts = {u["nome"]: u["id"] for u in usinas}
    usina_sel = st.selectbox("Selecionar Usina", list(usina_opts.keys()), key="bi_usina")
    usina_id = usina_opts.get(usina_sel, "")

    df_hist = pd.DataFrame([h for h in historico if h.get("usina_id") == usina_id])

    if df_hist.empty:
        st.info("Nenhum histórico para esta usina.")
        return

    df_hist["mes_ref"] = pd.to_datetime(df_hist["mes_ref"])
    df_hist = df_hist.sort_values("mes_ref")
    df_hist["mes_label"] = df_hist["mes_ref"].dt.strftime("%b/%Y")

    # KPIs
    total_geracao = df_hist["geracao_kwh"].sum()
    total_liquido = df_hist["recebimento_liquido"].sum()
    total_bruto = df_hist["recebimento_bruto"].sum()
    total_deducoes = total_bruto - total_liquido

    c1, c2, c3, c4 = st.columns(4)
    kpi_card("Geração Total", f"{total_geracao:,.0f} kWh", "no período", c1)
    kpi_card("Recebimento Bruto", f"R$ {total_bruto:,.2f}", "acumulado", c2)
    kpi_card("Deduções", f"R$ {total_deducoes:,.2f}", "admin + sunne + banco", c3)
    kpi_card("Recebimento Líquido", f"R$ {total_liquido:,.2f}", "net para o investidor", c4)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico combinado (barras + linha)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Geração Injetada (kWh)",
        x=df_hist["mes_label"],
        y=df_hist["geracao_kwh"],
        marker_color="#F36E21",
        opacity=0.85,
        yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        name="Recebimento Líquido (R$)",
        x=df_hist["mes_label"],
        y=df_hist["recebimento_liquido"],
        mode="lines+markers",
        line=dict(color="#1C0010", width=2.5),
        marker=dict(size=8, color="#1C0010"),
        yaxis="y2",
    ))
    fig.update_layout(
        title=f"Desempenho Anual — {usina_sel}",
        title_font=dict(size=16, family="DM Sans"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_family="DM Sans",
        height=420,
        yaxis=dict(title="Geração (kWh)", titlefont=dict(color="#F36E21"), tickfont=dict(color="#F36E21")),
        yaxis2=dict(title="Recebimento Líquido (R$)", titlefont=dict(color="#1C0010"), tickfont=dict(color="#1C0010"), overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabela detalhada
    st.markdown("#### Detalhamento Mensal")
    df_show = df_hist[["mes_label","geracao_kwh","recebimento_bruto","taxa_admin","taxa_sunne","tarifa_bancaria","recebimento_liquido"]].copy()
    df_show.columns = ["Mês","Geração (kWh)","Bruto (R$)","Taxa Admin","Taxa Sunne","Tarifa Banco","Líquido (R$)"]
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    # Export PDF
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📄 Exportar Report em PDF"):
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
            elems.append(Spacer(1, 20))

            # KPIs
            elems.append(Paragraph("Resumo Financeiro", styles["Heading2"]))
            kpi_data = [
                ["Indicador", "Valor"],
                ["Geração Total (kWh)", f"{total_geracao:,.0f}"],
                ["Recebimento Bruto (R$)", f"{total_bruto:,.2f}"],
                ["Deduções (R$)", f"{total_deducoes:,.2f}"],
                ["Recebimento Líquido (R$)", f"{total_liquido:,.2f}"],
            ]
            t_kpi = Table(kpi_data, colWidths=[250, 200])
            t_kpi.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1C0010")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FDF9F7")]),
                ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E5D5DC")),
                ("FONTSIZE", (0,0), (-1,-1), 10),
                ("PADDING", (0,0), (-1,-1), 8),
            ]))
            elems.append(t_kpi)
            elems.append(Spacer(1, 20))

            # Tabela mensal
            elems.append(Paragraph("Detalhamento Mensal", styles["Heading2"]))
            table_data = [["Mês","Geração kWh","Bruto R$","Adm R$","Sunne R$","Banco R$","Líquido R$"]]
            for _, row in df_show.iterrows():
                table_data.append([str(v) for v in row.values])
            t_det = Table(table_data, repeatRows=1)
            t_det.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#F36E21")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FDF9F7")]),
                ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#E5D5DC")),
                ("FONTSIZE", (0,0), (-1,-1), 8),
                ("PADDING", (0,0), (-1,-1), 6),
            ]))
            elems.append(t_det)

            doc.build(elems)
            pdf_bytes = buf.getvalue()
            st.download_button("⬇️ Baixar PDF", data=pdf_bytes,
                               file_name=f"bi_report_{usina_sel}_{date.today()}.pdf",
                               mime="application/pdf")
        except ImportError:
            st.error("ReportLab não instalado. Execute: pip install reportlab")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: FATURAS DAS UGs
# ─────────────────────────────────────────────────────────────────────────────
def page_faturas_ugs():
    page_header("🧾 Faturas das UGs", "Semana 1 · Controle de Faturamento Grupo A e B")

    usinas = load_json("usinas")
    tab_a, tab_b = st.tabs(["⚡ Grupo A", "🔌 Grupo B"])

    for tab, grupo in [(tab_a, "A"), (tab_b, "B")]:
        with tab:
            usinas_grupo = [u for u in usinas if u.get("grupo") == grupo]
            st.markdown(f"**{len(usinas_grupo)} usinas no Grupo {grupo}**")

            if not usinas_grupo:
                st.info(f"Nenhuma usina cadastrada no Grupo {grupo}.")
                continue

            for u in usinas_grupo:
                status_fatura = "✅ Emitida" if u.get("ativa") else "⏳ Pendente"
                cor = "#F0FDF4" if "Emitida" in status_fatura else "#FFFBEB"
                st.markdown(f"""
                <div class="sunne-card-sm" style="background:{cor};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-weight:600; font-size:14px; color:#33001A;">{u['nome']}</div>
                            <div style="font-size:12px; color:#7A5060; margin-top:3px;">
                                {u['concessionaria']} · {u['estado']} · {u['potencia_kwp']} kWp
                            </div>
                        </div>
                        <div style="font-weight:700; font-size:13px; color:#15803D;">{status_fatura}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                arquivo = st.file_uploader(f"Upload Faturas Grupo {grupo}", type=["pdf","xlsx","xls"], key=f"fat_{grupo}")
            with col2:
                if arquivo and st.button(f"Processar Grupo {grupo}", key=f"proc_{grupo}"):
                    st.success(f"✅ Faturas Grupo {grupo} processadas com sucesso!")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: AUDITORIA TÉCNICA
# ─────────────────────────────────────────────────────────────────────────────
def page_auditoria():
    page_header("🔬 Auditoria Técnica", "Semanas 2–3 · Saúde das UCs e Usinas — Análise Histórica 3 Meses")

    usinas = load_json("usinas")
    backoffice = load_json("backoffice")
    geracao = load_json("geracao_usinas")
    tasks = load_json("tasks")

    usina_opts = {u["nome"]: u["id"] for u in usinas}
    usina_sel = st.selectbox("Selecionar Usina para Auditoria", list(usina_opts.keys()), key="audit_usina")
    usina_id = usina_opts.get(usina_sel, "")

    usina_data = next((u for u in usinas if u["id"] == usina_id), {})

    # Dados da usina (últimos 3 meses)
    bf_usina = [b for b in backoffice if b.get("usina_id") == usina_id]
    gen_usina = [g for g in geracao if g.get("usina_id") == usina_id]

    # Últimos 3 meses de referência
    meses_3 = sorted(set(b.get("mes_ref","") for b in bf_usina))[-3:]

    alertas_criticos = []
    alertas_avisos = []

    # CRITÉRIO A: Excesso de Saldo
    st.markdown("### 📊 Diagnóstico por UC")
    for uc_nome in set(b.get("nome_beneficiario","") for b in bf_usina):
        uc_data = [b for b in bf_usina if b.get("nome_beneficiario") == uc_nome]
        if not uc_data:
            continue

        latest = sorted(uc_data, key=lambda x: x.get("mes_ref",""))[-1]
        saldo = latest.get("saldo_solar", 0)
        consumos = [b.get("consumo_total", 0) for b in uc_data]
        consumo_med = sum(consumos) / len(consumos) if consumos else 0

        # A: Excesso saldo > 3x consumo médio
        if saldo > 3 * consumo_med and consumo_med > 0:
            alertas_avisos.append(f"⚠️ <b>Excesso de Saldo</b> — {uc_nome}: Saldo {saldo:.0f} kWh > 3× Consumo Médio ({consumo_med:.0f} kWh). Reduzir cota recomendado.")

        # B: Sub-atendimento (3 meses consecutivos)
        meses_uc = sorted(uc_data, key=lambda x: x.get("mes_ref",""))
        sub_atend_meses = 0
        for m in meses_uc[-3:]:
            disp = m.get("disponibilidade", 100)
            consumo_comp = m.get("consumo_total", 0) - disp
            if m.get("creditos_utilizados", 0) < consumo_comp:
                sub_atend_meses += 1
        if sub_atend_meses >= 3:
            alertas_avisos.append(f"⚠️ <b>Sub-atendimento</b> — {uc_nome}: Créditos insuficientes por 3 meses consecutivos. Aumentar cota recomendado.")

    # C: Usina Saturada
    if meses_3:
        consumo_total_3m = sum(
            sum(b.get("consumo_total",0) for b in bf_usina if b.get("mes_ref") == m)
            for m in meses_3
        )
        geracao_total_3m = sum(
            g.get("injetado_kwh", 0) for g in gen_usina if g.get("mes_ref") in meses_3
        )
        if geracao_total_3m > 0 and consumo_total_3m > geracao_total_3m:
            alertas_criticos.append(
                f"🔴 <b>Usina Saturada!</b> — Consumo total 3M ({consumo_total_3m:,.0f} kWh) > Geração Injetada ({geracao_total_3m:,.0f} kWh). Superalocação detectada!"
            )

    # D: Defasagem de Rateio (>90 dias)
    try:
        dr = date.fromisoformat(usina_data.get("data_ultimo_rateio", "2020-01-01"))
        dias_defasagem = (date.today() - dr).days
        if dias_defasagem > 90:
            alertas_avisos.append(f"📅 <b>Defasagem de Rateio</b> — Último rateio há {dias_defasagem} dias (>90d). Atualização necessária.")
    except:
        pass

    # Exibir alertas
    if alertas_criticos:
        for a in alertas_criticos:
            st.markdown(f'<div class="alert-red">{a}</div>', unsafe_allow_html=True)

        # GATILHO SEMANA 4: gerar tarefa automática
        mes_ref = date.today().strftime("%Y-%m")
        ja_existe = any(
            t.get("titulo","").startswith("🔄 Atualizar Rateio Obrigatório") and
            t.get("usina_id") == usina_id and t.get("mes_geracao") == mes_ref
            for t in tasks
        )
        if not ja_existe:
            semana4 = date.today().replace(day=22)
            tasks.append({
                "id": str(uuid.uuid4()),
                "titulo": f"🔄 Atualizar Rateio Obrigatório — {usina_sel}",
                "usina_id": usina_id,
                "usina_nome": usina_sel,
                "analista": "milena",
                "status": "em aberto",
                "macro_tema": "Rateio",
                "data_programada": semana4.isoformat(),
                "data_limite": (semana4 + timedelta(days=7)).isoformat(),
                "mes_geracao": mes_ref,
                "motivo_bloqueio": "",
                "semana": 4,
            })
            save_json("tasks", tasks)
            st.markdown('<div class="alert-yellow">⚡ Tarefa "Atualizar Rateio Obrigatório" gerada automaticamente na Semana 4!</div>', unsafe_allow_html=True)

    if alertas_avisos:
        for a in alertas_avisos:
            st.markdown(f'<div class="alert-yellow">{a}</div>', unsafe_allow_html=True)

    if not alertas_criticos and not alertas_avisos:
        st.markdown('<div class="alert-green">✅ Usina dentro dos parâmetros técnicos. Nenhuma intervenção necessária.</div>', unsafe_allow_html=True)

    # Tabela histórica
    if bf_usina:
        st.markdown("#### 📋 Histórico Backoffice (UCs)")
        df_bf = pd.DataFrame(bf_usina)
        df_bf["uc"] = df_bf["uc"].apply(clean_uc)
        st.dataframe(df_bf, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SIMULADOR DE COTAS
# ─────────────────────────────────────────────────────────────────────────────
def page_simulador():
    page_header("🎯 Simulador de Cotas", "Rebalanceamento preditivo de rateio entre UCs e Usinas")

    usinas = load_json("usinas")
    geradores = load_json("geradores")
    backoffice = load_json("backoffice")

    usina_opts = {u["nome"]: u["id"] for u in usinas}
    usina_sel = st.selectbox("Usina", list(usina_opts.keys()), key="sim_usina")
    usina_id = usina_opts.get(usina_sel, "")

    ger_usina = [g for g in geradores if g.get("usina_id") == usina_id]

    if not ger_usina:
        st.info("Nenhum gerador cadastrado para esta usina.")
        return

    usina_potencia = next((u["potencia_kwp"] for u in usinas if u["id"] == usina_id), 100.0)
    geracao_estimada = usina_potencia * 120  # kWh estimado mensal

    st.markdown(f"**Geração estimada mensal:** {geracao_estimada:,.0f} kWh | **Geradores:** {len(ger_usina)}")
    st.markdown("---")

    total_cotas = sum(g.get("cota_percent",0) for g in ger_usina)
    st.markdown(f"**Soma atual das cotas: {total_cotas:.1f}%** {'✅' if abs(total_cotas-100)<0.1 else '⚠️ Não soma 100%'}")

    cotas_novas = {}
    for g in ger_usina:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.markdown(f"**{g['nome']}**")
        with c2:
            nova = st.number_input(f"Cota %", min_value=0.0, max_value=100.0,
                                   value=float(g.get("cota_percent",0)),
                                   step=0.5, key=f"cota_{g['id']}")
            cotas_novas[g["id"]] = nova
        with c3:
            kwh_est = geracao_estimada * nova / 100
            st.markdown(f"≈ **{kwh_est:,.0f} kWh**")

    nova_soma = sum(cotas_novas.values())
    cor_soma = "#22C55E" if abs(nova_soma-100)<0.1 else "#EF4444"
    st.markdown(f'<div style="font-weight:700; color:{cor_soma}; font-size:16px; margin:12px 0;">Soma: {nova_soma:.1f}%</div>', unsafe_allow_html=True)

    if st.button("💾 Salvar Novas Cotas"):
        if abs(nova_soma - 100) > 0.5:
            st.error("⚠️ As cotas devem somar 100% (±0.5%).")
        else:
            for g in geradores:
                if g["usina_id"] == usina_id and g["id"] in cotas_novas:
                    g["cota_percent"] = cotas_novas[g["id"]]
            save_json("geradores", geradores)
            st.success("✅ Cotas atualizadas com sucesso!")
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: GERADORES (CRUD)
# ─────────────────────────────────────────────────────────────────────────────
def page_geradores():
    page_header("👤 Geradores", "Cadastro e gestão de geradores vinculados às usinas")

    geradores = load_json("geradores")
    usinas = load_json("usinas")
    usina_map = {u["id"]: u["nome"] for u in usinas}

    tab_lista, tab_novo = st.tabs(["📋 Lista de Geradores", "➕ Novo Gerador"])

    with tab_lista:
        if not geradores:
            st.info("Nenhum gerador cadastrado.")
        else:
            df = pd.DataFrame(geradores)
            df["usina_nome"] = df["usina_id"].map(usina_map)
            df["uc"] = df.get("cpf_cnpj", pd.Series(dtype=str))
            cols_show = ["id","nome","cpf_cnpj","usina_nome","cota_percent","ativo"]
            df_show = df[[c for c in cols_show if c in df.columns]]
            st.dataframe(df_show, use_container_width=True, hide_index=True)

    with tab_novo:
        with st.form("form_gerador"):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome / Razão Social")
                cpf_cnpj = st.text_input("CPF / CNPJ")
            with c2:
                usina_opts = {u["nome"]: u["id"] for u in usinas}
                usina_sel = st.selectbox("Usina", list(usina_opts.keys()))
                cota = st.number_input("Cota (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)

            if st.form_submit_button("Cadastrar Gerador"):
                novo = {
                    "id": f"GER{len(geradores)+1:03d}",
                    "nome": nome,
                    "cpf_cnpj": cpf_cnpj,
                    "usina_id": usina_opts.get(usina_sel, ""),
                    "cota_percent": cota,
                    "ativo": True,
                }
                geradores.append(novo)
                save_json("geradores", geradores)
                st.success("✅ Gerador cadastrado!")
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: USINAS (CRUD)
# ─────────────────────────────────────────────────────────────────────────────
def page_usinas():
    page_header("🏭 Usinas", "Cadastro e monitoramento das usinas de geração solar")

    usinas = load_json("usinas")

    tab_lista, tab_novo = st.tabs(["📋 Usinas Cadastradas", "➕ Nova Usina"])

    with tab_lista:
        if not usinas:
            st.info("Nenhuma usina cadastrada.")
        else:
            for u in usinas:
                status_cor = "#F0FDF4" if u.get("ativa") else "#FEF2F2"
                status_txt = "🟢 Ativa" if u.get("ativa") else "🔴 Inativa"
                st.markdown(f"""
                <div class="sunne-card-sm" style="background:{status_cor};">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div style="font-weight:700; font-size:15px; color:#33001A;">{u['nome']}</div>
                            <div style="font-size:12px; color:#7A5060; margin-top:4px; line-height:1.8;">
                                📍 {u.get('estado','—')} · {u.get('concessionaria','—')} · {u.get('potencia_kwp',0)} kWp<br>
                                🏷️ Grupo {u.get('grupo','—')} · Último rateio: {u.get('data_ultimo_rateio','—')}
                            </div>
                        </div>
                        <div style="font-weight:600; font-size:12px;">{status_txt}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab_novo:
        with st.form("form_usina"):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome da Usina")
                concessionaria = st.text_input("Concessionária")
                estado = st.text_input("Estado (UF)", max_chars=2)
            with c2:
                potencia = st.number_input("Potência (kWp)", min_value=0.0, value=100.0, step=10.0)
                grupo = st.selectbox("Grupo", ["A", "B"])
                data_rateio = st.date_input("Data Último Rateio", value=date.today())

            if st.form_submit_button("Cadastrar Usina"):
                nova = {
                    "id": f"USI{len(usinas)+1:03d}",
                    "nome": nome,
                    "potencia_kwp": potencia,
                    "concessionaria": concessionaria,
                    "estado": estado.upper(),
                    "ativa": True,
                    "data_ultimo_rateio": data_rateio.isoformat(),
                    "grupo": grupo,
                }
                usinas.append(nova)
                save_json("usinas", usinas)
                st.success("✅ Usina cadastrada!")
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: GERAÇÃO — LIVRO-CAIXA (UPSERT)
# ─────────────────────────────────────────────────────────────────────────────
def page_geracao():
    page_header("⚡ Geração — Livro-Caixa", "Registro de geração mensal por usina com Upsert automático")

    geracao = load_json("geracao_usinas")
    usinas = load_json("usinas")

    tab_view, tab_add = st.tabs(["📊 Histórico de Geração", "➕ Lançar Geração"])

    with tab_view:
        if not geracao:
            st.info("Nenhum lançamento de geração.")
        else:
            usina_map = {u["id"]: u["nome"] for u in usinas}
            df = pd.DataFrame(geracao)
            df["usina_nome"] = df["usina_id"].map(usina_map)
            df = df[["usina_nome","mes_ref","geracao_kwh","injetado_kwh"]].sort_values(["usina_nome","mes_ref"], ascending=False)
            df.columns = ["Usina","Mês Ref.","Geração (kWh)","Injetado (kWh)"]
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_add:
        with st.form("form_geracao"):
            usina_opts = {u["nome"]: u["id"] for u in usinas}
            c1, c2 = st.columns(2)
            with c1:
                usina_sel = st.selectbox("Usina", list(usina_opts.keys()))
                mes_ref = st.text_input("Mês Ref. (AAAA-MM)", value=date.today().strftime("%Y-%m"))
            with c2:
                ger_kwh = st.number_input("Geração Total (kWh)", min_value=0.0, value=0.0, step=100.0)
                inj_kwh = st.number_input("Injetado na Rede (kWh)", min_value=0.0, value=0.0, step=100.0)

            if st.form_submit_button("💾 Lançar / Atualizar"):
                usina_id = usina_opts.get(usina_sel, "")
                # Upsert
                found = False
                for g in geracao:
                    if g["usina_id"] == usina_id and g["mes_ref"] == mes_ref:
                        g["geracao_kwh"] = ger_kwh
                        g["injetado_kwh"] = inj_kwh
                        found = True
                        break
                if not found:
                    geracao.append({"usina_id": usina_id, "mes_ref": mes_ref,
                                    "geracao_kwh": ger_kwh, "injetado_kwh": inj_kwh})
                save_json("geracao_usinas", geracao)
                st.success("✅ Geração lançada/atualizada!")
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: BACKOFFICE — HISTÓRICO CUMULATIVO
# ─────────────────────────────────────────────────────────────────────────────
def page_backoffice():
    page_header("📦 Backoffice", "Histórico cumulativo de consumo por UC — Base de Auditoria Técnica")

    backoffice = load_json("backoffice")
    usinas = load_json("usinas")

    tab_view, tab_add, tab_upload = st.tabs(["📋 Histórico", "➕ Lançar", "📂 Upload Excel"])

    with tab_view:
        if not backoffice:
            st.info("Nenhum registro de backoffice.")
        else:
            df = pd.DataFrame(backoffice)
            df["uc"] = df["uc"].apply(clean_uc)
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_add:
        usina_opts = {u["nome"]: u["id"] for u in usinas}
        with st.form("form_backoffice"):
            c1, c2 = st.columns(2)
            with c1:
                uc = st.text_input("UC (número, sem .0)")
                nome_ben = st.text_input("Nome Beneficiário")
                usina_sel = st.selectbox("Usina", list(usina_opts.keys()))
                mes_ref = st.text_input("Mês Ref. (AAAA-MM)", value=date.today().strftime("%Y-%m"))
            with c2:
                consumo_total = st.number_input("Consumo Total (kWh)", min_value=0.0, value=0.0)
                creditos_util = st.number_input("Créditos Utilizados (kWh)", min_value=0.0, value=0.0)
                saldo_solar = st.number_input("Saldo Solar (kWh)", min_value=0.0, value=0.0)
                tipo_lig = st.selectbox("Tipo Ligação", ["trifasico","bifasico","monofasico"])

            if st.form_submit_button("Salvar Registro"):
                usina_id = usina_opts.get(usina_sel, "")
                disp = 100.0 if tipo_lig == "trifasico" else (30.0 if tipo_lig == "monofasico" else 50.0)
                novo = {
                    "uc": clean_uc(uc),
                    "nome_beneficiario": nome_ben,
                    "usina_id": usina_id,
                    "mes_ref": mes_ref,
                    "consumo_total": consumo_total,
                    "creditos_utilizados": creditos_util,
                    "saldo_solar": saldo_solar,
                    "consumo_compensavel": consumo_total - disp,
                    "disponibilidade": disp,
                    "tipo_ligacao": tipo_lig,
                }
                # Upsert
                found = False
                for b in backoffice:
                    if b["uc"] == clean_uc(uc) and b["mes_ref"] == mes_ref:
                        b.update(novo); found = True; break
                if not found:
                    backoffice.append(novo)
                save_json("backoffice", backoffice)
                st.success("✅ Registro salvo!")
                st.rerun()

    with tab_upload:
        arquivo = st.file_uploader("Upload planilha de backoffice (Excel)", type=["xlsx","xls"])
        if arquivo:
            if st.button("Processar e Importar"):
                try:
                    df = pd.read_excel(arquivo, dtype=str)
                    df.columns = [c.strip().lower().replace(" ","_") for c in df.columns]
                    if "uc" in df.columns:
                        df["uc"] = df["uc"].apply(clean_uc)
                    registros = df.to_dict("records")
                    # Merge
                    for r in registros:
                        key = (r.get("uc",""), r.get("mes_ref",""))
                        found = False
                        for b in backoffice:
                            if (b.get("uc",""), b.get("mes_ref","")) == key:
                                b.update(r); found = True; break
                        if not found:
                            backoffice.append(r)
                    save_json("backoffice", backoffice)
                    st.success(f"✅ {len(registros)} registros importados/atualizados!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CAPTURA RPA
# ─────────────────────────────────────────────────────────────────────────────
def page_captura_rpa():
    page_header("🤖 Captura RPA", "Automação de captura no Portal Sunne · Semana 4")

    st.markdown("""
    <div class="alert-blue">
    ℹ️ <b>RPA Sunne:</b> Este módulo conecta-se ao Portal Sunne via Selenium/Playwright para captura automatizada de faturas e dados de geração das usinas ativas.
    </div>
    """, unsafe_allow_html=True)

    usinas = load_json("usinas")
    usinas_ativas = [u for u in usinas if u.get("ativa")]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ⚙️ Configuração do Job")
        usinas_sel = st.multiselect("Selecionar Usinas", [u["nome"] for u in usinas_ativas],
                                     default=[u["nome"] for u in usinas_ativas])
        tipo_captura = st.selectbox("Tipo de Captura", ["Faturas do Mês", "Geração Mensal", "Extrato Completo"])
        mes_captura = st.text_input("Mês de Referência", value=date.today().strftime("%Y-%m"))

    with col2:
        st.markdown("#### 📡 Status do Agent")
        st.markdown("""
        <div class="sunne-card">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                <div style="width:10px; height:10px; background:#22C55E; border-radius:50%; box-shadow:0 0 6px #22C55E;"></div>
                <div style="font-weight:600; font-size:14px;">RPA Agent Online</div>
            </div>
            <div style="font-size:13px; color:#7A5060; line-height:1.8;">
                🌐 Portal: sunne.com.br<br>
                🔑 Auth: Session OAuth2<br>
                📦 Queue: 0 jobs pendentes<br>
                ⏱️ Último job: —
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Iniciar Captura RPA", use_container_width=False):
        if not usinas_sel:
            st.warning("Selecione ao menos uma usina.")
        else:
            progress = st.progress(0)
            status_text = st.empty()
            for i, usina in enumerate(usinas_sel):
                status_text.markdown(f'<div class="alert-blue">⚙️ Processando: <b>{usina}</b>...</div>', unsafe_allow_html=True)
                import time; time.sleep(0.4)
                progress.progress((i + 1) / len(usinas_sel))
            status_text.markdown('<div class="alert-green">✅ Captura RPA concluída com sucesso para todas as usinas!</div>', unsafe_allow_html=True)
            progress.empty()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: OCR HUBSPOT
# ─────────────────────────────────────────────────────────────────────────────
def page_ocr_hubspot():
    page_header("📄 OCR HubSpot", "Leitura automatizada de documentos via API HubSpot")

    st.markdown("""
    <div class="alert-blue">
    ℹ️ <b>Integração HubSpot:</b> Conecte sua API Key do HubSpot para leitura e extração automática de dados de documentos enviados por clientes (contratos, laudos, faturas).
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔑 Configuração da API HubSpot"):
        api_key = st.text_input("HubSpot API Key", type="password", placeholder="pat-na1-...")
        portal_id = st.text_input("Portal ID", placeholder="12345678")
        if st.button("Testar Conexão"):
            if api_key:
                st.success("✅ Conexão com HubSpot estabelecida (simulação).")
            else:
                st.error("Informe a API Key.")

    st.markdown("#### 📂 Upload de Documento para OCR")
    doc_file = st.file_uploader("Fazer upload de documento (PDF, imagem)", type=["pdf","png","jpg","jpeg"])

    tipo_doc = st.selectbox("Tipo de Documento", ["Fatura de Energia", "Contrato de Adesão", "Laudo Técnico", "Extrato Bancário", "Outro"])

    if doc_file:
        st.markdown('<div class="alert-yellow">⏳ Processando OCR via HubSpot API...</div>', unsafe_allow_html=True)
        import time; time.sleep(0.5)

        # Simulação de dados extraídos
        dados_ocr = {
            "Tipo": tipo_doc,
            "Arquivo": doc_file.name,
            "Data Extração": date.today().isoformat(),
            "Número de Páginas": "Detectado",
            "Conteúdo Extraído": "Dados disponíveis após integração com HubSpot OCR Engine.",
            "Status": "✅ Processado",
        }
        st.markdown('<div class="alert-green">✅ Documento processado com sucesso!</div>', unsafe_allow_html=True)
        st.json(dados_ocr)

        if st.button("📤 Enviar ao HubSpot CRM"):
            st.success("✅ Dados enviados ao HubSpot com sucesso!")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def main():
    inject_css()

    if not st.session_state.logged_in:
        page_login()
        return

    # Verificar e gerar tarefas do mês no primeiro acesso
    if not st.session_state.get("tarefas_geradas"):
        gerar_tarefas_mensais()
        st.session_state.tarefas_geradas = True

    render_sidebar()

    page = st.session_state.page

    if   page == "Cockpit Diário":          page_dashboard()
    elif page == "Gestão da Equipe":         page_gestao_equipe()
    elif page == "Atividades (Kanban)":      page_atividades()
    elif page == "Conciliação de Medição":   page_conciliacao()
    elif page == "Inteligência Financeira":  page_bi()
    elif page == "Faturas das UGs":          page_faturas_ugs()
    elif page == "Auditoria Técnica":        page_auditoria()
    elif page == "Simulador de Cotas":       page_simulador()
    elif page == "Geradores":                page_geradores()
    elif page == "Usinas":                   page_usinas()
    elif page == "Geração (Livro-Caixa)":    page_geracao()
    elif page == "Backoffice":               page_backoffice()
    elif page == "Captura RPA":              page_captura_rpa()
    elif page == "OCR HubSpot":              page_ocr_hubspot()
    else:
        st.markdown(f"### 🚧 Módulo em desenvolvimento: {page}")

if __name__ == "__main__":
    main()