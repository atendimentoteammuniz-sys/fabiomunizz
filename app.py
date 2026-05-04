import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

# 2. ESTILO VISUAL PREMIUM
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    h1, h2, h3 { color: #D4AF37 !important; }
    .stDataFrame { background-color: #111111; border: 1px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNÇÃO DE CONEXÃO
def carregar_dados():
    try:
        # Puxa o link direto do segredo que você configurou
        url_original = st.secrets["LINK_PLANILHA"]
        # Transforma para link de download CSV
        url_csv = url_original.replace("/edit?usp=sharing", "/export?format=csv")
        
        # Lê as 7 colunas (A até G)
        df = pd.read_csv(url_csv, usecols=[0, 1, 2, 3, 4, 5, 6])
        df.columns = ['aluno', 'valor', 'dia', 'status', 'pacote', 'mes', 'tipo']
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

# 4. EXECUÇÃO
df_bruto = carregar_dados()

if df_bruto is not None:
    # Limpeza básica
    df_bruto = df_bruto.dropna(subset=['aluno'])
    df_bruto['mes'] = df_bruto['mes'].astype(str).str.strip().str.lower()
    df_bruto['tipo'] = df_bruto['tipo'].astype(str).str.strip().str.lower()

    def limpar_valor(x):
        try:
            if isinstance(x, str):
                return float(x.replace('R$', '').replace('.', '').replace(',', '.').strip())
            return float(x)
        except: return 0.0

    df_bruto['valor'] = df_bruto['valor'].apply(limpar_valor)

    # --- MENU LATERAL ---
    st.sidebar.title("🏆 TEAM MUNIZ")
    meses_lista = sorted(df_bruto['mes'].unique().tolist())
    mes_ref = st.sidebar.selectbox("Selecione o Mês", meses_lista)

    # Filtragem
    df_mes = df_bruto[df_bruto['mes'] == mes_ref].copy()
    receitas = df_mes[df_mes['tipo'].str.contains('receita', na=False)]
    gastos = df_mes[df_mes['tipo'].str.contains('gasto', na=False)]

    # --- DASHBOARD ---
    st.title(f"📊 Gestão Financeira • {mes_ref.upper()}")
    
    val_rec = receitas['valor'].sum()
    val_gas = gastos['valor'].sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("Faturamento", f"R$ {val_rec:,.2f}")
    m2.metric("Despesas", f"R$ {val_gas:,.2f}", delta_color="inverse")
    m3.metric("Lucro Líquido", f"R$ {val_rec - val_gas:,.2f}")

    st.markdown("---")

    # RELATÓRIOS
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("💰 Entradas")
        st.dataframe(receitas[['aluno', 'valor', 'status']], use_container_width=True, hide_index=True)
    with c2:
        st.subheader("💸 Saídas")
        if gastos.empty:
            st.info("Sem gastos registrados.")
        else:
            st.dataframe(gastos[['aluno', 'valor']], use_container_width=True, hide_index=True)

else:
    st.warning("Verifique se o LINK_PLANILHA foi adicionado corretamente nos Secrets.")
