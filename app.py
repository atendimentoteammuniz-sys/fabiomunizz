import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. SETUP DE PÁGINA
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

# 2. ESTILO VISUAL
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    .stSidebar { background-color: #050505 !important; border-right: 1px solid #D4AF37; }
    .stExpander { border: 1px solid #D4AF37 !important; background-color: #0A0A0A !important; border-radius: 10px; }
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

# 3. CONEXÃO
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Lendo a aba fluxo - Usando ttl=0 para garantir dados novos
    df = conn.read(worksheet="fluxo", ttl=0)
    
    # Padronização agressiva de nomes de colunas
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    # Remove linhas onde o nome do aluno/item está vazio
    df = df.dropna(subset=[df.columns[0]])

    # --- SIDEBAR ---
    st.sidebar.title("🏆 TEAM MUNIZ")
    
    # Detecta a coluna de mês (independente de maiúscula/minúscula)
    col_mes = 'mês' if 'mês' in df.columns else 'mes'
    
    if col_mes in df.columns:
        lista_meses = sorted(df[col_mes].unique().tolist())
        mes_ref = st.sidebar.selectbox("Selecione o Mês", lista_meses)
        df_mes = df[df[col_mes] == mes_ref].copy()
    else:
        st.error("Coluna 'Mês' não encontrada na planilha.")
        st.stop()

    # --- PROCESSAMENTO DE VALORES ---
    # Tenta encontrar a coluna de valor
    col_valor = 'valor mensal' if 'valor mensal' in df.columns else df.columns[1]
    df_mes[col_valor] = df_mes[col_valor].apply(limpar_valor)

    # --- SEPARAÇÃO RECEITA VS GASTO ---
    col_tipo = 'tipo' if 'tipo' in df.columns else None
    
    if col_tipo:
        receitas_df = df_mes[df_mes[col_tipo].str.contains('receita', na=False, case=False)]
        gastos_df = df_mes[df_mes[col_tipo].str.contains('gasto|saida|saída', na=False, case=False)]
    else:
        receitas_df = df_mes
        gastos_df = pd.DataFrame(columns=df.columns)

    # --- DASHBOARD ---
    st.title(f"📊 Gestão Financeira • {mes_ref.upper()}")
    
    total_rec = receitas_df[col_valor].sum()
    total_gas = gastos_df[col_valor].sum()
    saldo = total_rec - total_gas

    m1, m2, m3 = st.columns(3)
    m1.metric("Receitas", f"R$ {total_rec:,.2f}")
    m2.metric("Gastos", f"R$ {total_gas:,.2f}", delta_color="inverse")
    m3.metric("Saldo Líquido", f"R$ {saldo:,.2f}")

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        with st.expander("💰 RECEITAS DETALHADAS", expanded=True):
            for _, r in receitas_df.iterrows():
                st.write(f"🟢 {r[df.columns[0]]}: R$ {r[col_valor]:.2f}")
    
    with c2:
        with st.expander("💸 GASTOS DETALHADOS", expanded=True):
            for _, g in gastos_df.iterrows():
                st.write(f"🔴 {g[df.columns[0]]}: R$ {g[col_valor]:.2f}")

except Exception as e:
    st.error(f"Erro na conexão: {e}")
    st.info("💡 Dica: Verifique se o seu link nos Secrets termina em 'edit?usp=sharing'.")
