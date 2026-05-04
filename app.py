import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURAÇÃO DE TELA
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

# 2. DESIGN PREMIUM (PRETO E DOURADO)
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    .stSidebar { background-color: #050505 !important; border-right: 1px solid #D4AF37; }
    .stExpander { border: 1px solid #D4AF37 !important; background-color: #0A0A0A !important; border-radius: 10px; }
    h1, h2, h3 { color: #D4AF37 !important; }
    p { color: #FFFFFF; }
    </style>
    """, unsafe_allow_html=True)

def limpar_valor(valor):
    try:
        if isinstance(valor, str):
            v = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(v)
        return float(valor)
    except: return 0.0

# 3. CONEXÃO
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Leitura da aba fluxo
    df_bruto = conn.read(worksheet="fluxo", ttl=0) 
    df_bruto.columns = df_bruto.columns.astype(str).str.strip().str.lower()
    
    # Tratamento de dados
    df_bruto = df_bruto[df_bruto['aluno'].notna()]
    if 'valor mensal' in df_bruto.columns:
        df_bruto['valor mensal'] = df_bruto['valor mensal'].apply(limpar_valor)

    # --- MENU LATERAL ---
    st.sidebar.title("🏆 TEAM MUNIZ")
    
    if 'mês' in df_bruto.columns:
        lista_meses = df_bruto['mês'].unique().tolist()
        mes_escolhido = st.sidebar.selectbox("Selecione o Mês", lista_meses)
        df = df_bruto[df_bruto['mês'] == mes_escolhido]
    else:
        st.error("Coluna 'Mês' não encontrada.")
        st.stop()

    st.title(f"📊 Painel Financeiro • {mes_escolhido.upper()}")

    # --- CAMADA 1: MÉTRICAS ---
    total = df['valor mensal'].sum()
    pago_df = df[df['status'].str.contains('pago', na=False, case=False)]
    pendente_df = df[~df['status'].str.contains('pago', na=False, case=False)]
    
    pago_total = pago_df['valor mensal'].sum()
    pendente_total = total - pago_total

    m1, m2, m3 = st.columns(3)
    m1.metric("Faturamento Total", f"R$ {total:,.2f}")
    m2.metric("Recebido", f"R$ {pago_total:,.2f}")
    m3.metric("Pendente", f"R$ {pendente_total:,.2f}")

    st.markdown("---")
    
    # --- CAMADA 2: RELATÓRIO DE PAGAMENTOS POR DIA (NOVO) ---
    with st.expander("📅 RELATÓRIO DE ENTRADAS POR DIA", expanded=False):
        if 'dia' in df.columns:
            # Agrupa os valores por dia e ordena
            relatorio_dia = df.groupby('dia')['valor mensal'].sum().reset_index()
            relatorio_dia = relatorio_dia.sort_values('dia')
            
            for _, row in relatorio_dia.iterrows():
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; border-bottom: 1px solid #333; padding: 5px 0;'>
                    <span style='color: #FFFFFF;'>Dia {int(row['dia'])}</span>
                    <span style='color: #D4AF37; font-weight: bold;'>R$ {row['valor mensal']:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("Coluna 'Dia' não encontrada.")

    # --- CAMADA 3: LISTAS DE ALUNOS ---
    c_pend, c_pago = st.columns(2)
    
    with c_pend:
        with st.expander("❌ LISTA DE PENDENTES", expanded=True):
            if pendente_df.empty:
                st.write("✅ Tudo pago!")
            else:
                for _, row in pendente_df.iterrows():
                    st.write(f"🔴 {row['aluno']} - R$ {row['valor mensal']:.2f} (Dia {row['dia']})")

    with c_pago:
        with st.expander("✅ LISTA DE PAGOS"):
            if pago_df.empty:
                st.write("Nenhum pagamento registrado.")
            else:
                for _, row in pago_df.iterrows():
                    st.write(f"🟢 {row['aluno']} - R$ {row['valor mensal']:.2f}")

except Exception as e:
    st.error(f"Erro: {e}")
