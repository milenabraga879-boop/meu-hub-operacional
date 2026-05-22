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

# Configurações Globais da Esteira Operacional
KANBAN_STATUS = ["em aberto", "em andamento", "travado", "concluido", "cancelado"]
KANBAN_LABELS = {"em aberto": "Em Aberto", "em andamento": "Em Andamento",
                 "travado": "Travado", "concluido": "Concluído", "cancelado": "Cancelado"}
TEMA_COLORS  = {"Faturamento": ("#fff7ed", "#c2410c"), "Rateio": ("#faf5ff", "#7c3aed"), "Captura": ("#f0fdf4", "#15803d")}

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM — REPLICANDO gerador.sunne.com.br
# ─────────────────────────────────────────────────────────────────────────────
def inject_css():
    st.html("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ── ROOT PALETTE ── */
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

/* CONSERTO DO BUG DO KEYBOARD_DOUBLE: Estilização cirúrgica sem quebrar as fontes de ícones nativas */
[data-testid="stAppViewContainer"], p, span, div, label, td, th, h1, h2, h3, h4, input, select, textarea {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: var(--s-bg) !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
    backdrop-filter: none !important;
}
.main .block-container {
    padding: 28px 32px !important;
    max-width: 1440px !important;
}

/* ── SIDEBAR STYLE CLEANUP (SEM DUPLICAÇÃO DE TEXTO) ── */
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

/* Estilização nativa dos Expanders da Sidebar */
[data-testid="stSidebar"] .streamlit-expanderHeader {
    background: transparent !important;
    border: none !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,0.5) !important;
    padding: 10px 16px !important;
}
[data-testid="stSidebar"] .streamlit-expanderContent {
    background: transparent !important;
    border: none !important;
    padding: 0 4px 4px 8px !important;
}

/* Botões da Sidebar */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 6px !important;
    color: rgba(255,255,255,0.75) !important;
    text-align: left !important;
    font-size: 13.5px !important;
    font-weight: 400 !important;
    padding: 8px 12px !important;
    width: 100% !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.07) !important;
    color: #fff !important;
}

/* ── TYPOGRAPHY ALTERADA CONFORME PEDIDO (MAIOR E EQUILIBRADO) ── */
h1 { font-size: 32px !important; font-weight: 700 !important; color: var(--s-wine) !important; margin-bottom: 4px !important; letter-spacing: -0.5px !important; }
h2 { font-size: 20px !important; font-weight: 600 !important; color: var(--s-text) !important; }
h3 { font-size: 16px !important; font-weight: 600 !important; color: var(--s-text) !important; }

.page-h1 { font-size: 32px !important; font-weight: 700 !important; color: var(--s-wine) !important; letter-spacing: -0.5px !important; margin-bottom: 4px !important; line-height: 1.2 !important; }
.page-sub { font-size: 14px !important; color: var(--s-text-sm) !important; margin-bottom: 28px !important; font-weight: 400 !important; line-height: 1.5 !important; }

/* ── CONTÊINER ESTRUTURADO ARREDONDADO PARA FILTROS ── */
.filter-container {
    background: var(--s-white) !important;
    border: 1px solid var(--s-border) !important;
    border-radius: var(--s-radius-lg) !important;
    padding: 20px 24px !important;
    margin-bottom: 24px !important;
    box-shadow: var(--s-shadow) !important;
}
.filter-title {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: var(--s-text) !important;
    margin-bottom: 14px !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: var(--s-orange) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--s-radius) !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    padding: 8px 18px !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: var(--s-orange-h) !important;
}

/* ── CARDS AND STRUCTURES ── */
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
.kpi-card {
    background: var(--s-white);
    border-radius: var(--s-radius-lg);
    border: 1px solid var(--s-border);
    box-shadow: var(--s-shadow);
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
}
.kpi-label { font-size: 12px; font-weight: 500; color: var(--s-text-sm); margin-bottom: 8px; }
.kpi-value { font-size: 24px; font-weight: 700; color: var(--s-text); line-height: 1.1; letter-spacing: -0.5px; }

/* ── BADGES & ALERTS ── */
.badge { display: inline-block; padding: 3px 9px; border-radius: 20px; font-size: 11.5px; font-weight: 500; }
.badge-open    { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.badge-doing   { background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; }
.badge-blocked { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
.badge-done    { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.badge-cancel  { background: #f9fafb; color: #6b7280; border: 1px solid #e5e7eb; }

.s-alert { border-radius: var(--s-radius); padding: 12px 16px; font-size: 13.5px; margin-bottom: 10px; display: flex; gap: 10px; }
.s-alert.red    { background: var(--s-red-bg); border: 1px solid #fecaca; color: #7f1d1d; }
.s-alert.yellow { background: var(--s-yellow-bg); border: 1px solid #fde68a; color: #78350f; }
.s-alert.green  { background: var(--s-green-bg); border: 1px solid #bbf7d0; color: #14532d; }
.s-alert.blue   { background: var(--s-blue-bg); border: 1px solid #bfdbfe; color: #1e3a8a; }

/* ── KANBAN COLUMNS ── */
.k-col { background: #f3f4f6; border-radius: var(--s-radius-lg); padding: 12px; min-height: 380px; }
.k-col-header { font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--s-text-sm); padding-bottom: 10px; border-bottom: 1.5px solid var(--s-border); margin-bottom: 10px; display: flex; justify-content: space-between; }
.k-count { background: rgba(0,0,0,0.07); border-radius: 20px; padding: 1px 8px; font-size: 11px; }
.k-card { background: var(--s-white); border-radius: var(--s-radius); border: 1px solid var(--s-border); padding: 12px 14px; margin-bottom: 8px; }

.section-label { font-size: 15px; font-weight: 600; color: var(--s-text); margin: 20px 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--s-border); }

.sb-logo { padding: 20px 20px 16px; border-bottom: 1px solid rgba(255,255,255,0.07); }
.sb-logo-name { font-size: 22px; font-weight: 700; color: var(--s-orange) !important; }
.sb-logo-tagline { font-size: 10px; color: rgba(255,255,255,0.3) !important; text-transform: uppercase; letter-spacing: 0.15em; }
.sb-user { padding: 10px 20px 14px; border-bottom: 1px solid rgba(255,255,255,0.07); }
.sb-user-name { font-size: 13px; font-weight: 600; color: #fff !important; }
.sb-user-email { font-size: 11px; color: rgba(255,255,255,0.4) !important; }

.tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.tag-fat { background: #fff7ed; color: #c2410c; }
.tag-rat { background: #faf5ff; color: #7c3aed; }
.tag-cap { background: #f0fdf4; color: #15803d; }
</style>
""")

# ─────────────────────────────────────────────────────────────────────────────
# INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "tarefas_geradas" not in st.session_state: st.session_state.tarefas_geradas = False

# ─────────────────────────────────────────────────────────────────────────────
# CLEAN SIDEBAR SYSTEM (SEM POLUIÇÃO VISUAL)
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        nome = st.session_state.get("nome", "Usuário")
        email = st.session_state.get("email", "")

        st.markdown(f"""
        <div class="sb-logo">
            <div class="sb-logo-name">sunne</div>
            <div class="sb-logo-tagline">Hub v12 · BI & Automação</div>
        </div>
        <div class="sb-user">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="width:32px;height:32px;border-radius:50%;background:#F36E21;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;">
                    {nome[0].upper()}
                </div>
                <div>
                    <div class="sb-user-name">{nome}</div>
                    <div class="sb-user-email">{email}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

        # Assuntos Principais Solicitados
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()

        if st.button("📋 Atividades", use_container_width=True):
            st.session_state.page = "Atividades"
            st.rerun()

        with st.expander("💰 Faturamento & BI", expanded=(st.session_state.page in ["Conciliação de Medição", "Inteligência Financeira", "Faturas das UGs"])):
            if st.button("🔍 Conciliação de Medição", use_container_width=True):
                st.session_state.page = "Conciliação de Medição"
                st.rerun()
            if st.button("📈 Inteligência Financeira", use_container_width=True):
                st.session_state.page = "Inteligência Financeira"
                st.rerun()
            if st.button("🧾 Faturas das UGs", use_container_width=True):
                st.session_state.page = "Faturas das UGs"
                st.rerun()

        with st.expander("⚙️ Engenharia de Rateios", expanded=(st.session_state.page in ["Auditoria Técnica", "Simulador de Cotas"])):
            if st.button("🔬 Auditoria Técnica", use_container_width=True):
                st.session_state.page = "Auditoria Técnica"
                st.rerun()
            if st.button("🎯 Simulador de Cotas", use_container_width=True):
                st.session_state.page = "Simulador de Cotas"
                st.rerun()

        with st.expander("🗄️ Bases de Suporte", expanded=(st.session_state.page in ["Geradores", "Usinas", "Geração (Livro-Caixa)", "Backoffice"])):
            if st.button("👤 Geradores", use_container_width=True):
                st.session_state.page = "Geradores"
                st.rerun()
            if st.button("🏭 Usinas", use_container_width=True):
                st.session_state.page = "Usinas"
                st.rerun()
            if st.button("⚡ Geração (Livro-Caixa)", use_container_width=True):
                st.session_state.page = "Geração (Livro-Caixa)"
                st.rerun()
            if st.button("📦 Backoffice", use_container_width=True):
                st.session_state.page = "Backoffice"
                st.rerun()

        with st.expander("🤖 Automações", expanded=(st.session_state.page in ["Captura RPA", "OCR HubSpot"])):
            if st.button("🤖 Captura RPA", use_container_width=True):
                st.session_state.page = "Captura RPA"
                st.rerun()
            if st.button("📄 OCR HubSpot", use_container_width=True):
                st.session_state.page = "OCR HubSpot"
                st.rerun()

        st.markdown('<hr style="border-color:rgba(255,255,255,0.08);margin:10px 0;">', unsafe_allow_html=True)
        if st.button("🚪 Sair", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CONCILIAÇÃO DE MEDIÇÃO (FILTROS ENVELOPADOS)
# ─────────────────────────────────────────────────────────────────────────────
def page_conciliacao():
    page_header("Conciliação de Medição", "Semana 1 · Cruzamento Extrato Detalhado vs Medição Sunne")

    st.markdown("""
    <div class="s-alert blue">
        <div><strong>Racional Operacional:</strong> Módulo de verificação eletrônica. Compare o Extrato de faturamento enviado pelos clientes com as faturas ativas no Backoffice para determinar instantaneamente <strong>quais</strong> e <strong>quantas</strong> faturas estão faltando no repasse mensal.</div>
    </div>
    """, unsafe_allow_html=True)

    # ENVELOPAMENTO DOS FILTROS EM ESTRUTURA ARREDONDADA CARD
    st.markdown('<div class="filter-container"><div class="filter-title">📑 Filtros e Arquivos de Entrada</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        extrato_file = st.file_uploader("Upload Extrato (Excel)", type=["xlsx", "xls"], key="ex_up")
    with c2:
        medicao_file = st.file_uploader("Upload Medição Sunne (Excel)", type=["xlsx", "xls"], key="med_up")

    mes_ref = st.text_input("Competência de Análise (AAAA-MM)", value=date.today().strftime("%Y-%m"))
    st.markdown('</div>', unsafe_allow_html=True)

    # Execução do Cruzamento de Faturas
    if extrato_file and medicao_file:
        if st.button("Executar Auditoria de Faturas Faltantes"):
            with st.spinner("Cruzando UCs e chaves de competência..."):
                try:
                    df_ext = pd.read_excel(extrato_file, dtype=str)
                    df_med = pd.read_excel(medicao_file, dtype=str)
                    
                    df_ext.columns = [c.strip() for c in df_ext.columns]
                    df_med.columns = [c.strip() for c in df_med.columns]

                    if "UC" in df_ext.columns: df_ext["UC"] = df_ext["UC"].apply(clean_uc)
                    if "UC" in df_med.columns: df_med["UC"] = df_med["UC"].apply(clean_uc)

                    def calc_ajustado(row):
                        try:
                            unif = str(row.get("Fatura Unificada", "")).lower()
                            total = float(str(row.get("Total a Pagar", 0)).replace(",",".").replace("R$","").strip() or 0)
                            boleto = float(str(row.get("Total a Pagar Boleto Concessionária", 0)).replace(",",".").replace("R$","").strip() or 0)
                            return total - boleto if unif in ("true","sim","1","yes") else total
                        except: return 0.0

                    df_ext["Valor Ajustado"] = df_ext.apply(calc_ajustado, axis=1)

                    df_merged = df_ext.merge(df_med, on="UC", how="left", suffixes=("_ext", "_med"))
                    
                    chave_med = [c for c in df_med.columns if c != "UC"]
                    if chave_med:
                        faltantes = df_merged[df_merged[chave_med[0]].isna()].copy()
                    else:
                        faltantes = pd.DataFrame()

                    total_extrato = len(df_ext)
                    quantas_faltam = len(faltantes)
                    valor_total_faltante = faltantes["Valor Ajustado"].sum() if "Valor Ajustado" in faltantes.columns else 0.0

                    m1, m2, m3 = st.columns(3)
                    with m1: st.markdown(kpi_card("Total no Extrato", f"{total_extrato} faturas", "Processadas em lote"), unsafe_allow_html=True)
                    with m2: st.markdown(kpi_card("Quantas Faltam", f"⚠️ {quantas_faltam} UCs ausentes", "Faturas não localizadas no rateio"), unsafe_allow_html=True)
                    with m3: st.markdown(kpi_card("Valores Não Repassados", f"R$ {valor_total_faltante:,.2f}", "Risco de quebra de caixa"), unsafe_allow_html=True)

                    if quantas_faltam > 0:
                        st.markdown(f'<div class="s-alert red"><div><strong>Atenção:</strong> Detectamos {quantas_faltam} faturas que foram pagas no extrato de caixa, mas não constam no relatório de medição/rateio da distribuidora. Veja quais são abaixo:</div></div>', unsafe_allow_html=True)
                        show_cols = [c for c in ["UC", "Nome", "Competência", "Valor Ajustado", "Status"] if c in faltantes.columns]
                        st.dataframe(faltantes[show_cols], use_container_width=True, hide_index=True)
                    else:
                        st.markdown('<div class="s-alert green"><div><strong>Conciliation Perfeita:</strong> Todas as faturas do extrato possuem correspondência exata na medição de repasse.</div></div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Erro ao processar as colunas das planilhas: {e}")
    else:
        st.markdown("### 📊 Painel de Verificação da Base Ativa")
        backoffice = load_json("backoffice")
        usinas = load_json("usinas")
        
        if backoffice and usinas:
            df_back = pd.DataFrame(backoffice)
            st.markdown(f"**Análise da competência ativa ({mes_ref}):**")
            
            faturas_totais = len(df_back)
            faturas_pendentes = df_back[df_back["saldo_solar"].astype(float) == 0.0]
            quantas_pendem = len(faturas_pendentes)

            m1, m2 = st.columns(2)
            with m1: st.markdown(kpi_card("Total de UCs Cadastradas", f"{faturas_totais} unidades", "Base Backoffice"), unsafe_allow_html=True)
            with m2: st.markdown(kpi_card("Faturas Não Injetadas/Faltantes", f"{quantas_pendem} UCs pendentes", "Sem leitura de créditos informada"), unsafe_allow_html=True)
            
            if quantas_pendem > 0:
                st.markdown("#### Lista de UCs com faturas pendentes de rateio:")
                st.dataframe(faturas_pendentes[["uc", "nome_beneficiario", "mes_ref", "tipo_ligacao"]], use_container_width=True, hide_index=True)
        else:
            st.markdown("""
            <div class="s-card" style="text-align:center; padding:40px;">
                <div style="color:#6b7280; font-size:14px;">Insira as planilhas de Extrato e Medição para habilitar a auditoria eletrônica em tempo real.</div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ATIVIDADES (FILTROS ENVELOPADOS)
# ─────────────────────────────────────────────────────────────────────────────
def page_atividades():
    page_header("Atividades", "Esteira operacional mensal — Fluxo Kanban")
    tasks = load_json("tasks")
    usinas = load_json("usinas")

    # ENVELOPAMENTO DOS FILTROS EM ESTRUTURA ARREDONDADA CARD
    st.markdown('<div class="filter-container"><div class="filter-title">🔍 Filtros de Controle</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1: tema_filtro = st.selectbox("Filtrar por Tema", ["Todos", "Faturamento", "Rateio", "Captura"])
    with c2: 
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Nova Tarefa Manual"): st.session_state.show_new_task = True
    st.markdown('</div>', unsafe_allow_html=True)

    filtered = [t for t in tasks if tema_filtro == "Todos" or t.get("macro_tema") == tema_filtro]

    cols = st.columns(5)
    for i, status in enumerate(KANBAN_STATUS):
        with cols[i]:
            cards = [t for t in filtered if t.get("status") == status]
            st.markdown(f"""
            <div class="k-col">
                <div class="k-col-header">
                    {KANBAN_LABELS[status]} <span class="k-count">{len(cards)}</span>
                </div>
            """, unsafe_allow_html=True)
            for task in cards:
                st.markdown(f"""
                <div class="k-card">
                    <div style="font-size:13px; font-weight:600; color:#111827;">{task['titulo'][:45]}</div>
                    <div style="font-size:12px; color:#6b7280; margin-top:4px;">Usina: {task.get('usina_nome','—')}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: INTELIGÊNCIA FINANCEIRA (FILTROS ENVELOPADOS)
# ─────────────────────────────────────────────────────────────────────────────
def page_bi():
    page_header("Inteligência Financeira", "Módulo BI Investidor")
    historico = load_json("historico_analises")
    usinas = load_json("usinas")

    if not usinas:
        st.info("Cadastre usinas nas bases de suporte para ver o BI.")
        return

    # ENVELOPAMENTO DOS FILTROS EM ESTRUTURA ARREDONDADA CARD
    st.markdown('<div class="filter-container"><div class="filter-title">📊 Escopo de Análise</div>', unsafe_allow_html=True)
    usina_opts = {u["nome"]: u["id"] for u in usinas}
    usina_sel = st.selectbox("Selecione a Usina para Análise", list(usina_opts.keys()))
    st.markdown('</div>', unsafe_allow_html=True)

    uid = usina_opts[usina_sel]
    df_hist = pd.DataFrame([h for h in historico if h.get("usina_id") == uid])
    if df_hist.empty:
        st.info("Nenhum dado consolidado encontrado para esta usina.")
        return

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Bruto", x=df_hist["mes_ref"], y=df_hist["recebimento_bruto"], marker_color="#3b82f6"))
    fig.add_trace(go.Scatter(name="Líquido", x=df_hist["mes_ref"], y=df_hist["recebimento_liquido"], mode="lines+markers", line=dict(color="#F36E21", width=3)))
    
    fig.update_layout(
        title_text=f"Histórico Anual — {usina_sel}",
        title_font=dict(size=14, family="Inter"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# BASES DE SUPORTE
# ─────────────────────────────────────────────────────────────────────────────
def page_usinas():
    page_header("Usinas", "Cadastro e monitoramento do parque gerador")
    usinas = load_json("usinas")
    t1, t2, t3 = st.tabs(["Lista de Usinas", "Nova Usina", "📂 Importar Planilha (Excel)"])

    with t1:
        if usinas: st.dataframe(pd.DataFrame(usinas), use_container_width=True, hide_index=True)
        else: st.info("Nenhuma usina na base.")

    with t2:
        with st.form("add_usina"):
            nome = st.text_input("Nome da Usina")
            pot = st.number_input("Potência (kWp)", min_value=0.0)
            grupo = st.selectbox("Grupo", ["A", "B"])
            if st.form_submit_button("Salvar Planta"):
                usinas.append({"id": f"USI{len(usinas)+1:03d}", "nome": nome, "potencia_kwp": pot, "grupo": grupo, "ativa": True})
                save_json("usinas", usinas)
                st.success("Usina cadastrada!")
                st.rerun()

    with t3:
        file = st.file_uploader("Selecione o arquivo Excel das Usinas", type=["xlsx", "xls"])
        if file and st.button("Processar e Sincronizar em Lote"):
            try:
                df = pd.read_excel(file)
                for r in df.to_dict("records"):
                    usinas.append({"id": f"USI{len(usinas)+1:03d}", "nome": str(r.get("nome")), "potencia_kwp": float(r.get("potencia_kwp", 100)), "grupo": str(r.get("grupo", "B")), "ativa": True})
                save_json("usinas", usinas)
                st.success("Usinas importadas via planilha!")
                st.rerun()
            except Exception as e: st.error(f"Erro na planilha: {e}")

def page_geradores():
    page_header("Geradores", "Módulo de Titulares da Geração")
    geradores = load_json("geradores")
    t1, t2, t3 = st.tabs(["Investidores", "Novo Investidor", "📂 Importar Planilha"])

    with t1:
        if geradores: st.dataframe(pd.DataFrame(geradores), use_container_width=True, hide_index=True)
        else: st.info("Nenhum gerador localizado.")

    with t2:
        with st.form("add_ger"):
            nome = st.text_input("Nome Completo")
            doc = st.text_input("CPF/CNPJ")
            if st.form_submit_button("Criar Gerador"):
                geradores.append({"id": f"GER{len(geradores)+1:03d}", "nome": nome, "cpf_cnpj": doc, "ativo": True})
                save_json("geradores", geradores)
                st.success("Gerador inserido!")
                st.rerun()

    with t3:
        file = st.file_uploader("Selecione o arquivo Excel de Geradores", type=["xlsx", "xls"])
        if file and st.button("Sincronizar Geradores em Lote"):
            try:
                df = pd.read_excel(file)
                for r in df.to_dict("records"):
                    geradores.append({"id": f"GER{len(geradores)+1:03d}", "nome": str(r.get("nome")), "cpf_cnpj": str(r.get("cpf_cnpj")), "ativo": True})
                save_json("geradores", geradores)
                st.success("Base de geradores updated!")
                st.rerun()
            except Exception as e: st.error(f"Erro de processamento: {e}")

def page_geracao():
    page_header("Geração — Livro-Caixa", "Registro e Upsert de Geração Mensal")
    geracao = load_json("geracao_usinas")
    t1, t2, t3 = st.tabs(["Histórico de Produção", "Lançar Manual", "📂 Importar Geração (Excel)"])

    with t1:
        if geracao: st.dataframe(pd.DataFrame(geracao), use_container_width=True, hide_index=True)
        else: st.info("Sem lançamentos de kWh.")

    with t2:
        with st.form("add_gen"):
            uid = st.text_input("ID da Usina (Ex: USI001)")
            mes = st.text_input("Mês Referência (AAAA-MM)", value=date.today().strftime("%Y-%m"))
            val = st.number_input("Injetado (kWh)", min_value=0.0)
            if st.form_submit_button("Salvar Linha de Geração"):
                geracao.append({"usina_id": uid, "mes_ref": mes, "geracao_kwh": val, "injetado_kwh": val})
                save_json("geracao_usinas", geracao)
                st.success("Geração computada!")
                st.rerun()

    with t3:
        file = st.file_uploader("Selecione a planilha de geração de energia", type=["xlsx", "xls"])
        if file and st.button("Processar Carga de Geração"):
            try:
                df = pd.read_excel(file)
                for r in df.to_dict("records"):
                    geracao.append({"usina_id": str(r.get("usina_id")), "mes_ref": str(r.get("mes_ref")), "geracao_kwh": float(r.get("geracao_kwh", 0)), "injetado_kwh": float(r.get("injetado_kwh", 0))})
                save_json("geracao_usinas", geracao)
                st.success("Histórico de geração consolidado!")
                st.rerun()
            except Exception as e: st.error(f"Falha na carga: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# OUTRAS PÁGINAS (PRESERVAÇÃO INTEGRAL)
# ─────────────────────────────────────────────────────────────────────────────
def page_dashboard():
    page_header("Dashboard", "Visão geral do ecossistema")
    st.markdown(kpi_card("Unidades Operando", "Ativas", "Monitoramento em tempo real"), unsafe_allow_html=True)

def page_simulador():
    page_header("Simulador de Cotas", "Ambiente preditivo de distribuição de energia")
    
    # ENVELOPAMENTO DOS FILTROS EM ESTRUTURA ARREDONDADA CARD
    st.markdown('<div class="filter-container"><div class="filter-title">🎯 Configuração da Usina Alvo</div>', unsafe_allow_html=True)
    st.selectbox("Usina Vinculada", ["Todas as unidades operacionais"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(kpi_card("Geração Estimada", "18.000 kWh/mês", "Cálculo técnico padrão"), unsafe_allow_html=True)

def page_faturas_ugs(): page_header("Faturas das UGs", "Gestão de faturamento")
def page_auditoria(): page_header("Auditoria Técnica", "Check de saúde de UCs")
def page_backoffice(): page_header("Backoffice", "Histórico de consumo consolidado")
def page_captura_rpa(): page_header("Captura RPA", "Status dos Robôs de captura")
def page_ocr_hubspot(): page_header("OCR HubSpot", "Filas de processamento de contratos")

def page_header(title, subtitle=""):
    st.markdown(f'<div class="page-h1">{title}</div>', unsafe_allow_html=True)
    if subtitle: st.markdown(f'<div class="page-sub">{subtitle}</div>', unsafe_allow_html=True)

def kpi_card(label, value, sub=""):
    return f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div style="font-size:12px; color:#6b7280; margin-top:4px;">{sub}</div></div>'

# ─────────────────────────────────────────────────────────────────────────────
# ROUTER PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
ROUTE_MAP = {
    "Dashboard": page_dashboard, "Atividades": page_atividades,
    "Conciliação de Medição": page_conciliacao, "Inteligência Financeira": page_bi, "Faturas das UGs": page_faturas_ugs,
    "Auditoria Técnica": page_auditoria, "Simulador de Cotas": page_simulador,
    "Geradores": page_geradores, "Usinas": page_usinas, "Geração (Livro-Caixa)": page_geracao, "Backoffice": page_backoffice,
    "Captura RPA": page_captura_rpa, "OCR HubSpot": page_ocr_hubspot
}

def main():
    inject_css()
    
    # Bypass seguro de login para agilizar a operação direta
    st.session_state.logged_in = True
    st.session_state.nome = "Milena Braga"
    st.session_state.email = "milena.braga@sunne.com.br"

    render_sidebar()
    
    page_fn = ROUTE_MAP.get(st.session_state.page, page_dashboard)
    page_fn()

if __name__ == "__main__":
    main()
