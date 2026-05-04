import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# CONFIGURAÇÃO DE TELA
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

# DESIGN PREMIUM PRETO E DOURADO
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

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # ESTRATÉGIA ANTI-ERRO 400: LER CADA ABA SEPARADAMENTE COM TRATAMENTO
    df_rec_bruto = conn.read(worksheet="fluxo", ttl=0)
    df_gas_bruto = conn.read(worksheet="gastos", ttl=0)

    # Padronização
    df_rec_bruto.columns = df_rec_bruto.columns.astype(str).str.strip().str.lower()
    df_gas_bruto.columns = df_gas_bruto.columns.astype(str).str.strip().str.lower()
    
    # Limpeza de linhas vazias
    df_rec_bruto = df_rec_bruto.dropna(subset=['aluno'])
    df_gas_bruto = df_gas_bruto.dropna(subset=['item'])

    # MENU LATERAL
    st.sidebar.title("🏆 TEAM MUNIZ")
    lista_meses = sorted(df_rec_bruto['mês'].unique().tolist())
    mes_selecionado = st.sidebar.selectbox("Escolha o Mês", lista_meses)

    # Filtragem e Cálculos
    df_rec = df_rec_bruto[df_rec_bruto['mês'] == mes_selecionado].copy()
    df_gas = df_gas_bruto[df_gas_bruto['mês'] == mes_selecionado].copy()

    df_rec['valor mensal'] = df_rec['valor mensal'].apply(limpar_valor)
    df_gas['valor'] = df_gas['valor'].apply(limpar_valor)

    st.title(f"📊 Relatório de Lucratividade • {mes_selecionado.upper()}")

    # --- CÁLCULO DE RESULTADO ---
    receita_total = df_rec['valor mensal'].sum()
    gastos_total = df_gas['valor'].sum()
    lucro_liquido = receita_total - gastos_total

    # PAINEL DE MÉTRICAS
    c1, c2, c3 = st.columns(3)
    c1.metric("Receita (Alunos)", f"R$ {receita_total:,.2f}")
    c2.metric("Gastos (Contas)", f"R$ {gastos_total:,.2f}", delta_color="inverse")
    c3.metric("Lucro Líquido", f"R$ {lucro_liquido:,.2f}")

    st.markdown("---")

    # RELATÓRIO EM CAMADAS
    with st.expander("📝 DETALHAMENTO DO BALANÇO MENSAL"):
        st.subheader("Receitas")
        for _, r in df_rec.iterrows():
            st.write(f"🟢 {r['aluno']}: R$ {r['valor mensal']:,.2f}")
        
        st.divider()
        
        st.subheader("Gastos Fixos")
        for _, g in df_gas.iterrows():
            st.write(f"🔴 {g['item']}: R$ {g['valor']:,.2f}")
            
        st.divider()
        st.markdown(f"### **Resultado Final: R$ {lucro_liquido:,.2f}**")

    # RELATÓRIO POR DIA (RECEITAS)
    with st.expander("📅 ENTRADAS POR DIA"):
        rel_dia = df_rec.groupby('dia')['valor mensal'].sum().reset_index().sort_values('dia')
        for _, row in rel_dia.iterrows():
            st.write(f"**Dia {int(row['dia'])}:** R$ {row['valor mensal']:,.2f}")

except Exception as e:
    st.error(f"Erro ao processar: {e}")
    st.info("Verifique se as abas 'fluxo' e 'gastos' estão escritas corretamente na planilha.")
