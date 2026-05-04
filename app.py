import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO VISUAL PREMIUM
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

# Estilização CSS para Preto e Dourado
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

# 2. CONEXÃO E LIMPEZA
conn = st.connection("gsheets", type=GSheetsConnection)

def limpar_valor(valor):
    try:
        if isinstance(valor, str):
            v = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(v)
        return float(valor)
    except: return 0.0
try:
    # 1. Primeiro, tentamos ler a planilha sem especificar aba para testar a conexão
    # 2. Depois, forçamos a busca pela aba 'fluxo'
    df_bruto = conn.read(worksheet="fluxo", ttl=0)
    
    # Limpeza de colunas
    df_bruto.columns = df_bruto.columns.astype(str).str.strip().str.lower()
    
    # Tratamento de dados
    df_bruto = df_bruto[df_bruto['aluno'].notna()]
    if 'valor mensal' in df_bruto.columns:
        df_bruto['valor mensal'] = df_bruto['valor mensal'].apply(limpar_valor)

    # --- MENU LATERAL ---
    st.sidebar.title("🏆 TEAM MUNIZ")
    st.sidebar.markdown("### Estratégia e Resultado")
    
    if 'mês' in df_bruto.columns:
        # Pega os meses disponíveis e garante que 'maio' apareça antes de 'junho' se possível
        meses_disponiveis = df_bruto['mês'].unique().tolist()
        mes_escolhido = st.sidebar.selectbox("Selecione o Mês", meses_disponiveis)
        
        # Filtro de dados pelo mês
        df = df_bruto[df_bruto['mês'] == mes_escolhido]
    else:
        st.error("Erro: Coluna 'Mês' não encontrada na planilha.")
        st.stop()

    st.title(f"📊 Painel Financeiro • {mes_escolhido.upper()}")

    # --- CAMADA 1: MÉTRICAS TOTAIS (FIXO) ---
    total_previsto = df['valor mensal'].sum()
    pago_df = df[df['status'].str.contains('pago', na=False, case=False)]
    pendente_df = df[~df['status'].str.contains('pago', na=False, case=False)]
    
    pago_total = pago_df['valor mensal'].sum()
    pendente_total = total_previsto - pago_total

    m1, m2, m3 = st.columns(3)
    m1.metric("Faturamento Previsto", f"R$ {total_previsto:,.2f}")
    m2.metric("Recebido (Pix/Dinheiro)", f"R$ {pago_total:,.2f}")
    m3.metric("Aguardando Pagamento", f"R$ {pendente_total:,.2f}")

    st.markdown("---")

    # --- CAMADA 2: GRÁFICO DIÁRIO ---
    with st.expander("📈 ANÁLISE DE FLUXO POR DIA"):
        if 'dia' in df.columns:
            # Agrupa por dia para ver os picos de recebimento
            df_dia = df.groupby('dia')['valor mensal'].sum().reset_index()
            df_dia['dia'] = df_dia['dia'].astype(int)
            df_dia = df_dia.sort_values('dia')
            
            fig = px.bar(df_dia, x='dia', y='valor mensal',
                         labels={'dia': 'Dia do Vencimento', 'valor mensal': 'Total R$'},
                         color_discrete_sequence=['#D4AF37'],
                         template="plotly_dark")
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    # --- CAMADA 3: GESTÃO DE ALUNOS ---
    col_esq, col_dir = st.columns(2)

    with col_esq:
        with st.expander("❌ PENDENTES DESTE MÊS", expanded=True):
            if pendente_df.empty:
                st.write("✅ Todos os alunos estão em dia!")
            else:
                for _, row in pendente_df.iterrows():
                    st.markdown(f"""
                    <div style='border-left: 5px solid #FF4B4B; padding: 10px; margin-bottom: 5px; background-color: #1A1A1A;'>
                        <b style='color: #FFFFFF;'>{row['aluno']}</b><br>
                        <span style='color: #D4AF37;'>R$ {row['valor mensal']:.2f}</span> | Vence dia: {row['dia']}
                    </div>
                    """, unsafe_allow_html=True)

    with col_dir:
        with st.expander("✅ PAGAMENTOS CONFIRMADOS"):
            if pago_df.empty:
                st.write("Aguardando primeiros pagamentos...")
            else:
                for _, row in pago_df.iterrows():
                    st.markdown(f"🟢 **{row['aluno']}** - R$ {row['valor mensal']:.2f}")

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
