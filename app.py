import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# Configuração visual e do navegador
st.set_page_config(page_title="MFIT Control", layout="wide", page_icon="💪")

# Conexão direta com a sua planilha
url = "https://docs.google.com/spreadsheets/d/1BkD7YetGCHdpCupoYDfJE_dOOM0o86s3nepNl75BJNI/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

def limpar_valor(valor):
    try:
        if isinstance(valor, str):
            v = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(v)
        return float(valor)
    except:
        return 0.0

try:
    # Lendo a aba de Maio da sua planilha
    df = conn.read(spreadsheet=url, worksheet="maio")
    
    # Tratamento de dados: remove espaços extras e limpa linhas vazias
    df.columns = df.columns.str.strip()
    df = df[df['Aluno'].notna()]
    df = df[~df['Aluno'].astype(str).str.contains('vaga', case=False)]
    df['Valor mensal'] = df['Valor mensal'].apply(limpar_valor)

    st.title("🚀 MFIT • Painel de Controle")
    st.markdown(f"### Gestão Mensal: Maio 2026")

    # --- MÉTRICAS DE RESUMO ---
    receita_total = df['Valor mensal'].sum()
    receita_paga = df[df['status'].astype(str).str.contains('pago', case=False, na=False)]['Valor mensal'].sum()
    pendente = receita_total - receita_paga

    m1, m2, m3 = st.columns(3)
    m1.metric("Faturamento Previsto", f"R$ {receita_total:,.2f}")
    m2.metric("Recebido", f"R$ {receita_paga:,.2f}")
    m3.metric("Pendente", f"R$ {pendente:,.2f}", delta_color="inverse")

    st.divider()

    # --- GRÁFICO DE ENTRADAS ---
    if 'Dia' in df.columns:
        st.subheader("📅 Previsão de Entradas (Por Dia)")
        fluxo = df.groupby('Dia')['Valor mensal'].sum().reset_index()
        fig = px.bar(fluxo, x='Dia', y='Valor mensal', 
                     text_auto='.2f', 
                     labels={'Dia': 'Dia do Vencimento', 'Valor mensal': 'Total R$'},
                     color_discrete_sequence=['#00CC96'])
        st.plotly_chart(fig, use_container_width=True)

    # --- LISTA DE ALUNOS E COBRANÇA ---
    st.subheader("📲 Gestão de Pagamentos")
    for _, row in df.iterrows():
        status_texto = str(row['status']).lower()
        cor_status = "✅" if 'pago' in status_texto else "🔴"
        
        with st.expander(f"{cor_status} {row['Aluno']} - R$ {row['Valor mensal']:.2f} (Dia {int(row['Dia'])})"):
            if 'pago' in status_texto:
                st.success(f"Pagamento de {row['Aluno']} confirmado.")
            else:
                st.warning(f"Aguardando pagamento do pacote: {row['Pacote']}")
                # Mensagem de cobrança automática
                msg = f"Olá {row['Aluno']}! Tudo bem? Notei que o pagamento do plano {row['Pacote']} (Vencimento Dia {int(row['Dia'])}) ainda não consta aqui. Qualquer dúvida estou à disposição!"
                link_whatsapp = f"https://wa.me/?text={msg.replace(' ', '%20')}"
                st.markdown(f"**[📩 Enviar Lembrete no WhatsApp]({link_whatsapp})**")

except Exception as e:
    st.error(f"Erro ao carregar dados. Verifique os nomes das colunas na planilha. Erro: {e}")
