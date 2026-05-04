import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DE TELA
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

# 2. DESIGN PREMIUM (PRETO E DOURADO)
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

# 3. CONEXÃO ROBUSTA
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Lemos a planilha sem especificar worksheet aqui para evitar o Erro 400
    # O filtro da aba 'fluxo' é feito logo abaixo
    df_bruto = conn.read(ttl=0) 
    
    # Se a planilha lida não for a 'fluxo', tentamos forçar a busca pelo nome da aba
    if 'mês' not in [str(c).lower() for c in df_bruto.columns]:
        df_bruto = conn.read(worksheet="fluxo", ttl=0)

    df_bruto.columns = df_bruto.columns.astype(str).str.strip().str.lower()
    
    # Tratamento de dados
    df_bruto = df_bruto[df_bruto['aluno'].notna()]
    if 'valor mensal' in df_bruto.columns:
        df_bruto['valor mensal'] = df_bruto['valor mensal'].apply(limpar_valor)

    # --- MENU LATERAL ---
    st.sidebar.title("🏆 TEAM MUNIZ")
    
    if 'mês' in df_bruto.columns:
        lista_meses = df_bruto['mês'].unique().tolist()
        mes_escolhido = st.sidebar.selectbox("Selecione o Mês", lista_meses)
        df = df_bruto[df_bruto['mês'] == mes_escolhido]
    else:
        st.error("Coluna 'Mês' não encontrada. Verifique se a aba 'fluxo' é a primeira da planilha.")
        st.stop()

    st.title(f"📊 Painel Financeiro • {mes_escolhido.upper()}")

    # --- MÉTRICAS ---
    total = df['valor mensal'].sum()
    pago_df = df[df['status'].str.contains('pago', na=False, case=False)]
    pendente_df = df[~df['status'].str.contains('pago', na=False, case=False)]
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Faturamento Total", f"R$ {total:,.2f}")
    m2.metric("Recebido", f"R$ {pago_df['valor mensal'].sum():,.2f}")
    m3.metric("Pendente", f"R$ {total - pago_df['valor mensal'].sum():,.2f}")

    st.markdown("---")
    
    # --- CAMADAS ---
    with st.expander("📈 GRÁFICO DE ENTRADAS"):
        if 'dia' in df.columns:
            df_dia = df.groupby('dia')['valor mensal'].sum().reset_index()
            fig = px.bar(df_dia, x='dia', y='valor mensal', color_discrete_sequence=['#D4AF37'], template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

    c_pend, c_pago = st.columns(2)
    with c_pend:
        with st.expander("❌ LISTA DE PENDENTES", expanded=True):
            for _, row in pendente_df.iterrows():
                st.write(f"🔴 {row['aluno']} - R$ {row['valor mensal']:.2f}")

    with c_pago:
        with st.expander("✅ LISTA DE PAGOS"):
            for _, row in pago_df.iterrows():
                st.write(f"🟢 {row['aluno']} - R$ {row['valor mensal']:.2f}")

except Exception as e:
    st.error(f"Erro Crítico: {e}")
    st.info("Dica: Arraste a aba 'fluxo' para ser a primeira aba (à esquerda) no seu Google Sheets.")
