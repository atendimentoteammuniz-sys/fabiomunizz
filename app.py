import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DE TELA
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

# 2. ESTILO PREMIUM PRETO E DOURADO
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    h1, h2, h3 { color: #D4AF37 !important; }
    .stDataFrame { background-color: #111111; border: 1px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNÇÃO DE CONEXÃO DIRETA (IGNORA ERRO 400)
def carregar_dados():
    try:
        # Puxa o link dos Secrets
        url_original = st.secrets["connections"]["gsheets"]["spreadsheet"]
        # Transforma o link para formato de exportação direta
        url_csv = url_original.replace("/edit?usp=sharing", "/export?format=csv")
        
        # Lê apenas as 7 colunas que você criou
        df = pd.read_csv(url_csv, usecols=[0, 1, 2, 3, 4, 5, 6])
        df.columns = ['aluno', 'valor', 'dia', 'status', 'pacote', 'mes', 'tipo']
        return df
    except Exception as e:
        st.error(f"Erro ao acessar planilha: {e}")
        return None

# 4. PROCESSAMENTO
df_bruto = carregar_dados()

if df_bruto is not None:
    # Limpeza de dados
    df_bruto = df_bruto.dropna(subset=['aluno'])
    df_bruto['mes'] = df_bruto['mes'].str.strip().str.lower()
    df_bruto['tipo'] = df_bruto['tipo'].str.strip().str.lower()

    def limpar_valor(x):
        try:
            if isinstance(x, str):
                return float(x.replace('R$', '').replace('.', '').replace(',', '.').strip())
            return float(x)
        except: return 0.0

    df_bruto['valor'] = df_bruto['valor'].apply(limpar_valor)

    # --- SIDEBAR ---
    st.sidebar.title("🏆 TEAM MUNIZ")
    meses_lista = sorted(df_bruto['mes'].unique().tolist())
    mes_ref = st.sidebar.selectbox("Selecione o Mês", meses_lista)

    # Filtros
    df_mes = df_bruto[df_bruto['mes'] == mes_ref].copy()
    receitas = df_mes[df_mes['tipo'].str.contains('receita', na=False)]
    gastos = df_mes[df_mes['tipo'].str.contains('gasto', na=False)]

    # --- DASHBOARD ---
    st.title(f"📊 Gestão Financeira • {mes_ref.upper()}")
    
    val_rec = receitas['valor'].sum()
    val_gas = gastos['valor'].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas (Entradas)", f"R$ {val_rec:,.2f}")
    col2.metric("Gastos (Saídas)", f"R$ {val_gas:,.2f}", delta_color="inverse")
    col3.metric("Saldo Líquido", f"R$ {val_rec - val_gas:,.2f}")

    st.markdown("---")

    # RELATÓRIO LADO A LADO
    left, right = st.columns(2)
    
    with left:
        st.subheader("💰 Lista de Receitas")
        st.dataframe(receitas[['aluno', 'valor', 'status', 'pacote']], use_container_width=True, hide_index=True)

    with right:
        st.subheader("💸 Lista de Gastos")
        st.dataframe(gastos[['aluno', 'valor']], use_container_width=True, hide_index=True)

    # HISTÓRICO POR DIA
    with st.expander("📅 Resumo de Entradas por Dia"):
        df_dia = receitas.groupby('dia')['valor'].sum().reset_index()
        for _, row in df_dia.iterrows():
            st.write(f"**Dia {int(row['dia'])}:** R$ {row['valor']:,.2f}")
