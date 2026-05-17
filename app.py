import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página do aplicativo
st.set_page_config(
    page_title="Team Muniz - Dashboard",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Premium (Preto, Branco e Dourado)
st.markdown("""
    <style>
    .main { background-color: #111111; color: #FFFFFF; }
    .sidebar .sidebar-content { background-color: #1A1A1A; }
    h1, h2, h3 { color: #D4AF37 !important; } /* Dourado */
    div.stButton > button:first-child {
        background-color: #D4AF37; color: #111111; font-weight: bold; border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# URL da sua planilha original convertida para exportação automática de CSV
URL_BASE = "https://docs.google.com/spreadsheets/d/1tqfyKLolU1P7AVOYw7vJcOtG19QOM9tSVu6OK09j668/export?format=csv&gid="

# GIDs REAIS identificados na sua planilha compartilhada
GIDS = {
    "Cadastro_Alunos": "1168521543",
    "Controle_Financeiro": "439294975",
    "Agendamento_Aulas": "1486576823",
    "Historico_Bioimpedancia": "2134988451",
    "Prescricao_Treinos": "1619478144",
    "Fluxo_Caixa_Geral": "1809059737"
}

@st.cache_data(ttl=30) # Atualiza o app a cada 30 segundos se houver mudança na planilha
def carregar_dados(aba_nome):
    url = URL_BASE + GIDS[aba_nome]
    try:
        df = pd.read_csv(url)
        # Limpeza básica de colunas vazias que o Sheets costuma exportar
        df = df.dropna(how='all')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a aba '{aba_nome}': {e}")
        return pd.DataFrame()

# --- MENU LATERAL ---
st.sidebar.title("🏆 Team Muniz App")
st.sidebar.write("---")
perfil = st.sidebar.radio("Escolha o Perfil:", ["👑 Treinador (Fábio)", "🏃 Área do Aluno"])

# --- VISÃO DO TREINADOR ---
if perfil == "👑 Treinador (Fábio)":
    st.title("Painel de Controle Executivo")
    
    menu_treinador = st.sidebar.selectbox(
        "Gerenciar:", 
        ["📊 Dashboard Geral", "💰 Financeiro Detalhado", "📅 Agenda de Atendimentos", "🏋️ Prescrição de Treinos"]
    )
    
    # Carregando bases essenciais
    df_alunos = carregar_dados("Cadastro_Alunos")
    df_financeiro = carregar_dados("Controle_Financeiro")
    df_agenda = carregar_dados("Agendamento_Aulas")

    # Tratamento de valores financeiros para cálculos numéricos
    if not df_financeiro.empty and 'Valor_Cobrado' in df_financeiro.columns:
        df_financeiro['Valor_Num'] = df_financeiro['Valor_Cobrado'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
    else:
        df_financeiro['Valor_Num'] = 0.0

    if menu_treinador == "📊 Dashboard Geral":
        st.subheader("Métricas em Tempo Real")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Alunos Ativos Cadastrados", len(df_alunos))
        with col2:
            faturamento_total = df_financeiro['Valor_Num'].sum()
            st.metric("Faturamento Previsto (Maio)", f"R$ {faturamento_total:,.2f}")
        with col3:
            st.metric("Horários Fixos na Agenda", len(df_agenda))
            
        st.write("---")
        st.subheader("Visualização Rápida da Base de Clientes")
        st.dataframe(df_alunos, use_container_width=True)

    elif menu_treinador == "💰 Financeiro Detalhado":
        st.subheader("Gestão de Receitas")
        
        # Gráfico simples de pizza/barra por status de pagamento
        if 'Status_Pagamento' in df_financeiro.columns:
            resumo_status = df_financeiro.groupby('Status_Pagamento')['Valor_Num'].sum()
            st.bar_chart(resumo_status)
            
        st.write("---")
        st.subheader("Lista de Cobranças")
        st.dataframe(df_financeiro[['Nome_Aluno', 'Mes_Referencia', 'Valor_Cobrado', 'Data_Vencimento', 'Status_Pagamento']], use_container_width=True)

    elif menu_treinador == "📅 Agenda de Atendimentos":
        st.subheader("Cronograma de Aulas Presenciais")
        
        # Mapeamento de dias para filtro amigável
        dias_semana = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
        dia_filtro = st.selectbox("Filtrar por dia da semana:", ["Todos"] + dias_semana)
        
        if dia_filtro != "Todos":
            agenda_filtrada = df_agenda[df_agenda['Data_Aula'] == dia_filtro]
        else:
            agenda_filtrada = df_agenda
            
        st.dataframe(agenda_filtrada[['Nome_Aluno', 'Data_Aula', 'Horario_Inicio', 'Horario_Fim', 'Observacoes_Agenda']], use_container_width=True)

    elif menu_treinador == "🏋️ Prescrição de Treinos":
        st.subheader("Central de Fichas de Exercícios")
        df_treinos = carregar_dados("Prescricao_Treinos")
        
        aluno_treino = st.selectbox("Selecione o aluno para ver/editar a ficha:", df_alunos['Nome_Completo'].tolist())
        treino_especifico = df_treinos[df_treinos['Nome_Aluno'] == aluno_treino]
        
        st.write(f"Exercícios atuais de: **{aluno_treino}**")
        st.dataframe(treino_especifico, use_container_width=True)

# --- VISÃO DO ALUNO ---
elif perfil == "🏃 Área do Aluno":
    st.title("Portal do Aluno - Team Muniz")
    
    df_alunos = carregar_dados("Cadastro_Alunos")
    
    if not df_alunos.empty:
        lista_nomes = df_alunos["Nome_Completo"].dropna().tolist()
        aluno_selecionado = st.selectbox("Quem está acessando?", lista_nomes)
        
        id_aluno = df_alunos[df_alunos["Nome_Completo"] == aluno_selecionado]["ID_Aluno"].values[0]
        
        aba_treino, aba_evolucao, aba_financeiro = st.tabs(["🏋️ Meu Treino", "📈 Minha Evolução", "💳 Meu Financeiro"])
        
        with aba_treino:
            st.subheader("Minha Ficha de Treino Ativa")
            df_treinos = carregar_dados("Prescricao_Treinos")
            treino_do_aluno = df_treinos[df_treinos["ID_Aluno"] == id_aluno]
            
            if not treino_do_aluno.empty and not treino_do_aluno["Nome_Exercicio"].isna().all():
                st.dataframe(treino_do_aluno.dropna(subset=['Nome_Exercicio']), use_container_width=True)
            else:
                st.info("Fábio está preparando sua nova periodização. Aguarde as instruções técnicas!")
                
        with aba_evolucao:
            st.subheader("Histórico de Avaliações Físicas")
            df_bio = carregar_dados("Historico_Bioimpedancia")
            bio_do_aluno = df_bio[df_bio["ID_Aluno"] == id_aluno]
            st.dataframe(bio_do_aluno, use_container_width=True)
            
        with aba_financeiro:
            st.subheader("Minhas Faturas")
            df_fin = carregar_dados("Controle_Financeiro")
            fin_do_aluno = df_fin[df_fin["ID_Aluno"] == id_aluno]
            st.dataframe(fin_do_aluno[["Mes_Referencia", "Valor_Cobrado", "Data_Vencimento", "Status_Pagamento"]], use_container_width=True)
