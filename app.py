import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# CONFIGURAÇÃO DE TELA
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

# CONEXÃO
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # LER SEM ESPECIFICAR ABA PRIMEIRO PARA EVITAR O BAD REQUEST
    df_bruto = conn.read(ttl=0)
    
    # Se ele não encontrar a coluna 'Mês' na primeira aba, ele tenta forçar a aba 'fluxo'
    # mas usando um método de tratamento de erro
    try:
        if 'Mês' not in df_bruto.columns and 'mês' not in df_bruto.columns:
            df_bruto = conn.read(worksheet="fluxo", ttl=0)
    except:
        pass

    # Padronização total
    df_bruto.columns = df_bruto.columns.astype(str).str.strip().str.lower()
    df_bruto = df_bruto.dropna(subset=['aluno']) # Remove linhas vazias que causam erro 400
    
    if 'valor mensal' in df_bruto.columns:
        df_bruto['valor mensal'] = df_bruto['valor mensal'].apply(limpar_valor)

    # --- MENU LATERAL ---
    st.sidebar.title("🏆 TEAM MUNIZ")
    
    col_mes = 'mês' if 'mês' in df_bruto.columns else None
    
    if col_mes:
        lista_meses = sorted(df_bruto[col_mes].unique().tolist())
        mes_escolhido = st.sidebar.selectbox("Selecione o Mês", lista_meses)
        df = df_bruto[df_bruto[col_mes] == mes_escolhido]
    else:
        st.error("Coluna 'Mês' não encontrada. Verifique o cabeçalho da planilha.")
        st.stop()

    st.title(f"📊 Painel Financeiro • {mes_escolhido.upper()}")

    # --- MÉTRICAS ---
    total = df['valor mensal'].sum()
    pago_df = df[df['status'].str.contains('pago', na=False, case=False)]
    pendente_df = df[~df['status'].str.contains('pago', na=False, case=False)]
    
    pago_total = pago_df['valor mensal'].sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("Faturamento Total", f"R$ {total:,.2f}")
    m2.metric("Recebido", f"R$ {pago_total:,.2f}")
    m3.metric("Pendente", f"R$ {total - pago_total:,.2f}")

    st.markdown("---")
    
    # --- RELATÓRIO POR DIA ---
    with st.expander("📅 RELATÓRIO DE ENTRADAS POR DIA"):
        if 'dia' in df.columns:
            # Garante que 'dia' seja número para ordenar certo
            df['dia'] = pd.to_numeric(df['dia'], errors='coerce').fillna(0)
            relatorio_dia = df.groupby('dia')['valor mensal'].sum().reset_index()
            relatorio_dia = relatorio_dia.sort_values('dia')
            
            for _, row in relatorio_dia.iterrows():
                if row['valor mensal'] > 0:
                    st.markdown(f"**Dia {int(row['dia'])}:** R$ {row['valor mensal']:,.2f}")
                    st.divider()

    # --- LISTAS ---
    c_pend, c_pago = st.columns(2)
    with c_pend:
        with st.expander("❌ PENDENTES", expanded=True):
            for _, row in pendente_df.iterrows():
                st.write(f"🔴 {row['aluno']} - R$ {row['valor mensal']:.2f} (Dia {row['dia']})")

    with c_pago:
        with st.expander("✅ PAGOS"):
            for _, row in pago_df.iterrows():
                st.write(f"🟢 {row['aluno']} - R$ {row['valor mensal']:.2f}")

except Exception as e:
    st.error(f"Erro de Conexão: {e}")
