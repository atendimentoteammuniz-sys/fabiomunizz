import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="Financeiro Team Muniz", layout="wide", page_icon="🏆")

# 2. DESIGN PREMIUM TEAM MUNIZ
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    .stSidebar { background-color: #050505 !important; border-right: 1px solid #D4AF37; }
    .stExpander { border: 1px solid #D4AF37 !important; background-color: #0A0A0A !important; border-radius: 10px; }
    h1, h2, h3 { color: #D4AF37 !important; }
    p, span { color: #FFFFFF; }
    </style>
    """, unsafe_allow_html=True)

def limpar_valor(valor):
    try:
        if isinstance(valor, str):
            v = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(v)
        return float(valor)
    except: return 0.0

# 3. CONEXÃO COM A ABA 'fluxo'
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Leitura da aba unificada
    df = conn.read(worksheet="fluxo", ttl=0)
    
    # Padronização de Colunas
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    # Limpeza: Remove linhas totalmente vazias e padroniza os meses
    df = df.dropna(subset=['aluno'])
    df['mês'] = df['mês'].str.strip().str.lower()
    
    # Processamento de Valores
    col_valor = 'valor mensal' if 'valor mensal' in df.columns else df.columns[1]
    df[col_valor] = df[col_valor].apply(limpar_valor)

    # --- SIDEBAR ---
    st.sidebar.title("🏆 TEAM MUNIZ")
    lista_meses = sorted(df['mês'].unique().tolist())
    mes_selecionado = st.sidebar.selectbox("Selecione o Mês", lista_meses)

    # Filtragem dos dados do mês
    df_mes = df[df['mês'] == mes_selecionado].copy()

    # --- SEPARAÇÃO DE RECEITAS E GASTOS ---
    # Filtra pela coluna 'tipo'
    receitas = df_mes[df_mes['tipo'].str.contains('receita', na=False, case=False)]
    gastos = df_mes[df_mes['tipo'].str.contains('gasto', na=False, case=False)]

    total_rec = receitas[col_valor].sum()
    total_gas = gastos[col_valor].sum()
    saldo_liquido = total_rec - total_gas

    # --- DASHBOARD ---
    st.title(f"📊 Gestão Mensal • {mes_selecionado.upper()}")

    m1, m2, m3 = st.columns(3)
    m1.metric("Faturamento (Receitas)", f"R$ {total_rec:,.2f}")
    m2.metric("Despesas (Gastos)", f"R$ {total_gas:,.2f}", delta_color="inverse")
    m3.metric("Lucro Líquido", f"R$ {saldo_liquido:,.2f}")

    st.markdown("---")

    # RELATÓRIO LADO A LADO
    c1, c2 = st.columns(2)

    with c1:
        with st.expander("💰 DETALHE DE RECEITAS", expanded=True):
            for _, r in receitas.iterrows():
                cor_status = "🟢" if "pago" in str(r['status']).lower() else "🟡"
                st.write(f"{cor_status} {r['aluno']} - R$ {r[col_valor]:.2f} ({r['pacote']})")

    with c2:
        with st.expander("💸 DETALHE DE GASTOS", expanded=True):
            if gastos.empty:
                st.write("Nenhum gasto registrado para este mês.")
            else:
                for _, g in gastos.iterrows():
                    st.write(f"🔴 {g['aluno']} - R$ {g[col_valor]:.2f}")

    # RESUMO DIÁRIO DE ENTRADAS
    with st.expander("📅 PREVISÃO DE ENTRADAS POR DIA"):
        if 'dia' in receitas.columns:
            # Converte 'dia' para número para ordenar corretamente
            receitas['dia'] = pd.to_numeric(receitas['dia'], errors='coerce')
            rel_dia = receitas.groupby('dia')[col_valor].sum().reset_index().sort_values('dia')
            for _, row in rel_dia.iterrows():
                st.markdown(f"**Dia {int(row['dia'])}:** R$ {row[col_valor]:.2f}")

except Exception as e:
    st.error(f"Erro ao processar: {e}")
    st.info("💡 Verifique se as colunas na planilha seguem exatamente a ordem: Aluno, Valor mensal, Dia, status, Pacote, Mês, Tipo.")
