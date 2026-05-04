import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURAÇÃO DE PÁGINA E DESIGN PREMIUM
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stMetricValue"] { font-weight: bold; }
    .stSidebar { background-color: #050505 !important; border-right: 1px solid #D4AF37; }
    .stExpander { border: 1px solid #D4AF37 !important; background-color: #0A0A0A !important; border-radius: 10px; }
    h1, h2, h3 { color: #D4AF37 !important; }
    .stMetric { background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

def limpar_valor(valor):
    try:
        if isinstance(valor, str):
            v = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(v)
        return float(valor)
    except: return 0.0

# 2. CONEXÃO COM AS ABAS
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Lendo as duas fontes de dados
    df_receitas_bruto = conn.read(worksheet="fluxo", ttl=0)
    df_gastos_bruto = conn.read(worksheet="gastos", ttl=0)
    
    # Padronização de colunas para evitar erros de digitação
    df_receitas_bruto.columns = df_receitas_bruto.columns.astype(str).str.strip().str.lower()
    df_gastos_bruto.columns = df_gastos_bruto.columns.astype(str).str.strip().str.lower()

    # --- MENU LATERAL: SELEÇÃO DE MÊS ---
    st.sidebar.title("🏆 TEAM MUNIZ")
    meses_disponiveis = sorted(df_receitas_bruto['mês'].unique().tolist())
    mes_escolhido = st.sidebar.selectbox("Selecione o Mês para Relatório", meses_disponiveis)

    # Filtragem por mês
    df_rec = df_receitas_bruto[df_receitas_bruto['mês'] == mes_escolhido].copy()
    df_gas = df_gastos_bruto[df_gastos_bruto['mês'] == mes_escolhido].copy()

    # Tratamento Numérico
    df_rec['valor mensal'] = df_rec['valor mensal'].apply(limpar_valor)
    df_gas['valor'] = df_gas['valor'].apply(limpar_valor)

    st.title(f"📈 Relatório de Lucratividade • {mes_escolhido.upper()}")

    # --- CÁLCULO DO RELATÓRIO ---
    total_receitas = df_rec['valor mensal'].sum()
    total_gastos = df_gas['valor'].sum()
    lucro_real = total_receitas - total_gastos
    margem = (lucro_real / total_receitas) * 100 if total_receitas > 0 else 0

    # --- PAINEL FIXO DE MÉTRICAS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento (A)", f"R$ {total_receitas:,.2f}")
    c2.metric("Despesas (B)", f"R$ {total_gastos:,.2f}", delta_color="inverse")
    c3.metric("Lucro Líquido (A-B)", f"R$ {lucro_real:,.2f}")
    c4.metric("Margem de Lucro", f"{margem:.1f}%")

    st.markdown("---")

    # --- RELATÓRIO DETALHADO EM CAMADAS ---
    
    col_dir, col_esq = st.columns(2)

    with col_dir:
        with st.expander("💰 DETALHAMENTO DE RECEITAS", expanded=True):
            # Agrupado por tipo de pacote para visão estratégica
            if 'pacote' in df_rec.columns:
                resumo_pacote = df_rec.groupby('pacote')['valor mensal'].sum().reset_index()
                for _, r in resumo_pacote.iterrows():
                    st.write(f"**{r['pacote']}:** R$ {r['valor mensal']:,.2f}")
                st.divider()
            
            # Lista de alunos
            for _, row in df_rec.iterrows():
                status_icon = "🟢" if "pago" in str(row['status']).lower() else "🔴"
                st.write(f"{status_icon} {row['aluno']} - R$ {row['valor mensal']:.2f}")

    with col_esq:
        with st.expander("💸 DETALHAMENTO DE GASTOS", expanded=True):
            if df_gas.empty:
                st.info("Nenhum gasto fixo registrado para este mês.")
            else:
                for _, row in df_gas.iterrows():
                    st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #222;'>
                        <span>{row['item']}</span>
                        <span style='color: #FF4B4B;'>R$ {row['valor']:,.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f"<br><h4 style='text-align: right;'>Total Saídas: R$ {total_gastos:,.2f}</h4>", unsafe_allow_html=True)

    # --- CAMADA DE FLUXO DIÁRIO ---
    with st.expander("📅 RESUMO DE ENTRADAS POR DIA"):
        rel_dia = df_rec.groupby('dia')['valor mensal'].sum().reset_index().sort_values('dia')
        for _, row in rel_dia.iterrows():
            st.write(f"**Dia {int(row['dia'])}:** R$ {row['valor mensal']:,.2f}")

except Exception as e:
    st.error(f"Erro ao processar o relatório: {e}")
    st.info("Certifique-se de que a aba 'gastos' existe e as colunas estão corretas.")
