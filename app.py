import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

# ESTILO PREMIUM
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    .stSidebar { background-color: #050505 !important; border-right: 1px solid #D4AF37; }
    .stExpander { border: 1px solid #D4AF37 !important; background-color: #0A0A0A !important; }
    h1, h2, h3 { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

def limpar_valor(valor):
    try:
        if isinstance(valor, str):
            v = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(v)
        return float(valor)
    except: return 0.0

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # LENDO O INTERVALO NOMEADO (MUITO MAIS ESTÁVEL)
    # Se você ainda não nomeou, ele tentará ler a aba 'fluxo' filtrando as colunas
    df = conn.read(worksheet="fluxo", ttl=0)
    
    # Seleciona apenas as 7 colunas de dados para ignorar o resto da planilha
    df = df.iloc[:, :7]
    df.columns = ['aluno', 'valor', 'dia', 'status', 'pacote', 'mes', 'tipo']
    
    # Limpeza básica
    df = df.dropna(subset=['aluno'])
    df['mes'] = df['mes'].astype(str).str.strip().str.lower()
    df['tipo'] = df['tipo'].astype(str).str.strip().str.lower()
    df['valor'] = df['valor'].apply(limpar_valor)

    # --- SIDEBAR ---
    st.sidebar.title("🏆 TEAM MUNIZ")
    meses = sorted(df['mes'].unique().tolist())
    mes_ref = st.sidebar.selectbox("Escolha o Mês", meses)

    # Dados Filtrados
    df_mes = df[df['mes'] == mes_ref].copy()

    # Separação
    rec = df_mes[df_mes['tipo'].str.contains('receita', na=False)]
    gas = df_mes[df_mes['tipo'].str.contains('gasto', na=False)]

    t_rec, t_gas = rec['valor'].sum(), gas['valor'].sum()

    # --- DISPLAY ---
    st.title(f"📊 Gestão Team Muniz • {mes_ref.upper()}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento", f"R$ {t_rec:,.2f}")
    c2.metric("Gastos Fixos", f"R$ {t_gas:,.2f}", delta_color="inverse")
    c3.metric("Saldo Real", f"R$ {t_rec - t_gas:,.2f}")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        with st.expander("💰 RECEITAS", expanded=True):
            for _, r in rec.iterrows():
                st.write(f"🟢 {r['aluno']} - R$ {r['valor']:.2f}")

    with col_b:
        with st.expander("💸 GASTOS", expanded=True):
            for _, g in gas.iterrows():
                st.write(f"🔴 {g['aluno']} - R$ {g['valor']:.2f}")

except Exception as e:
    st.error(f"Erro: {e}")
    st.info("💡 Vá no Google Sheets e exclua todas as colunas vazias à direita da coluna G.")
