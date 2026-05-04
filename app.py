import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO E IDENTIDADE VISUAL
st.set_page_config(page_title="Team Muniz Business Intelligence", layout="wide", page_icon="📈")

# CSS para criar os cards coloridos e o visual escuro de BI
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    [data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 28px !important; }
    .card-receita { background-color: #1A2634; padding: 20px; border-radius: 10px; border-left: 5px solid #2E86AB; }
    .card-gasto { background-color: #2D1B1B; padding: 20px; border-radius: 10px; border-left: 5px solid #A63D40; }
    .card-lucro { background-color: #1B2D1B; padding: 20px; border-radius: 10px; border-left: 5px solid #4D9078; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'Arial'; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARREGAMENTO DE DADOS
def carregar_dados():
    try:
        url = st.secrets["LINK_PLANILHA"].replace("/edit?usp=sharing", "/export?format=csv")
        df = pd.read_csv(url, usecols=[0, 1, 2, 3, 4, 5, 6])
        df.columns = ['aluno', 'valor', 'dia', 'status', 'pacote', 'mes', 'tipo']
        return df
    except: return None

df_bruto = carregar_dados()

if df_bruto is not None:
    # Tratamento
    df_bruto = df_bruto.dropna(subset=['aluno'])
    df_bruto['mes'] = df_bruto['mes'].str.strip().str.lower()
    df_bruto['tipo'] = df_bruto['tipo'].str.strip().str.lower()
    
    def limpar_valor(x):
        try:
            if isinstance(x, str): return float(x.replace('R$', '').replace('.', '').replace(',', '.').strip())
            return float(x)
        except: return 0.0
    
    df_bruto['valor'] = df_bruto['valor'].apply(limpar_valor)

    # --- HEADER ---
    st.title("🏆 Análise de Receita e Margem • Team Muniz")
    
    # Filtro Principal no Topo (como no seu print)
    meses_disponiveis = df_bruto['mes'].unique().tolist()
    mes_selecionado = st.selectbox("Selecione o Mês para análise detalhada:", meses_lista := sorted(meses_disponiveis))

    # Dados Filtrados
    df_mes = df_bruto[df_bruto['mes'] == mes_selecionado].copy()
    rec_mes = df_mes[df_mes['tipo'].str.contains('receita', na=False)]
    gas_mes = df_mes[df_mes['tipo'].str.contains('gasto', na=False)]

    # --- LINHA 1: CARDS DE MÉTRICAS ---
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown('<div class="card-receita">', unsafe_allow_html=True)
        st.metric("Receita Operacional", f"R$ {rec_mes['valor'].sum():,.2f}")
        st.write(f"Mês Ref: {mes_selecionado.capitalize()}")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card-gasto">', unsafe_allow_html=True)
        st.metric("Despesas Totais", f"R$ {gas_mes['valor'].sum():,.2f}")
        st.write("Custo de Operação")
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="card-lucro">', unsafe_allow_html=True)
        lucro = rec_mes['valor'].sum() - gas_mes['valor'].sum()
        st.metric("Margem de Contribuição", f"R$ {lucro:,.2f}")
        st.write("Lucro Líquido Real")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 📈 Evolução Diária de Receitas")
    
    # --- LINHA 2: GRÁFICO DE EVOLUÇÃO (Estilo BI) ---
    if not rec_mes.empty:
        # Agrupa por dia para criar o gráfico de área
        graf_data = rec_mes.groupby('dia')['valor'].sum().reset_index()
        st.area_chart(graf_data.set_index('dia'), color="#D4AF37")

    # --- LINHA 3: TABELAS DETALHADAS ---
    st.markdown("---")
    col_ent, col_sai = st.columns(2)

    with col_ent:
        with st.expander(f"🔍 Detalhes de Entradas ({mes_selecionado.upper()})", expanded=False):
            st.table(rec_mes[['aluno', 'valor', 'status']].sort_values('valor', ascending=False))

    with col_sai:
        with st.expander(f"🔍 Detalhes de Saídas ({mes_selecionado.upper()})", expanded=False):
            if gas_mes.empty:
                st.info("Sem gastos registrados.")
            else:
                st.table(gas_mes[['aluno', 'valor']].sort_values('valor', ascending=False))

    # --- RODAPÉ COM RESUMO GERAL ---
    st.markdown("---")
    st.subheader("🎯 Resumo por Pacote")
    if not rec_mes.empty:
        pacotes = rec_mes.groupby('pacote')['valor'].sum().sort_values(ascending=False)
        st.bar_chart(pacotes, color="#2E86AB")

else:
    st.error("Não foi possível conectar à planilha. Verifique o LINK_PLANILHA nos Secrets.")
