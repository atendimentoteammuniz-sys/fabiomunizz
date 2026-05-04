import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DE TELA
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

# 2. DESIGN PREMIUM
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    h1, h2, h3 { color: #D4AF37 !important; }
    .stDataFrame { background-color: #0A0A0A; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNÇÃO DE CONEXÃO DIRETA (SEM BIBLIOTECAS EXTRAS)
def carregar_dados():
    # Pega o link dos secrets
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    # Transforma o link para formato de exportação CSV (Garante que não dê Erro 400)
    csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv&gid=0")
    # Lê os dados
    df = pd.read_csv(csv_url)
    return df

try:
    df_bruto = carregar_dados()
    
    # Padronização de Colunas (Baseado na sua tabela A até G)
    df_bruto.columns = ['aluno', 'valor', 'dia', 'status', 'pacote', 'mes', 'tipo']
    
    # Limpeza
    df_bruto = df_bruto.dropna(subset=['aluno'])
    df_bruto['mes'] = df_bruto['mes'].str.strip().str.lower()
    df_bruto['tipo'] = df_bruto['tipo'].str.strip().str.lower()

    def limpar_moeda(x):
        if isinstance(x, str):
            return float(x.replace('R$', '').replace('.', '').replace(',', '.').strip())
        return float(x)

    df_bruto['valor'] = df_bruto['valor'].apply(limpar_moeda)

    # --- SIDEBAR ---
    st.sidebar.title("🏆 TEAM MUNIZ")
    meses = sorted(df_bruto['mes'].unique().tolist())
    mes_ref = st.sidebar.selectbox("Selecione o Mês", meses)

    # Filtragem
    df_mes = df_bruto[df_bruto['mes'] == mes_ref].copy()
    receitas = df_mes[df_mes['tipo'] == 'receita']
    gastos = df_mes[df_mes['tipo'] == 'gasto']

    # --- DASHBOARD ---
    st.title(f"📊 Gestão Financeira • {mes_ref.upper()}")
    
    total_rec = receitas['valor'].sum()
    total_gas = gastos['valor'].sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("Faturamento", f"R$ {total_rec:,.2f}")
    m2.metric("Gastos", f"R$ {total_gas:,.2f}", delta_color="inverse")
    m3.metric("Lucro Líquido", f"R$ {total_rec - total_gas:,.2f}")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("💰 Receitas")
        st.dataframe(receitas[['aluno', 'valor', 'status', 'pacote']], use_container_width=True)

    with col_b:
        st.subheader("💸 Gastos")
        st.dataframe(gastos[['aluno', 'valor']], use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar: {e}")
    st.info("💡 Certifique-se de que a aba 'fluxo' é a primeira da planilha e que o link termina em /edit?usp=sharing")
