import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO VISUAL PREMIUM
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="💰")

# CSS para forçar o tema Preto e Dourado
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; } /* Cor Dourada */
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    .stButton>button { 
        background-color: #D4AF37; 
        color: black; 
        border-radius: 10px;
        border: none;
        width: 100%;
        font-weight: bold;
    }
    .stExpander { border: 1px solid #D4AF37 !important; background-color: #111111 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. PAINEL FIXO E SELEÇÃO DE MÊS
st.sidebar.title("🏆 Financeiro Team Muniz")
mes_selecionado = st.sidebar.selectbox("Selecione o Mês", ["maio", "junho", "julho"])
st.sidebar.markdown("---")
st.sidebar.write("Foco na estratégia, o esforço vira resultado.")

def limpar_valor(valor):
    try:
        if isinstance(valor, str):
            v = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(v)
        return float(valor)
    except: return 0.0

try:
    # Lendo a aba selecionada no botão lateral
    df = conn.read(worksheet=mes_selecionado, ttl=0)
    df.columns = df.columns.astype(str).str.strip().str.lower()

    # Tratamento de Dados
    df = df[df['aluno'].notna()]
    if 'valor mensal' in df.columns:
        df['valor mensal'] = df['valor mensal'].apply(limpar_valor)

    st.title(f"📊 Painel Geral: {mes_selecionado.capitalize()}")

    # --- CAMADA 1: RESUMO FIXO ---
    total = df['valor mensal'].sum() if 'valor mensal' in df.columns else 0
    pago_df = df[df['status'].str.contains('pago', na=False, case=False)] if 'status' in df.columns else pd.DataFrame()
    pendente_df = df[~df['status'].str.contains('pago', na=False, case=False)] if 'status' in df.columns else df
    
    pago_total = pago_df['valor mensal'].sum() if not pago_df.empty else 0
    pendente_total = total - pago_total

    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento Total", f"R$ {total:,.2f}")
    c2.metric("Total Recebido", f"R$ {pago_total:,.2f}")
    c3.metric("Total Pendente", f"R$ {pendente_total:,.2f}")

    st.markdown("---")

    # --- CAMADA 2: BOTÕES RETRÁTEIS (Expander) ---

    with st.expander("📈 VER GRÁFICO DE ENTRADAS (FLUXO DE CAIXA)"):
        if 'dia' in df.columns:
            fig = px.bar(df.groupby('dia')['valor mensal'].sum().reset_index(), 
                         x='dia', y='valor mensal', 
                         color_discrete_sequence=['#D4AF37'], # Dourado
                         template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

    col_pag, col_pend = st.columns(2)

    with col_pag:
        if st.checkbox("✅ VER PAGOS"):
            st.subheader("Lista de Alunos Adimplentes")
            for _, row in pago_df.iterrows():
                st.success(f"🟢 {row['aluno']} - R$ {row['valor mensal']:.2f}")

    with col_pend:
        if st.checkbox("❌ VER PENDENTES"):
            st.subheader("Lista de Cobrança")
            for _, row in pendente_df.iterrows():
                st.error(f"🔴 {row['aluno']} - R$ {row['valor mensal']:.2f} (Dia {row['dia']})")

except Exception as e:
    st.error(f"Erro ao carregar o mês {mes_selecionado}: {e}")
    st.info("Verifique se a aba com esse nome existe na sua planilha.")
