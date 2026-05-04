import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. SETUP
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

# 2. ESTILO
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    h1, h2, h3 { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXÃO (Com tratamento de erro manual)
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Tentativa de leitura direta da aba 'fluxo'
    # Adicionamos o 'usecols' para garantir que ele só peça pro Google as 7 primeiras colunas
    df = conn.read(
        worksheet="fluxo",
        ttl=0,
        usecols=[0, 1, 2, 3, 4, 5, 6]
    )

    if df is not None:
        # Renomeia para garantir que o código funcione independente do que está escrito no topo
        df.columns = ['aluno', 'valor', 'dia', 'status', 'pacote', 'mes', 'tipo']
        
        # Limpa espaços e converte para minúsculo para não dar erro de busca
        df = df.dropna(subset=['aluno'])
        df['mes'] = df['mes'].astype(str).str.strip().str.lower()
        df['tipo'] = df['tipo'].astype(str).str.strip().str.lower()

        # Sidebar
        st.sidebar.title("🏆 TEAM MUNIZ")
        meses = sorted(df['mes'].unique().tolist())
        mes_ref = st.sidebar.selectbox("Escolha o Mês", meses)

        # Filtros
        df_mes = df[df['mes'] == mes_ref].copy()
        
        def converter_moeda(x):
            try:
                if isinstance(x, str):
                    return float(x.replace('R$', '').replace('.', '').replace(',', '.').strip())
                return float(x)
            except: return 0.0

        df_mes['valor'] = df_mes['valor'].apply(converter_moeda)

        # Divisão
        rec = df_mes[df_mes['tipo'].contains('receita', na=False)]
        gas = df_mes[df_mes['tipo'].contains('gasto', na=False)]

        # Dashboard
        st.title(f"📊 Gestão • {mes_ref.upper()}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Receitas", f"R$ {rec['valor'].sum():,.2f}")
        col2.metric("Gastos", f"R$ {gas['valor'].sum():,.2f}", delta_color="inverse")
        col3.metric("Saldo", f"R$ {rec['valor'].sum() - gas['valor'].sum():,.2f}")

        st.markdown("---")
        ca, cb = st.columns(2)
        with ca:
            st.subheader("💰 Entradas")
            st.dataframe(rec[['aluno', 'valor', 'status', 'pacote']], use_container_width=True)
        with cb:
            st.subheader("💸 Saídas")
            st.dataframe(gas[['aluno', 'valor']], use_container_width=True)

except Exception as e:
    st.error(f"Erro de Comunicação com Google: {e}")
    st.info("💡 Isso acontece quando o Google bloqueia o acesso temporariamente.")
    st.markdown("""
    **Como destravar:**
    1. Vá no seu Google Sheets.
    2. No canto superior direito, clique em **Compartilhar**.
    3. Garanta que está como **'Qualquer pessoa com o link'** e como **'Leitor'**.
    4. Copie o link novamente e cole nos Secrets do Streamlit Cloud.
    """)
