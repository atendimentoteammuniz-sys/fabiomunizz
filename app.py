import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

# CSS PERSONALIZADO PRETO E DOURADO
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    .stSidebar { background-color: #050505 !important; border-right: 1px solid #D4AF37; }
    .stExpander { border: 1px solid #D4AF37 !important; background-color: #0A0A0A !important; border-radius: 10px; }
    h1, h2, h3 { color: #D4AF37 !important; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# CONEXÃO
conn = st.connection("gsheets", type=GSheetsConnection)

def limpar_valor(valor):
    try:
        if isinstance(valor, str):
            v = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(v)
        return float(valor)
    except: return 0.0

try:
    # Lendo a aba fluxo
    df_bruto = conn.read(worksheet="fluxo", ttl=0)
    df_bruto.columns = df_bruto.columns.astype(str).str.strip().str.lower()
    
    # Tratamento de dados
    df_bruto = df_bruto[df_bruto['aluno'].notna()]
    if 'valor mensal' in df_bruto.columns:
        df_bruto['valor mensal'] = df_bruto['valor mensal'].apply(limpar_valor)

    # --- MENU LATERAL ---
    st.sidebar.title("🏆 TEAM MUNIZ")
    st.sidebar.markdown("---")
    
    if 'mês' in df_bruto.columns:
        lista_meses = df_bruto['mês'].unique().tolist()
        mes_escolhido = st.sidebar.selectbox("📅 Selecione o Mês", lista_meses)
        df = df_bruto[df_bruto['mês'] == mes_escolhido]
    else:
        st.sidebar.error("Coluna 'Mês' não encontrada!")
        st.stop()

    st.title(f"📊 Gestão Financeira • {mes_escolhido.upper()}")

    # --- CAMADA 1: MÉTRICAS (PAINEL FIXO) ---
    total = df['valor mensal'].sum()
    pago_df = df[df['status'].str.contains('pago', na=False, case=False)]
    pendente_df = df[~df['status'].str.contains('pago', na=False, case=False)]
    
    pago_total = pago_df['valor mensal'].sum()
    pendente_total = total - pago_total

    m1, m2, m3 = st.columns(3)
    m1.metric("Faturamento Previsto", f"R$ {total:,.2f}")
    m2.metric("Total Recebido", f"R$ {pago_total:,.2f}")
    m3.metric("Total Pendente", f"R$ {pendente_total:,.2f}")

    st.markdown("---")

    # --- CAMADA 2: GRÁFICO ---
    with st.expander("📈 VER FLUXO DE CAIXA POR DIA"):
        if 'dia' in df.columns:
            df_dia = df.groupby('dia')['valor mensal'].sum().reset_index()
            df_dia = df_dia.sort_values('dia')
            fig = px.bar(df_dia, x='dia', y='valor mensal', 
                         color_discrete_sequence=['#D4AF37'],
                         template="plotly_dark",
                         labels={'dia': 'Dia do Vencimento', 'valor mensal': 'Total (R$)'})
            st.plotly_chart(fig, use_container_width=True)

    # --- CAMADA 3: LISTAS SEPARADAS ---
    col_pend, col_pag = st.columns(2)

    with col_pend:
        with st.expander("❌ PENDENTES", expanded=True):
            for _, row in pendente_df.iterrows():
                st.markdown(f"""
                <div style='border-left: 4px solid #FF4B4B; padding: 10px; margin-bottom: 8px; background-color: #1A1A1A;'>
                    <span style='color:white;'>🔴 {row['aluno']}</span><br>
                    <span style='color:#D4AF37;'>R$ {row['valor mensal']:.2f}</span> | Vence dia {row['dia']}
                </div>
                """, unsafe_allow_html=True)

    with col_pag:
        with st.expander("✅ PAGOS"):
            for _, row in pago_df.iterrows():
                st.markdown(f"🟢 **{row['aluno']}** - R$ {row['valor mensal']:.2f}")

except Exception as e:
    st.error(f"Erro de Conexão: {e}")
