import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

# DESIGN PREMIUM
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
    # LENDO APENAS UMA ABA (MUITO MAIS SEGURO)
    df_bruto = conn.read(worksheet="fluxo", ttl=0)
    df_bruto.columns = df_bruto.columns.astype(str).str.strip().str.lower()
    df_bruto = df_bruto.dropna(subset=['aluno']) # Remove linhas vazias

    # TRATAMENTO DE VALORES
    valor_col = 'valor mensal' if 'valor mensal' in df_bruto.columns else df_bruto.columns[1]
    df_bruto[valor_col] = df_bruto[valor_col].apply(limpar_valor)

    # --- SIDEBAR ---
    st.sidebar.title("🏆 TEAM MUNIZ")
    lista_meses = sorted(df_bruto['mês'].unique().tolist())
    mes_ref = st.sidebar.selectbox("Selecione o Mês", lista_meses)

    # Filtragem por Mês
    df = df_bruto[df_bruto['mês'] == mes_ref].copy()

    # --- LÓGICA DE CÁLCULO (RECEITA VS GASTO) ---
    # Filtra as linhas baseado na coluna 'tipo'
    receitas_df = df[df['tipo'].str.contains('receita', na=False, case=False)]
    gastos_df = df[df['tipo'].str.contains('gasto', na=False, case=False)]

    total_receita = receitas_df[valor_col].sum()
    total_gasto = gastos_df[valor_col].sum()
    saldo_final = total_receita - total_gasto

    st.title(f"📊 Balanço Team Muniz • {mes_ref.upper()}")

    # PAINEL DE MÉTRICAS
    m1, m2, m3 = st.columns(3)
    m1.metric("Receita Total", f"R$ {total_receita:,.2f}")
    m2.metric("Gastos Totais", f"R$ {total_gasto:,.2f}", delta_color="inverse")
    m3.metric("Saldo Líquido", f"R$ {saldo_final:,.2f}")

    st.markdown("---")

    # RELATÓRIO DETALHADO
    col_rec, col_gas = st.columns(2)

    with col_rec:
        with st.expander("💰 RECEITAS (ALUNOS)", expanded=True):
            for _, r in receitas_df.iterrows():
                st.write(f"🟢 {r['aluno']} - R$ {r[valor_col]:.2f}")

    with col_gas:
        with st.expander("💸 GASTOS (CONTAS)", expanded=True):
            if gastos_df.empty:
                st.write("Nenhum gasto registrado para este mês.")
            else:
                for _, g in gastos_df.iterrows():
                    st.write(f"🔴 {g['aluno']} - R$ {g[valor_col]:.2f}")

    # FLUXO POR DIA
    with st.expander("📅 RECEBIMENTOS POR DIA"):
        if 'dia' in receitas_df.columns:
            rel_dia = receitas_df.groupby('dia')[valor_col].sum().reset_index().sort_values('dia')
            for _, row in rel_dia.iterrows():
                st.write(f"**Dia {int(row['dia'])}:** R$ {row[valor_col]:.2f}")

except Exception as e:
    st.error(f"Erro de Processamento: {e}")
    st.info("⚠️ Verifique se a coluna 'tipo' foi criada na aba fluxo e se os nomes estão corretos.")
