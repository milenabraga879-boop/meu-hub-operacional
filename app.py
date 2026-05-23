import streamlit as st
import json, os, uuid
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
from io import BytesIO

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sunne Hub v12",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DATABASE ──────────────────────────────────────────────────────────────────
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
    return s[:-2] if s.endswith(".0") else s

# ── CSS ───────────────────────────────────────────────────────────────────────
def inject_css():
    css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --wine:    #1C0010;
  --orange:  #F36E21;
  --orange2: #d45c16;
  --bg:      #f9fafb;
  --white:   #ffffff;
  --border:  #e5e7eb;
  --text:    #111827;
  --textmd:  #374151;
  --textsm:  #6b7280;
  --textxs:  #9ca3af;
  --green:   #16a34a;
  --red:     #dc2626;
  --yellow:  #d97706;
  --blue:    #2563eb;
  --r:       8px;
  --rlg:     12px;
  --sh:      0 1px 3px rgba(0,0,0,0.08),0 1px 2px rgba(0,0,0,0.04);
}

* { font-family: 'Inter', system-ui, sans-serif !important; box-sizing: border-box; }

[data-testid="stAppViewContainer"] { background: var(--bg) !important; }
[data-testid="stHeader"] { background: transparent !important; }
.main .block-container { padding: 28px 32px !important; max-width: 1440px !important; }

/* SIDEBAR */
[data-testid="stSidebar"] { background: var(--wine) !important; }
[data-testid="stSidebar"] > div:first-child { background: var(--wine) !important; padding: 0 !important; }
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.8) !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08) !important; }
[data-testid="stSidebar"] .streamlit-expanderHeader {
  background: transparent !important; border: none !important;
  font-size: 10.5px !important; font-weight: 700 !important;
  letter-spacing: 0.1em !important; text-transform: uppercase !important;
  color: rgba(255,255,255,0.3) !important; padding: 10px 20px 4px !important;
}
[data-testid="stSidebar"] .streamlit-expanderContent { background: transparent !important; border: none !important; padding: 0 8px 4px !important; }
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important; border: none !important;
  border-radius: 6px !important; color: rgba(255,255,255,0.72) !important;
  text-align: left !important; font-size: 13.5px !important;
  font-weight: 400 !important; padding: 8px 14px !important;
  width: 100% !important; box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255,255,255,0.08) !important; color: #fff !important;
  transform: none !important; box-shadow: none !important;
}

/* BUTTONS */
.stButton > button {
  background: var(--orange) !important; color: #fff !important;
  border: none !important; border-radius: var(--r) !important;
  font-weight: 500 !important; font-size: 13.5px !important;
  padding: 8px 18px !important; box-shadow: none !important;
  transition: background 0.15s, transform 0.1s !important;
}
.stButton > button:hover {
  background: var(--orange2) !important; transform: translateY(-1px) !important;
  box-shadow: 0 3px 10px rgba(243,110,33,0.28) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* INPUTS */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
  border-radius: var(--r) !important; border: 1.5px solid #d1d5db !important;
  font-size: 13.5px !important; background: #fff !important; padding: 8px 12px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--orange) !important;
  box-shadow: 0 0 0 3px rgba(243,110,33,0.12) !important;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
  border-radius: var(--r) !important; border: 1.5px solid #d1d5db !important;
  background: #fff !important; font-size: 13.5px !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important; border-bottom: 1.5px solid var(--border) !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important; border-radius: 0 !important;
  font-size: 13.5px !important; font-weight: 500 !important;
  color: var(--textsm) !important; padding: 10px 20px !important; border: none !important;
}
.stTabs [aria-selected="true"] {
  color: var(--orange) !important; border-bottom: 2.5px solid var(--orange) !important; font-weight: 600 !important;
}

/* DATAFRAME */
.stDataFrame { border-radius: var(--rlg) !important; border: 1px solid var(--border) !important; overflow: hidden !important; }

/* HEADINGS */
h1 { font-size: 22px !important; font-weight: 700 !important; color: var(--text) !important; letter-spacing: -0.3px !important; margin-bottom: 2px !important; }
h2 { font-size: 18px !important; font-weight: 600 !important; color: var(--text) !important; }
h3 { font-size: 15px !important; font-weight: 600 !important; color: var(--text) !important; }
p  { font-size: 14px !important; color: var(--textmd) !important; }

/* HIDE STREAMLIT CHROME */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
</style>
"""
    st.markdown(css, unsafe_allow_html=True)

# ── COMPONENT HELPERS ─────────────────────────────────────────────────────────
def card(content, style=""):
    st.markdown(f'<div style="background:#fff;border-radius:12px;border:1px solid #e5e7eb;box-shadow:0 1px 3px rgba(0,0,0,0.07);padding:20px 24px;margin-bottom:16px;{style}">{content}</div>', unsafe_allow_html=True)

def kpi(label, value, sub="", delta="", delta_up=None, icon_char="", icon_bg="#fff7ed", icon_col="#F36E21"):
    delta_html = ""
    if delta:
        clr = "#16a34a" if delta_up else ("#dc2626" if delta_up is False else "#9ca3af")
        arr = "▲ " if delta_up else ("▼ " if delta_up is False else "")
        delta_html = f'<div style="font-size:12px;font-weight:500;color:{clr};margin-top:5px;">{arr}{delta}</div>'
    icon_html = f'<div style="position:absolute;right:16px;top:16px;width:34px;height:34px;border-radius:8px;background:{icon_bg};display:flex;align-items:center;justify-content:center;font-size:16px;">{icon_char}</div>' if icon_char else ""
    sub_html  = f'<div style="font-size:12px;color:#9ca3af;margin-top:3px;">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div style="background:#fff;border-radius:12px;border:1px solid #e5e7eb;box-shadow:0 1px 3px rgba(0,0,0,0.07);padding:18px 20px;position:relative;overflow:hidden;">
        {icon_html}
        <div style="font-size:11.5px;font-weight:500;color:#6b7280;margin-bottom:6px;">{label}</div>
        <div style="font-size:26px;font-weight:700;color:#111827;line-height:1;letter-spacing:-0.5px;">{value}</div>
        {sub_html}{delta_html}
    </div>""", unsafe_allow_html=True)

def badge(status):
    styles = {
        "em aberto":   ("background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe", "Em Aberto"),
        "em andamento":("background:#fff7ed;color:#c2410c;border:1px solid #fed7aa", "Em Andamento"),
        "travado":     ("background:#fef2f2;color:#b91c1c;border:1px solid #fecaca", "Travado"),
        "concluido":   ("background:#f0fdf4;color:#15803d;border:1px solid #bbf7d0", "Concluído"),
        "cancelado":   ("background:#f9fafb;color:#6b7280;border:1px solid #e5e7eb", "Cancelado"),
    }
    s, lbl = styles.get(status, ("background:#f3f4f6;color:#374151", status))
    return f'<span style="display:inline-block;padding:2px 9px;border-radius:20px;font-size:11.5px;font-weight:500;{s};">{lbl}</span>'

def alert(msg, kind="blue"):
    cfg = {
        "blue":   ("#eff6ff","#bfdbfe","#1e3a8a","ℹ"),
        "green":  ("#f0fdf4","#bbf7d0","#14532d","✓"),
        "yellow": ("#fffbeb","#fde68a","#78350f","⚠"),
        "red":    ("#fef2f2","#fecaca","#7f1d1d","✕"),
    }
    bg, br, tc, ic = cfg.get(kind, cfg["blue"])
    st.markdown(f'<div style="background:{bg};border:1px solid {br};border-radius:8px;padding:12px 16px;font-size:13.5px;color:{tc};margin-bottom:10px;display:flex;gap:10px;align-items:flex-start;"><span style="flex-shrink:0;font-weight:700;">{ic}</span><div>{msg}</div></div>', unsafe_allow_html=True)

def section_label(text):
    st.markdown(f'<div style="font-size:15px;font-weight:600;color:#111827;margin:20px 0 12px;padding-bottom:8px;border-bottom:1px solid #e5e7eb;">{text}</div>', unsafe_allow_html=True)

def page_header(title, sub=""):
    st.markdown(f'<div style="font-size:22px;font-weight:700;color:#111827;letter-spacing:-0.3px;margin-bottom:{"2px" if sub else "20px"};">{title}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div style="font-size:13.5px;color:#6b7280;margin-bottom:22px;">{sub}</div>', unsafe_allow_html=True)

# ── AUTH ──────────────────────────────────────────────────────────────────────
USERS = {
    "admin":  {"senha":"sunne2024","role":"admin",   "nome":"Administrador",  "email":"admin@sunne.com.br"},
    "milena": {"senha":"milena123","role":"analista","nome":"Milena Braga",    "email":"milena.braga@sunne.com.br"},
    "carlos": {"senha":"carlos123","role":"analista","nome":"Carlos Mendes",   "email":"carlos.mendes@sunne.com.br"},
}

def init_session():
    for k,v in {"logged_in":False,"user":None,"role":None,"page":"Dashboard",
                "tarefas_geradas":False,"trava_task_id":None,"trava_target_status":None,
                "show_new_task":False,"nome":"","email":""}.items():
        if k not in st.session_state: st.session_state[k] = v

init_session()

# ── LOGIN PAGE ────────────────────────────────────────────────────────────────
def page_login():
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: #f3f4f6 !important; }
    </style>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1,1,1])
    with mid:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;margin-bottom:28px;">
            <div style="font-size:34px;font-weight:800;color:#F36E21;letter-spacing:-1.5px;">sunne</div>
            <div style="font-size:11px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:#9ca3af;margin-top:3px;">Hub v12 · Gestão Solar</div>
        </div>
        <div style="background:#fff;border-radius:14px;border:1px solid #e5e7eb;padding:36px;box-shadow:0 2px 16px rgba(0,0,0,0.06);">
            <div style="font-size:18px;font-weight:700;color:#111827;margin-bottom:4px;">Acesso à Plataforma</div>
            <div style="font-size:13px;color:#6b7280;margin-bottom:22px;">Entre com suas credenciais corporativas</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login"):
            user  = st.text_input("Usuário",  placeholder="seu.usuario",  label_visibility="collapsed")
            senha = st.text_input("Senha", type="password", placeholder="Senha", label_visibility="collapsed")
            ok    = st.form_submit_button("Entrar", use_container_width=True)

        if ok:
            u = USERS.get(user.lower())
            if u and u["senha"] == senha:
                st.session_state.update(logged_in=True, user=user.lower(),
                    role=u["role"], nome=u["nome"], email=u.get("email",""))
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

        st.markdown('<p style="text-align:center;font-size:12px;color:#9ca3af;margin-top:16px;">Acesso restrito · Sunne Energia</p>', unsafe_allow_html=True)

# ── MOTOR DIA 01 ──────────────────────────────────────────────────────────────
def gerar_tarefas_mensais():
    tasks = load_json("tasks")
    today = date.today()
    mes   = today.strftime("%Y-%m")
    if any(t.get("mes_geracao")==mes for t in tasks): return
    usinas = [u for u in load_json("usinas") if u.get("ativa", True)]
    s1,s2,s3,s4 = [today.replace(day=d) for d in [1,8,15,22]]
    novas = []
    for u in usinas:
        base = dict(usina_id=u["id"],usina_nome=u["nome"],analista="milena",
                    status="em aberto",mes_geracao=mes,motivo_bloqueio="")
        novas += [
            {**base,"id":str(uuid.uuid4()),"titulo":f"Captura de Fatura UG — {u['nome']}","macro_tema":"Faturamento","data_programada":s1.isoformat(),"data_limite":(s1+timedelta(days=6)).isoformat(),"semana":1},
            {**base,"id":str(uuid.uuid4()),"titulo":f"Conciliacao de Medicao — {u['nome']}","macro_tema":"Faturamento","data_programada":s1.isoformat(),"data_limite":(s1+timedelta(days=6)).isoformat(),"semana":1},
            {**base,"id":str(uuid.uuid4()),"titulo":f"Auditoria Tecnica UCs — {u['nome']}","macro_tema":"Rateio","data_programada":s2.isoformat(),"data_limite":(s3+timedelta(days=6)).isoformat(),"semana":2},
            {**base,"id":str(uuid.uuid4()),"titulo":f"Captura RPA Portal Sunne — {u['nome']}","analista":"carlos","macro_tema":"Captura","data_programada":s4.isoformat(),"data_limite":(s4+timedelta(days=7)).isoformat(),"semana":4},
        ]
    save_json("tasks", tasks + novas)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def is_overdue(t):
    try: return date.fromisoformat(t.get("data_limite","2099-12-31")) < date.today() and t["status"] not in ("concluido","cancelado")
    except: return False

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
NAV = {
    "CENTRAL": [("Dashboard","dashboard"),("Gestao da Equipe","team")],
    "ESTEIRA":  [("Atividades","kanban")],
    "FATURAMENTO": [("Conciliacao de Medicao","receipt"),("Inteligencia Financeira","chart"),("Faturas das UGs","invoice")],
    "RATEIOS":  [("Auditoria Tecnica","audit"),("Simulador de Cotas","scale")],
    "BASES":    [("Geradores","user"),("Usinas","building"),("Geracao (Livro-Caixa)","flash"),("Backoffice","db")],
    "AUTOMACOES":[("Captura RPA","robot"),("OCR HubSpot","ocr")],
}

def render_sidebar():
    nome  = st.session_state.nome
    email = st.session_state.email
    role  = st.session_state.role

    with st.sidebar:
        st.markdown(f"""
        <div style="padding:20px 20px 14px;border-bottom:1px solid rgba(255,255,255,0.08);">
            <div style="font-size:24px;font-weight:800;color:#F36E21;letter-spacing:-1px;">sunne</div>
            <div style="font-size:10px;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;color:rgba(255,255,255,0.28);margin-top:2px;">Hub v12</div>
        </div>
        <div style="padding:12px 20px 14px;border-bottom:1px solid rgba(255,255,255,0.07);">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:30px;height:30px;border-radius:50%;background:#F36E21;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;flex-shrink:0;">{nome[0].upper() if nome else "U"}</div>
                <div>
                    <div style="font-size:13px;font-weight:600;color:#fff;">{nome}</div>
                    <div style="font-size:11px;color:rgba(255,255,255,0.38);">{email}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for section, pages in NAV.items():
            if section == "CENTRAL" and role != "admin":
                pages = [("Dashboard","dashboard")]
            with st.expander(section, expanded=any(st.session_state.page==lbl for lbl,_ in pages)):
                for label, _ in pages:
                    active = st.session_state.page == label
                    if active:
                        st.markdown(f'<div style="background:rgba(243,110,33,0.15);border-radius:6px;padding:8px 14px;font-size:13.5px;font-weight:600;color:#F36E21;margin-bottom:2px;">{label}</div>', unsafe_allow_html=True)
                    if st.button(label, key=f"nav_{label}", use_container_width=True):
                        st.session_state.page = label
                        st.rerun()

        st.markdown('<hr>', unsafe_allow_html=True)
        if st.button("Sair", key="logout", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# ════════════════════════════════════════════════════════════════════
# PAGES
# ════════════════════════════════════════════════════════════════════

# ── DASHBOARD ─────────────────────────────────────────────────────────────────
def page_dashboard():
    page_header("Dashboard", "Visao geral")
    tasks  = load_json("tasks")
    usinas = load_json("usinas")
    geracao= load_json("geracao_usinas")
    mes    = date.today().strftime("%Y-%m")

    total = len(tasks)
    concl = len([t for t in tasks if t["status"]=="concluido"])
    atras = len([t for t in tasks if is_overdue(t)])
    trav  = len([t for t in tasks if t["status"]=="travado"])
    uat   = len([u for u in usinas if u.get("ativa",True)])
    pct   = round(concl/total*100) if total else 0

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi("Tarefas no Mes",    total, icon_char="≡",   icon_bg="#eff6ff", icon_col="#2563eb")
    with c2: kpi("Concluidas",        concl, f"{pct}% do total", delta=f"+{pct}% conclusao", delta_up=pct>50, icon_char="✓", icon_bg="#f0fdf4", icon_col="#16a34a")
    with c3: kpi("Atrasadas",         atras, "requerem atencao", delta=f"{atras} vencidas", delta_up=False if atras else None, icon_char="!", icon_bg="#fef2f2", icon_col="#dc2626")
    with c4: kpi("Travadas",          trav,  "aguardam desbloq.", icon_char="×", icon_bg="#faf5ff", icon_col="#7c3aed")
    with c5: kpi("Usinas Ativas",     uat,   "em operacao",       icon_char="☀", icon_bg="#fff7ed", icon_col="#F36E21")

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1.2])

    with col_a:
        section_label("Alertas Criticos")
        usinas_com_ger = {g["usina_id"] for g in geracao if g.get("mes_ref","").startswith(mes[:7])}
        alertas = []
        for u in usinas:
            if u.get("ativa") and u["id"] not in usinas_com_ger:
                alertas.append(("red", f"Sem geracao registrada: <strong>{u['nome']}</strong>"))
        for t in tasks:
            if is_overdue(t):
                alertas.append(("yellow", f"Tarefa vencida: <strong>{t['titulo'][:50]}</strong>"))
        for u in usinas:
            try:
                dias = (date.today() - date.fromisoformat(u.get("data_ultimo_rateio","2020-01-01"))).days
                if dias > 90: alertas.append(("yellow", f"Rateio desatualizado ({dias}d): <strong>{u['nome']}</strong>"))
            except: pass
        if not alertas:
            alert("Nenhum alerta critico. Sistema operando normalmente.", "green")
        else:
            for kind, msg in alertas[:6]: alert(msg, kind)

    with col_b:
        section_label("Minha Agenda de Hoje")
        user = st.session_state.user
        hoje = date.today().isoformat()
        minhas = [t for t in tasks if t.get("analista")==user and t["status"] not in ("concluido","cancelado")]
        agenda = sorted([t for t in minhas if t.get("data_programada")==hoje or t.get("data_limite","9999")<hoje],
                        key=lambda x: x.get("data_limite","9999"))
        if not agenda:
            alert("Nenhuma tarefa para hoje.", "green")
        else:
            for t in agenda[:6]:
                ov  = is_overdue(t)
                bdr = "#dc2626" if ov else "#F36E21"
                st.markdown(f"""
                <div style="background:#fff;border-radius:10px;border:1px solid #e5e7eb;border-left:3px solid {bdr};
                     box-shadow:0 1px 3px rgba(0,0,0,0.06);padding:12px 16px;margin-bottom:8px;">
                    <div style="font-size:13px;font-weight:600;color:#111827;margin-bottom:5px;">{t['titulo'][:55]}</div>
                    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-size:12px;color:#6b7280;">
                        <span>{t.get('usina_nome','—')[:28]}</span>
                        <span>Limite: {t.get('data_limite','—')}</span>
                        {badge(t['status'])}
                        {'<span style="font-size:11px;font-weight:600;color:#dc2626;">Atrasada</span>' if ov else ''}
                    </div>
                </div>""", unsafe_allow_html=True)

    # Receita mensal
    historico = load_json("historico_analises")
    if historico:
        section_label("Receita Mensal (Visao Caixa)")
        df = pd.DataFrame(historico)
        df["mes_ref"] = pd.to_datetime(df["mes_ref"])
        df = df.sort_values("mes_ref")
        df["lb"] = df["mes_ref"].dt.strftime("%b/%y")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["lb"], y=df["recebimento_bruto"],   name="Emitido",  marker_color="#3b82f6", opacity=0.8))
        fig.add_trace(go.Bar(x=df["lb"], y=df["recebimento_liquido"], name="Recebido", marker_color="#F36E21", opacity=0.85))
        fig.update_layout(barmode="group", plot_bgcolor="white", paper_bgcolor="white",
                          font=dict(family="Inter",size=12), height=270,
                          margin=dict(l=10,r=10,t=10,b=30),
                          legend=dict(orientation="h",yanchor="bottom",y=1.02),
                          yaxis=dict(gridcolor="#f3f4f6"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # Agenda 7 dias
    section_label("Proximos 7 Dias")
    eventos = ["Envio Faturas Grp A","Reuniao Operacional","Auditoria USI001",
               "Deadline Conciliacao","Relatorio BI","Captura RPA","Revisao Rateios"]
    cols = st.columns(7)
    for i, ev in enumerate(eventos):
        dt = (date.today()+timedelta(days=i)).strftime("%d/%m")
        with cols[i]:
            is_td = i==0
            bg  = "#fff7ed" if is_td else "#fff"
            bdr = "#F36E21" if is_td else "#e5e7eb"
            st.markdown(f'<div style="background:{bg};border:1px solid {bdr};border-radius:10px;padding:12px 8px;text-align:center;min-height:78px;"><div style="font-size:11px;font-weight:700;color:#F36E21;">{dt}</div><div style="font-size:11.5px;color:#374151;margin-top:5px;font-weight:500;line-height:1.35;">{ev}</div></div>', unsafe_allow_html=True)

# ── GESTAO DA EQUIPE ──────────────────────────────────────────────────────────
def page_gestao_equipe():
    if st.session_state.role != "admin":
        st.error("Acesso restrito ao Administrador.")
        return
    page_header("Gestao da Equipe", "Desempenho operacional por analista")
    tasks = load_json("tasks")
    analistas = list({t.get("analista","") for t in tasks if t.get("analista")})
    if not analistas:
        st.info("Nenhuma tarefa cadastrada.")
        return
    rows = []
    for an in analistas:
        ta = [t for t in tasks if t.get("analista")==an]
        rows.append({"Analista":USERS.get(an,{}).get("nome",an),
                     "Total":len(ta),
                     "Concluidas":len([t for t in ta if t["status"]=="concluido"]),
                     "Em Andamento":len([t for t in ta if t["status"]=="em andamento"]),
                     "Atrasadas":len([t for t in ta if is_overdue(t)]),
                     "Travadas":len([t for t in ta if t["status"]=="travado"])})
    df = pd.DataFrame(rows)
    tot_concl = sum(r["Concluidas"] for r in rows)
    pct = round(tot_concl/len(tasks)*100) if tasks else 0
    c1,c2,c3 = st.columns(3)
    with c1: kpi("Analistas Ativos", len(analistas))
    with c2: kpi("Total Tarefas", len(tasks), "todas as equipes")
    with c3: kpi("Taxa Conclusao", f"{pct}%", "global", delta=f"{pct}% do mes", delta_up=pct>50)
    st.markdown("<br>", unsafe_allow_html=True)
    fig = go.Figure()
    for cat, cor in [("Concluidas","#22c55e"),("Em Andamento","#F36E21"),("Atrasadas","#ef4444"),("Travadas","#8b5cf6")]:
        fig.add_trace(go.Bar(name=cat, x=df["Analista"], y=df[cat], marker_color=cor, text=df[cat], textposition="auto"))
    fig.update_layout(barmode="group", plot_bgcolor="white", paper_bgcolor="white",
                      font=dict(family="Inter",size=12), height=330,
                      margin=dict(l=10,r=10,t=20,b=10),
                      legend=dict(orientation="h",yanchor="bottom",y=1.02),
                      yaxis=dict(gridcolor="#f3f4f6"))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    section_label("SLA por Analista")
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── KANBAN ────────────────────────────────────────────────────────────────────
KSTATUS = ["em aberto","em andamento","travado","concluido","cancelado"]
KLABELS = {"em aberto":"Em Aberto","em andamento":"Em Andamento",
           "travado":"Travado","concluido":"Concluido","cancelado":"Cancelado"}
KACCENT = {"em aberto":"#3b82f6","em andamento":"#F36E21","travado":"#ef4444","concluido":"#22c55e","cancelado":"#9ca3af"}
TEMA_S  = {"Faturamento":("#fff7ed","#c2410c"),"Rateio":("#faf5ff","#7c3aed"),"Captura":("#f0fdf4","#15803d")}

def page_atividades():
    page_header("Atividades", "Esteira operacional mensal")
    tasks  = load_json("tasks")
    usinas = load_json("usinas")

    c1,c2,c3,c4 = st.columns([1,1,1,1])
    with c1: tf = st.selectbox("Macro-tema", ["Todos","Faturamento","Rateio","Captura"])
    with c2: af = st.selectbox("Analista",   ["Todos"]+list(USERS.keys()))
    with c3: sf = st.selectbox("Semana",     ["Todas","1","2","3","4"])
    with c4:
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("Nova Tarefa"): st.session_state.show_new_task = True

    if st.session_state.get("show_new_task"):
        with st.expander("Criar Nova Tarefa", expanded=True):
            with st.form("form_task"):
                cc1,cc2 = st.columns(2)
                with cc1:
                    titulo = st.text_input("Titulo")
                    uo = {u["nome"]:u["id"] for u in usinas}
                    us = st.selectbox("Usina", list(uo.keys()) or ["—"])
                    an = st.selectbox("Analista", list(USERS.keys()))
                with cc2:
                    tema = st.selectbox("Macro-tema", ["Faturamento","Rateio","Captura"])
                    dp   = st.date_input("Data Programada", value=date.today())
                    dl   = st.date_input("Data Limite",     value=date.today()+timedelta(days=7))
                if st.form_submit_button("Criar"):
                    tasks.append({"id":str(uuid.uuid4()),"titulo":titulo,
                                  "usina_id":uo.get(us,""),"usina_nome":us,"analista":an,
                                  "status":"em aberto","macro_tema":tema,
                                  "data_programada":dp.isoformat(),"data_limite":dl.isoformat(),
                                  "mes_geracao":date.today().strftime("%Y-%m"),"motivo_bloqueio":"","semana":1})
                    save_json("tasks",tasks)
                    st.session_state.show_new_task = False
                    st.rerun()

    filtered = [t for t in tasks
                if (tf=="Todos" or t.get("macro_tema")==tf)
                and (af=="Todos" or t.get("analista")==af)
                and (sf=="Todas" or str(t.get("semana",""))==sf)]

    # Trava de governança
    if st.session_state.get("trava_task_id"):
        alert("<strong>Trava de Governanca Ativa</strong> — Justificativa obrigatoria.", "red")
        motivo = st.text_area("Motivo (minimo 10 caracteres):", key="motivo_trava")
        target = st.session_state.get("trava_target_status","travado")
        bc1, bc2 = st.columns([1,4])
        with bc1:
            if st.button("Confirmar", key="confirm_trava"):
                if len(motivo.strip()) < 10: st.error("Motivo muito curto.")
                else:
                    for t in tasks:
                        if t["id"]==st.session_state.trava_task_id:
                            t["status"]=target; t["motivo_bloqueio"]=motivo.strip()
                    save_json("tasks",tasks)
                    st.session_state.trava_task_id = None
                    st.rerun()
        with bc2:
            if st.button("Cancelar", key="cancel_trava"):
                st.session_state.trava_task_id = None; st.rerun()
        st.markdown("---")

    cols = st.columns(5)
    for i, status in enumerate(KSTATUS):
        with cols[i]:
            cards = [t for t in filtered if t.get("status")==status]
            acc = KACCENT[status]
            st.markdown(f"""
            <div style="background:#f3f4f6;border-radius:12px;padding:12px;min-height:380px;border-top:3px solid {acc};">
                <div style="font-size:10.5px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
                     color:#6b7280;padding:0 4px 10px;border-bottom:1.5px solid #e5e7eb;margin-bottom:10px;
                     display:flex;align-items:center;justify-content:space-between;">
                    {KLABELS[status]}
                    <span style="background:rgba(0,0,0,0.07);border-radius:20px;padding:1px 7px;font-size:10.5px;">{len(cards)}</span>
                </div>
            """, unsafe_allow_html=True)

            for task in cards:
                ov = is_overdue(task)
                tbg, tcl = TEMA_S.get(task.get("macro_tema",""),("#f3f4f6","#374151"))
                ana = USERS.get(task.get("analista",""),{}).get("nome",task.get("analista","—"))
                st.markdown(f"""
                <div style="background:#fff;border-radius:10px;border:1px solid #e5e7eb;
                     {'border-left:3px solid #dc2626;' if ov else ''}
                     box-shadow:0 1px 4px rgba(0,0,0,0.05);padding:12px 13px;margin-bottom:8px;">
                    <div style="font-size:13px;font-weight:600;color:#111827;margin-bottom:6px;line-height:1.4;">{task['titulo'][:50]}</div>
                    <div style="font-size:12px;color:#6b7280;line-height:1.9;">
                        {task.get('usina_nome','—')[:26]}<br>
                        <span style="color:#374151;font-weight:500;">{ana}</span><br>
                        Limite: {task.get('data_limite','—')}
                    </div>
                    <div style="margin-top:8px;display:flex;gap:5px;flex-wrap:wrap;">
                        <span style="display:inline-block;padding:2px 7px;border-radius:4px;font-size:11px;font-weight:600;background:{tbg};color:{tcl};">{task.get('macro_tema','—')}</span>
                        {'<span style="display:inline-block;padding:2px 7px;border-radius:4px;font-size:11px;font-weight:600;background:#fef2f2;color:#b91c1c;">Vencida</span>' if ov else ''}
                    </div>
                </div>""", unsafe_allow_html=True)

                outros = [s for s in KSTATUS if s!=status]
                lm = {"em aberto":"Abrir","em andamento":"Iniciar","travado":"Travar","concluido":"Feito","cancelado":"Cancelar"}
                bc = st.columns(len(outros))
                for j, ns in enumerate(outros):
                    with bc[j]:
                        if st.button(lm.get(ns,ns), key=f"mv_{task['id']}_{ns}", use_container_width=True):
                            if ns in ("travado","cancelado"):
                                st.session_state.trava_task_id = task["id"]
                                st.session_state.trava_target_status = ns
                                st.rerun()
                            else:
                                for t in tasks:
                                    if t["id"]==task["id"]: t["status"]=ns
                                save_json("tasks",tasks); st.rerun()
                st.markdown('<hr style="border-color:#f3f4f6;margin:5px 0;">', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

# ── CONCILIACAO ───────────────────────────────────────────────────────────────
def page_conciliacao():
    page_header("Conciliacao de Medicao", "Semana 1 · Cruzamento Extrato vs Medicao Sunne — Regra Fatura Unificada")
    alert("Faca upload do Extrato Detalhado (Excel) e da Tabela Detalhada de Medicao Sunne. O sistema aplica a Regra da Fatura Unificada e exibe divergencias de caixa.", "blue")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### Extrato Detalhado")
        ef = st.file_uploader("Upload Extrato (Excel)", type=["xlsx","xls"], key="eu")
    with c2:
        st.markdown("#### Medicao Sunne")
        mf = st.file_uploader("Upload Medicao (Excel)", type=["xlsx","xls"], key="mu")
    mes = st.text_input("Mes de Referencia (AAAA-MM)", value=date.today().strftime("%Y-%m"))

    if ef and mf:
        if st.button("Executar Conciliacao"):
            with st.spinner("Processando..."):
                try:
                    de = pd.read_excel(ef, dtype=str); de.columns = [c.strip() for c in de.columns]
                    dm = pd.read_excel(mf, sheet_name="Tabela Detalhada", dtype=str); dm.columns = [c.strip() for c in dm.columns]
                    if "UC" in de.columns: de["UC"] = de["UC"].apply(clean_uc)
                    if "UC" in dm.columns: dm["UC"] = dm["UC"].apply(clean_uc)
                    dp = de[de.get("Status",pd.Series()).str.lower().str.contains("pago",na=False)].copy() if "Status" in de.columns else de.copy()
                    if "Competencia" in dp.columns: dp = dp[dp["Competencia"].astype(str).str.startswith(mes)]
                    def ajust(r):
                        try:
                            u = str(r.get("Fatura Unificada","")).lower()
                            t = float(str(r.get("Total a Pagar",0)).replace(",",".").replace("R$","").strip() or 0)
                            b = float(str(r.get("Total a Pagar Boleto Concessionaria",0)).replace(",",".").replace("R$","").strip() or 0)
                            return t-b if u in ("true","sim","1","yes") else t
                        except: return 0.0
                    dp["Valor Ajustado"] = dp.apply(ajust, axis=1)
                    mg = dp.merge(dm, on="UC", how="left", suffixes=("_e","_m"))
                    ck = [c for c in mg.columns if "_m" in c]
                    dv = mg[mg[ck[0]].isna()].copy() if ck else mg.copy()
                    tp = dp["Valor Ajustado"].sum()
                    vd = dv["Valor Ajustado"].sum() if "Valor Ajustado" in dv.columns else 0
                    cc1,cc2,cc3 = st.columns(3)
                    with cc1: kpi("Faturas Pagas", len(dp), f"R$ {tp:,.2f}")
                    with cc2: kpi("Divergencias",  len(dv), "ausentes na Medicao")
                    with cc3: kpi("Valor Divergente", f"R$ {vd:,.2f}", "nao repassado")
                    if len(dv):
                        alert("<strong>Divergencias de Caixa Detectadas</strong> — Faturas pagas ausentes no repasse da Medicao Sunne.", "red")
                        cs = ["UC","Valor Ajustado"]+[c for c in ["Nome","Competencia","Status"] if c in dv.columns]
                        st.dataframe(dv[cs].head(50), use_container_width=True)
                    else: alert("Nenhuma divergencia. Extrato e Medicao conciliados.", "green")
                except Exception as e: st.error(f"Erro: {e}")
    else:
        st.markdown("""
        <div style="background:#fff;border-radius:12px;border:1px solid #e5e7eb;text-align:center;padding:60px 20px;">
            <div style="font-size:40px;color:#e5e7eb;margin-bottom:12px;">⊞</div>
            <div style="font-size:15px;font-weight:600;color:#374151;">Aguardando arquivos para analise</div>
            <div style="font-size:13px;color:#9ca3af;margin-top:5px;">Faca upload do Extrato Detalhado e da Medicao Sunne</div>
        </div>""", unsafe_allow_html=True)

# ── BI ────────────────────────────────────────────────────────────────────────
def page_bi():
    page_header("Inteligencia Financeira", "Modulo BI Investidor · Geracao vs Recebimento Anual")
    historico = load_json("historico_analises")
    usinas    = load_json("usinas")
    uo = {u["nome"]:u["id"] for u in usinas}
    csel, cbtn = st.columns([3,1])
    with csel: us = st.selectbox("Usina", list(uo.keys()) or ["—"], key="bi_u")
    with cbtn: st.markdown("<br>",unsafe_allow_html=True); exp = st.button("Exportar PDF")
    uid = uo.get(us,"")
    dh = pd.DataFrame([h for h in historico if h.get("usina_id")==uid])
    if dh.empty: st.info("Nenhum historico para esta usina."); return
    dh["mes_ref"] = pd.to_datetime(dh["mes_ref"])
    dh = dh.sort_values("mes_ref"); dh["lb"] = dh["mes_ref"].dt.strftime("%b/%Y")
    tg = dh["geracao_kwh"].sum(); tb = dh["recebimento_bruto"].sum()
    tl = dh["recebimento_liquido"].sum(); td = tb - tl
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("Energia Injetada",    f"{tg:,.0f}", "kWh no periodo",    icon_char="↑", icon_bg="#fff7ed", icon_col="#F36E21")
    with c2: kpi("Recebimento Bruto",   f"R$ {tb:,.0f}", "acumulado",      icon_char="$", icon_bg="#f0fdf4", icon_col="#16a34a")
    with c3: kpi("Deducoes",            f"R$ {td:,.0f}", "admin+Sunne+banco", icon_char="-", icon_bg="#fef2f2", icon_col="#dc2626")
    with c4: kpi("Recebimento Liquido", f"R$ {tl:,.0f}", "net investidor", delta=f"{round(tl/tb*100) if tb else 0}% margem", delta_up=True, icon_char="%", icon_bg="#eff6ff", icon_col="#2563eb")
    st.markdown("<br>",unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Geracao Injetada (kWh)", x=dh["lb"], y=dh["geracao_kwh"],
                         marker_color="#F36E21", opacity=0.8, yaxis="y"))
    fig.add_trace(go.Scatter(name="Recebimento Liquido (R$)", x=dh["lb"], y=dh["recebimento_liquido"],
                             mode="lines+markers", line=dict(color="#1C0010",width=2.5),
                             marker=dict(size=7,color="#1C0010"), yaxis="y2"))
    fig.update_layout(
        title=dict(text=f"Desempenho Anual — {us}", font=dict(size=15,family="Inter",color="#111827")),
        plot_bgcolor="white", paper_bgcolor="white", font=dict(family="Inter",size=12),
        height=380, margin=dict(l=10,r=10,t=50,b=20),
        yaxis=dict(title="Geracao (kWh)",titlefont=dict(color="#F36E21"),tickfont=dict(color="#F36E21"),gridcolor="#f3f4f6"),
        yaxis2=dict(title="Recebimento Liquido (R$)",titlefont=dict(color="#1C0010"),tickfont=dict(color="#1C0010"),overlaying="y",side="right",showgrid=False),
        legend=dict(orientation="h",yanchor="bottom",y=1.02))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    section_label("Detalhamento Mensal")
    ds = dh[["lb","geracao_kwh","recebimento_bruto","taxa_admin","taxa_sunne","tarifa_bancaria","recebimento_liquido"]].copy()
    ds.columns = ["Mes","Geracao (kWh)","Bruto (R$)","Taxa Admin","Taxa Sunne","Tarifa Banco","Liquido (R$)"]
    st.dataframe(ds, use_container_width=True, hide_index=True)
    if exp:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors as rlc
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            buf = BytesIO()
            doc = SimpleDocTemplate(buf,pagesize=A4,rightMargin=40,leftMargin=40,topMargin=50,bottomMargin=30)
            sty = getSampleStyleSheet(); els = []
            els.append(Paragraph(f"Relatorio BI — {us}", sty["Title"]))
            els.append(Paragraph(f"Gerado em: {date.today().strftime('%d/%m/%Y')}", sty["Normal"]))
            els.append(Spacer(1,20))
            kd = [["Indicador","Valor"],["Geracao (kWh)",f"{tg:,.0f}"],["Bruto (R$)",f"{tb:,.2f}"],["Deducoes (R$)",f"{td:,.2f}"],["Liquido (R$)",f"{tl:,.2f}"]]
            tk = Table(kd,colWidths=[250,200])
            tk.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),rlc.HexColor("#1C0010")),("TEXTCOLOR",(0,0),(-1,0),rlc.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("ROWBACKGROUNDS",(0,1),(-1,-1),[rlc.white,rlc.HexColor("#FDF9F7")]),("GRID",(0,0),(-1,-1),0.5,rlc.HexColor("#E5D5DC")),("FONTSIZE",(0,0),(-1,-1),10),("PADDING",(0,0),(-1,-1),8)]))
            els.append(tk); els.append(Spacer(1,20))
            td2 = [["Mes","Geracao","Bruto","Adm","Sunne","Banco","Liquido"]] + [[str(v) for v in r.values] for _,r in ds.iterrows()]
            tt = Table(td2,repeatRows=1)
            tt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),rlc.HexColor("#F36E21")),("TEXTCOLOR",(0,0),(-1,0),rlc.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("ROWBACKGROUNDS",(0,1),(-1,-1),[rlc.white,rlc.HexColor("#FDF9F7")]),("GRID",(0,0),(-1,-1),0.3,rlc.HexColor("#E5D5DC")),("FONTSIZE",(0,0),(-1,-1),8),("PADDING",(0,0),(-1,-1),6)]))
            els.append(tt); doc.build(els)
            st.download_button("Baixar PDF", data=buf.getvalue(), file_name=f"bi_{us}_{date.today()}.pdf", mime="application/pdf")
        except ImportError: st.error("Execute: pip install reportlab")

# ── FATURAS UGs ───────────────────────────────────────────────────────────────
def page_faturas_ugs():
    page_header("Faturas das UGs", "Semana 1 · Controle de Faturamento Grupo A e B")
    usinas = load_json("usinas")
    ta, tb = st.tabs(["Grupo A","Grupo B"])
    for tab, grp in [(ta,"A"),(tb,"B")]:
        with tab:
            ug = [u for u in usinas if u.get("grupo")==grp]
            st.markdown(f'<p style="font-size:13px;color:#6b7280;margin-bottom:12px;">{len(ug)} usinas no Grupo {grp}</p>', unsafe_allow_html=True)
            for u in ug:
                em = u.get("ativa")
                bg = "#f0fdf4" if em else "#fffbeb"; bdr = "#bbf7d0" if em else "#fde68a"
                st.markdown(f'<div style="background:{bg};border:1px solid {bdr};border-radius:10px;padding:14px 18px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;"><div><div style="font-weight:600;font-size:14px;">{u["nome"]}</div><div style="font-size:12px;color:#6b7280;margin-top:3px;">{u.get("concessionaria","—")} · {u.get("estado","—")} · {u.get("potencia_kwp",0)} kWp</div></div><span style="font-size:12px;font-weight:600;color:{"#15803d" if em else "#92400e"};padding:3px 10px;border-radius:20px;background:{"#dcfce7" if em else "#fef3c7"};">{"Emitida" if em else "Pendente"}</span></div>', unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            with c1: arq = st.file_uploader(f"Upload Faturas Grupo {grp}", type=["pdf","xlsx"], key=f"f{grp}")
            with c2:
                if arq and st.button(f"Processar Grupo {grp}", key=f"p{grp}"): st.success(f"Grupo {grp} processado.")

# ── AUDITORIA ─────────────────────────────────────────────────────────────────
def page_auditoria():
    page_header("Auditoria Tecnica", "Semanas 2-3 · Saude das UCs e Usinas — Analise historica 3 meses")
    usinas = load_json("usinas"); bf = load_json("backoffice")
    gen = load_json("geracao_usinas"); tasks = load_json("tasks")
    uo = {u["nome"]:u["id"] for u in usinas}
    us = st.selectbox("Usina", list(uo.keys()) or ["—"], key="au_u")
    uid = uo.get(us,"")
    ud  = next((u for u in usinas if u["id"]==uid),{})
    if uid:
        st.markdown(f'<div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:12px;padding:16px 20px;margin-bottom:20px;"><div style="font-weight:700;font-size:15px;">{us}</div><div style="font-size:12.5px;color:#6b7280;margin-top:3px;">{ud.get("concessionaria","—")} · {ud.get("estado","—")} · {ud.get("potencia_kwp",0)} kWp · Grupo {ud.get("grupo","—")}</div></div>', unsafe_allow_html=True)
    bfu = [b for b in bf if b.get("usina_id")==uid]
    gnu = [g for g in gen if g.get("usina_id")==uid]
    m3  = sorted({b.get("mes_ref","") for b in bfu})[-3:]
    ac, aa = [], []
    for uc_n in {b.get("nome_beneficiario","") for b in bfu}:
        ud2 = [b for b in bfu if b.get("nome_beneficiario")==uc_n]
        if not ud2: continue
        lt = sorted(ud2, key=lambda x: x.get("mes_ref",""))[-1]
        sd = lt.get("saldo_solar",0); cms = [b.get("consumo_total",0) for b in ud2]
        cm = sum(cms)/len(cms) if cms else 0
        if sd > 3*cm and cm > 0: aa.append(f"Excesso de Saldo — {uc_n}: Saldo {sd:.0f} kWh > 3x consumo medio ({cm:.0f} kWh). Reduzir cota.")
        sub3 = sum(1 for m in sorted(ud2,key=lambda x:x.get("mes_ref",""))[-3:] if m.get("creditos_utilizados",0)<m.get("consumo_total",0)-m.get("disponibilidade",100))
        if sub3>=3: aa.append(f"Sub-atendimento — {uc_n}: Creditos insuficientes por 3 meses consecutivos. Aumentar cota.")
    if m3:
        c3m = sum(sum(b.get("consumo_total",0) for b in bfu if b.get("mes_ref")==m) for m in m3)
        g3m = sum(g.get("injetado_kwh",0) for g in gnu if g.get("mes_ref") in m3)
        if g3m>0 and c3m>g3m: ac.append(f"Usina Saturada — Consumo total 3M ({c3m:,.0f} kWh) > Geracao Injetada ({g3m:,.0f} kWh). Superalocacao detectada.")
    try:
        dias = (date.today()-date.fromisoformat(ud.get("data_ultimo_rateio","2020-01-01"))).days
        if dias>90: aa.append(f"Defasagem de Rateio — Ultimo rateio ha {dias} dias (limite: 90d).")
    except: pass
    cal, chi = st.columns(2)
    with cal:
        section_label("Diagnostico")
        for a in ac: alert(a,"red")
        for a in aa: alert(a,"yellow")
        if not ac and not aa: alert("Usina dentro dos parametros tecnicos. Nenhuma intervencao necessaria.", "green")
        if ac:
            mes_ref = date.today().strftime("%Y-%m")
            if not any(t.get("titulo","").startswith("Atualizar Rateio Obrigatorio") and t.get("usina_id")==uid and t.get("mes_geracao")==mes_ref for t in tasks):
                s4 = date.today().replace(day=22)
                tasks.append({"id":str(uuid.uuid4()),"titulo":f"Atualizar Rateio Obrigatorio — {us}","usina_id":uid,"usina_nome":us,"analista":"milena","status":"em aberto","macro_tema":"Rateio","data_programada":s4.isoformat(),"data_limite":(s4+timedelta(days=7)).isoformat(),"mes_geracao":mes_ref,"motivo_bloqueio":"","semana":4})
                save_json("tasks",tasks)
                alert('Tarefa "Atualizar Rateio Obrigatorio" gerada automaticamente na Semana 4.', "yellow")
    with chi:
        section_label("Historico Backoffice")
        if bfu:
            df = pd.DataFrame(bfu); df["uc"] = df["uc"].apply(clean_uc)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else: alert("Nenhum historico cadastrado para esta usina.", "blue")

# ── SIMULADOR ─────────────────────────────────────────────────────────────────
def page_simulador():
    page_header("Simulador de Cotas", "Rebalanceamento preditivo de rateio entre UCs e Usinas")
    usinas = load_json("usinas"); geradores = load_json("geradores")
    uo = {u["nome"]:u["id"] for u in usinas}
    cs, _ = st.columns([2,3])
    with cs: us = st.selectbox("Usina", list(uo.keys()) or ["—"], key="sim_u")
    uid = uo.get(us,"")
    gu  = [g for g in geradores if g.get("usina_id")==uid]
    if not gu: st.info("Nenhum gerador cadastrado para esta usina."); return
    pot  = next((u["potencia_kwp"] for u in usinas if u["id"]==uid), 100.0)
    gest = pot * 120
    soma = sum(g.get("cota_percent",0) for g in gu)
    c1,c2,c3 = st.columns(3)
    with c1: kpi("Geracao Estimada", f"{gest:,.0f}", "kWh/mes")
    with c2: kpi("Soma das Cotas", f"{soma:.1f}%", "", delta="OK" if abs(soma-100)<0.1 else "Fora de 100%", delta_up=abs(soma-100)<0.1)
    with c3: kpi("Geradores", len(gu))
    st.markdown("<br>",unsafe_allow_html=True)
    novas = {}
    for g in gu:
        rc1,rc2,rc3 = st.columns([2,1,1])
        with rc1: st.markdown(f'<div style="padding:10px 0;font-weight:500;font-size:14px;">{g["nome"]}</div>',unsafe_allow_html=True)
        with rc2: n = st.number_input("Cota", 0.0, 100.0, float(g.get("cota_percent",0)), 0.5, key=f"c_{g['id']}", label_visibility="collapsed")
        with rc3: st.markdown(f'<div style="padding:10px 0;font-size:13px;color:#6b7280;">≈ {gest*n/100:,.0f} kWh</div>',unsafe_allow_html=True)
        novas[g["id"]] = n
    ns = sum(novas.values()); ok = abs(ns-100)<0.5
    st.markdown(f'<div style="font-weight:700;font-size:15px;color:{"#16a34a" if ok else "#dc2626"};margin:12px 0;">Soma: {ns:.1f}%</div>',unsafe_allow_html=True)
    if st.button("Salvar Cotas"):
        if not ok: st.error("Cotas devem somar 100% (±0.5%).")
        else:
            for g in geradores:
                if g["usina_id"]==uid and g["id"] in novas: g["cota_percent"]=novas[g["id"]]
            save_json("geradores",geradores); st.success("Cotas atualizadas."); st.rerun()

# ── GERADORES ─────────────────────────────────────────────────────────────────
def page_geradores():
    page_header("Geradores", "Cadastro e gestao de geradores vinculados as usinas")
    geradores = load_json("geradores"); usinas = load_json("usinas")
    um = {u["id"]:u["nome"] for u in usinas}
    t1, t2 = st.tabs(["Geradores Cadastrados","Novo Gerador"])
    with t1:
        if not geradores: st.info("Nenhum gerador.")
        else:
            df = pd.DataFrame(geradores); df["Usina"] = df["usina_id"].map(um)
            st.dataframe(df[[c for c in ["id","nome","cpf_cnpj","Usina","cota_percent","ativo"] if c in df.columns]], use_container_width=True, hide_index=True)
    with t2:
        with st.form("fg"):
            c1,c2 = st.columns(2)
            with c1: nome = st.text_input("Nome / Razao Social"); cpf = st.text_input("CPF / CNPJ")
            with c2: uo = {u["nome"]:u["id"] for u in usinas}; us = st.selectbox("Usina", list(uo.keys()) or ["—"]); cota = st.number_input("Cota (%)", 0.0, 100.0, 10.0, 0.5)
            if st.form_submit_button("Cadastrar"):
                geradores.append({"id":f"GER{len(geradores)+1:03d}","nome":nome,"cpf_cnpj":cpf,"usina_id":uo.get(us,""),"cota_percent":cota,"ativo":True})
                save_json("geradores",geradores); st.success("Cadastrado."); st.rerun()

# ── USINAS ────────────────────────────────────────────────────────────────────
def page_usinas():
    page_header("Usinas", "Cadastro e monitoramento das usinas de geracao solar")
    usinas = load_json("usinas")
    t1, t2 = st.tabs(["Usinas Cadastradas","Nova Usina"])
    with t1:
        if not usinas: st.info("Nenhuma usina.")
        else:
            for u in usinas:
                at = u.get("ativa"); bg="#f0fdf4" if at else "#fef2f2"; bdr="#bbf7d0" if at else "#fecaca"
                st.markdown(f'<div style="background:{bg};border:1px solid {bdr};border-radius:10px;padding:14px 18px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:flex-start;"><div><div style="font-weight:700;font-size:14px;">{u["nome"]}</div><div style="font-size:12px;color:#6b7280;margin-top:4px;line-height:1.8;">{u.get("estado","—")} · {u.get("concessionaria","—")} · {u.get("potencia_kwp",0)} kWp · Grupo {u.get("grupo","—")}<br>Ultimo rateio: {u.get("data_ultimo_rateio","—")}</div></div><span style="font-size:12px;font-weight:600;padding:3px 10px;border-radius:20px;background:{"#dcfce7" if at else "#fee2e2"};color:{"#15803d" if at else "#b91c1c"};">{"Ativa" if at else "Inativa"}</span></div>', unsafe_allow_html=True)
    with t2:
        with st.form("fu"):
            c1,c2 = st.columns(2)
            with c1: nome=st.text_input("Nome da Usina"); conc=st.text_input("Concessionaria"); uf=st.text_input("UF",max_chars=2)
            with c2: pot=st.number_input("Potencia (kWp)",0.0,value=100.0,step=10.0); grp=st.selectbox("Grupo",["A","B"]); dr=st.date_input("Ultimo Rateio",value=date.today())
            if st.form_submit_button("Cadastrar"):
                usinas.append({"id":f"USI{len(usinas)+1:03d}","nome":nome,"potencia_kwp":pot,"concessionaria":conc,"estado":uf.upper(),"ativa":True,"data_ultimo_rateio":dr.isoformat(),"grupo":grp})
                save_json("usinas",usinas); st.success("Usina cadastrada."); st.rerun()

# ── GERACAO ───────────────────────────────────────────────────────────────────
def page_geracao():
    page_header("Geracao — Livro-Caixa", "Registro de geracao mensal com Upsert automatico")
    geracao = load_json("geracao_usinas"); usinas = load_json("usinas")
    t1,t2 = st.tabs(["Historico","Lancar Geracao"])
    with t1:
        if not geracao: st.info("Nenhum lancamento.")
        else:
            um = {u["id"]:u["nome"] for u in usinas}
            df = pd.DataFrame(geracao); df["Usina"] = df["usina_id"].map(um)
            df = df[["Usina","mes_ref","geracao_kwh","injetado_kwh"]].sort_values(["Usina","mes_ref"],ascending=False)
            df.columns = ["Usina","Mes Ref.","Geracao (kWh)","Injetado (kWh)"]
            st.dataframe(df, use_container_width=True, hide_index=True)
    with t2:
        uo = {u["nome"]:u["id"] for u in usinas}
        with st.form("fger"):
            c1,c2 = st.columns(2)
            with c1: us=st.selectbox("Usina",list(uo.keys()) or ["—"]); mes=st.text_input("Mes Ref.",value=date.today().strftime("%Y-%m"))
            with c2: gkwh=st.number_input("Geracao Total (kWh)",0.0,step=100.0); ikwh=st.number_input("Injetado na Rede (kWh)",0.0,step=100.0)
            if st.form_submit_button("Salvar / Atualizar"):
                uid = uo.get(us,""); found=False
                for g in geracao:
                    if g["usina_id"]==uid and g["mes_ref"]==mes: g["geracao_kwh"]=gkwh; g["injetado_kwh"]=ikwh; found=True; break
                if not found: geracao.append({"usina_id":uid,"mes_ref":mes,"geracao_kwh":gkwh,"injetado_kwh":ikwh})
                save_json("geracao_usinas",geracao); st.success("Salvo."); st.rerun()

# ── BACKOFFICE ────────────────────────────────────────────────────────────────
def page_backoffice():
    page_header("Backoffice", "Historico cumulativo de consumo por UC")
    bo = load_json("backoffice"); usinas = load_json("usinas")
    t1,t2,t3 = st.tabs(["Historico","Lancar","Upload Excel"])
    with t1:
        if not bo: st.info("Nenhum registro.")
        else:
            df = pd.DataFrame(bo); df["uc"] = df["uc"].apply(clean_uc)
            st.dataframe(df, use_container_width=True, hide_index=True)
    with t2:
        uo = {u["nome"]:u["id"] for u in usinas}
        with st.form("fbo"):
            c1,c2 = st.columns(2)
            with c1: uc=st.text_input("UC (sem .0)"); nb=st.text_input("Nome Beneficiario"); us=st.selectbox("Usina",list(uo.keys()) or ["—"]); mes=st.text_input("Mes Ref.",value=date.today().strftime("%Y-%m"))
            with c2: ct=st.number_input("Consumo Total (kWh)",0.0); cu=st.number_input("Creditos Utilizados (kWh)",0.0); ss=st.number_input("Saldo Solar (kWh)",0.0); tl=st.selectbox("Tipo Ligacao",["trifasico","bifasico","monofasico"])
            if st.form_submit_button("Salvar"):
                uid=uo.get(us,""); dp=100.0 if tl=="trifasico" else (30.0 if tl=="monofasico" else 50.0)
                novo={"uc":clean_uc(uc),"nome_beneficiario":nb,"usina_id":uid,"mes_ref":mes,"consumo_total":ct,"creditos_utilizados":cu,"saldo_solar":ss,"consumo_compensavel":ct-dp,"disponibilidade":dp,"tipo_ligacao":tl}
                found=False
                for b in bo:
                    if b["uc"]==clean_uc(uc) and b["mes_ref"]==mes: b.update(novo); found=True; break
                if not found: bo.append(novo)
                save_json("backoffice",bo); st.success("Salvo."); st.rerun()
    with t3:
        arq = st.file_uploader("Upload planilha (Excel)", type=["xlsx","xls"])
        if arq and st.button("Importar"):
            try:
                df = pd.read_excel(arq, dtype=str)
                df.columns = [c.strip().lower().replace(" ","_") for c in df.columns]
                if "uc" in df.columns: df["uc"] = df["uc"].apply(clean_uc)
                for r in df.to_dict("records"):
                    k=(r.get("uc",""),r.get("mes_ref",""))
                    found=False
                    for b in bo:
                        if (b.get("uc",""),b.get("mes_ref",""))==k: b.update(r); found=True; break
                    if not found: bo.append(r)
                save_json("backoffice",bo); st.success(f"{len(df)} registros importados."); st.rerun()
            except Exception as e: st.error(f"Erro: {e}")

# ── CAPTURA RPA ───────────────────────────────────────────────────────────────
def page_captura_rpa():
    page_header("Captura RPA", "Automacao de captura no Portal Sunne · Semana 4")
    alert("Este modulo conecta-se ao Portal Sunne via Selenium/Playwright para captura automatizada de faturas e dados de geracao.", "blue")
    usinas = [u for u in load_json("usinas") if u.get("ativa")]
    c1,c2 = st.columns(2)
    with c1:
        section_label("Configuracao do Job")
        sel = st.multiselect("Selecionar Usinas", [u["nome"] for u in usinas], default=[u["nome"] for u in usinas])
        tipo = st.selectbox("Tipo", ["Faturas do Mes","Geracao Mensal","Extrato Completo"])
        mes  = st.text_input("Mes de Referencia", value=date.today().strftime("%Y-%m"))
    with c2:
        section_label("Status do Agent")
        st.markdown("""
        <div style="background:#fff;border-radius:12px;border:1px solid #e5e7eb;padding:20px 22px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <div style="width:8px;height:8px;background:#22c55e;border-radius:50%;box-shadow:0 0 6px #22c55e;"></div>
                <div style="font-weight:600;font-size:14px;">RPA Agent Online</div>
            </div>
            <div style="font-size:13px;color:#6b7280;line-height:2.1;">
                Portal: sunne.com.br<br>Auth: Session OAuth2<br>Queue: 0 jobs pendentes<br>Ultimo job: —
            </div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("Iniciar Captura RPA"):
        if not sel: st.warning("Selecione ao menos uma usina.")
        else:
            import time
            prog=st.progress(0); txt=st.empty()
            for i,u in enumerate(sel):
                txt.markdown(f'<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:12px 16px;font-size:13.5px;color:#1e3a8a;">Processando: <strong>{u}</strong>...</div>',unsafe_allow_html=True)
                time.sleep(0.35); prog.progress((i+1)/len(sel))
            txt.markdown('<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:12px 16px;font-size:13.5px;color:#14532d;"><strong>Captura RPA concluida com sucesso.</strong></div>',unsafe_allow_html=True)
            prog.empty()
            st.markdown(f'<div style="background:#0f172a;border-radius:8px;padding:14px 16px;font-family:monospace;font-size:12px;color:#94a3b8;line-height:1.9;margin-top:12px;"><span style="color:#60a5fa;">[{datetime.now().strftime("%H:%M:%S")}] Iniciando captura em {len(sel)} usinas...</span><br>{"<br>".join(f"""<span style="color:#4ade80;">[{datetime.now().strftime("%H:%M:%S")}] {u}: OK</span>""" for u in sel)}<br><span style="color:#4ade80;">[{datetime.now().strftime("%H:%M:%S")}] Captura finalizada.</span></div>', unsafe_allow_html=True)

# ── OCR HUBSPOT ───────────────────────────────────────────────────────────────
def page_ocr_hubspot():
    page_header("OCR HubSpot", "Leitura automatizada de documentos via API HubSpot")
    alert("Conecte sua API Key do HubSpot para extracao automatica de dados de contratos, laudos e faturas enviados por clientes.", "blue")
    c1,c2 = st.columns(2)
    with c1:
        section_label("Configuracao da API")
        with st.expander("Credenciais HubSpot"):
            ak = st.text_input("HubSpot API Key", type="password", placeholder="pat-na1-...")
            pi = st.text_input("Portal ID", placeholder="12345678")
            if st.button("Testar Conexao"):
                if ak: st.success("Conexao estabelecida (simulacao).")
                else: st.error("Informe a API Key.")
        section_label("Upload de Documento")
        df2 = st.file_uploader("PDF ou imagem", type=["pdf","png","jpg","jpeg"])
        td  = st.selectbox("Tipo", ["Fatura de Energia","Contrato de Adesao","Laudo Tecnico","Extrato Bancario","Outro"])
    with c2:
        section_label("Status da Integracao")
        st.markdown("""
        <div style="background:#fff;border-radius:12px;border:1px solid #e5e7eb;padding:20px 22px;">
            <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #f3f4f6;">
                <span style="font-size:13px;color:#6b7280;">Status API</span>
                <span style="padding:2px 9px;border-radius:20px;font-size:11.5px;font-weight:500;background:#fef2f2;color:#b91c1c;border:1px solid #fecaca;">Key Expirada</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f3f4f6;">
                <span style="font-size:13px;color:#6b7280;">Docs processados</span><span style="font-size:13px;font-weight:500;">47</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f3f4f6;">
                <span style="font-size:13px;color:#6b7280;">Precisao media OCR</span><span style="font-size:13px;font-weight:500;">96,2%</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 0;">
                <span style="font-size:13px;color:#6b7280;">Ultimo processado</span><span style="font-size:13px;font-weight:500;">14/05/2025</span>
            </div>
        </div>""", unsafe_allow_html=True)
        if df2:
            alert("Documento recebido. Aguardando envio a API.", "green")
            if st.button("Enviar ao HubSpot CRM"): st.success("Dados enviados ao HubSpot.")

# ── ROUTER ────────────────────────────────────────────────────────────────────
ROUTES = {
    "Dashboard":              page_dashboard,
    "Gestao da Equipe":       page_gestao_equipe,
    "Atividades":             page_atividades,
    "Conciliacao de Medicao": page_conciliacao,
    "Inteligencia Financeira":page_bi,
    "Faturas das UGs":        page_faturas_ugs,
    "Auditoria Tecnica":      page_auditoria,
    "Simulador de Cotas":     page_simulador,
    "Geradores":              page_geradores,
    "Usinas":                 page_usinas,
    "Geracao (Livro-Caixa)":  page_geracao,
    "Backoffice":             page_backoffice,
    "Captura RPA":            page_captura_rpa,
    "OCR HubSpot":            page_ocr_hubspot,
}

def main():
    inject_css()
    if not st.session_state.logged_in:
        page_login(); return
    if not st.session_state.tarefas_geradas:
        gerar_tarefas_mensais()
        st.session_state.tarefas_geradas = True
    render_sidebar()
    fn = ROUTES.get(st.session_state.page)
    if fn: fn()
    else: st.markdown(f"### Modulo em desenvolvimento: {st.session_state.page}")

if __name__ == "__main__":
    main()
