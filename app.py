import streamlit as st
import pandas as pd

# Configuração da página do aplicativo
st.set_page_config(
    page_title="Team Muniz - Dashboard",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Premium (Preto e Dourado)
st.markdown("""
    <style>
    .main { background-color: #111111; color: #FFFFFF; }
    .sidebar .sidebar-content { background-color: #1A1A1A; }
    h1, h2, h3 { color: #D4AF37 !important; }
    div.stButton > button:first-child {
        background-color: #D4AF37; color: #111111; font-weight: bold; border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# URL base de exportação limpa
URL_BASE = "https://docs.google.com/spreadsheets/d/1tqfyKLolU1P7AVOYw7vJcOtG19QOM9tSVu6OK09j668/export?format=csv&gid="

# GIDs estritos retirados diretamente da sua planilha ativa
GIDS = {
    "Cadastro_Alunos": "1168521543",
    "Controle_Financeiro": "439294975",
    "Agendamento_Aulas": "1486576823",
    "Historico_Bioimpedancia": "2134988451",
    "Prescricao_Treinos": "1619478144",
    "Fluxo_Caixa_Geral": "1809059737"
}

@st.cache_data(ttl=5) # Cache agressivo de 5 segundos para atualizar quase em tempo real
def carregar_e_limpar_dados(aba_nome):
    url = URL_BASE + GIDS[aba_nome]
    try:
        df = pd.read_csv(url)
        # Corta linhas totalmente vazias que o Sheets gera no final
        df = df.dropna(how='all')
        
        # BLINDAGEM CRÍTICA: Remove asteriscos, barras invertidas e espaços dos nomes das colunas
        df.columns = df.columns.astype(str).str.replace(r'\\', '', regex=True)
        df.columns = df.columns.str.replace('*', '', regex=False)
        df.columns = df.columns.str.strip()
        
        return df
    except Exception as e:
        st.error(f"Erro de conexão na aba '{aba_nome}': {e}")
        return pd.DataFrame()

# --- CARREGAMENTO INICIAL DE TODAS AS BASES ---
df_alunos = carregar_e_limpar_dados("Cadastro_Alunos")
df_financeiro = carregar_e_limpar_dados("Controle_Financeiro")
df_agenda = carregar_e_limpar_dados("Agendamento_Aulas")
df_treinos = carregar_e_limpar_dados("Prescricao_Treinos")
df_bio = carregar_e_limpar_dados("Historico_Bioimpedancia")
df_caixa = carregar_e_limpar_dados("Fluxo_Caixa_Geral")

# --- TRATAMENTO DOS VALORES FINANCEIRES ---
if not df_financeiro.empty and 'Valor_Cobrado' in df_financeiro.columns:
    df_financeiro['Valor_Num'] = df_financeiro['Valor_Cobrado'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
else:
    df_financeiro['Valor_Num'] = 0.0

# --- MENU LATERAL ---
st.sidebar.title("🏆 Team Muniz App")
st.sidebar.write("---")
perfil = st.sidebar.radio("Escolha o Perfil:", ["👑 Treinador (Fábio)", "🏃 Área do Aluno"])

# ==========================================
# 👑 INTERFACE DO TREINADOR (FÁBIO)
# ==========================================
if perfil == "👑 Treinador (Fábio)":
    st.title("Painel de Controle Executivo")
    
    menu_treinador = st.sidebar.selectbox(
        "Gerenciar:", 
        ["📊 Dashboard Geral", "💰 Financeiro Detalhado", "📅 Agenda de Atendimentos", "🏋️ Prescrição de Treinos"]
    )
    
    # CORREÇÃO 1: MÓDULO DASHBOARD GERAL
    if menu_treinador == "📊 Dashboard Geral":
        st.subheader("Métricas em Tempo Real")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            # Conta estritamente as linhas da aba de Cadastro (Alunos reais)
            total_alunos = len(df_alunos) if not df_alunos.empty else 0
            st.metric("Alunos Ativos Cadastrados", total_alunos)
        with col2:
            # Soma real dos lançamentos financeiros
            faturamento_total = df_financeiro['Valor_Num'].sum() if 'Valor_Num' in df_financeiro.columns else 0.0
            st.metric("Faturamento Previsto (Maio)", f"R$ {faturamento_total:,.2f}")
        with col3:
            # Conta as linhas de agendamentos (Aulas marcadas)
            total_agendamentos = len(df_agenda) if not df_agenda.empty else 0
            st.metric("Aulas Presenciais Agendadas", total_agendamentos)
            
        st.write("---")
        # CORREÇÃO 2: Visualização Rápida puxando estritamente da aba de Cadastro
        st.subheader("Visualização Rápida da Base de Clientes (Cadastro)")
        if not df_alunos.empty:
            st.dataframe(df_alunos[['ID_Aluno', 'Nome_Completo', 'WhatsApp', 'Modalidade', 'Status_Aluno']], use_container_width=True)
        else:
            st.warning("Aba de Cadastro de Alunos não pôde ser lida ou está vazia.")

    # CORREÇÃO 3: MÓDULO FINANCEIRO DETALHADO
    elif menu_treinador == "💰 Financeiro Detalhado":
        st.subheader("Gestão de Receitas & Cobranças")
        
        if not df_financeiro.empty and 'Status_Pagamento' in df_financeiro.columns:
            # Gráfico de barras resumindo a grana por status (Pendente / Pago)
            resumo_status = df_financeiro.groupby('Status_Pagamento')['Valor_Num'].sum()
            st.bar_chart(resumo_status)
            
            st.write("---")
            st.subheader("Lista de Lançamentos Vinculados (Chave: ID_Lancamento)")
            st.dataframe(df_financeiro[['ID_Lancamento', 'ID_Aluno', 'Nome_Aluno', 'Mes_Referencia', 'Valor_Cobrado', 'Status_Pagamento']], use_container_width=True)
        else:
            st.error("Erro ao estruturar dados financeiros. Verifique as colunas ID_Lancamento e Status_Pagamento na planilha.")

    # CORREÇÃO 4: MÓDULO AGENDA DE ATENDIMENTOS (Puxando estritamente da aba central de agendamentos)
    elif menu_treinador == "📅 Agenda de Atendimentos":
        st.subheader("Cronograma de Aulas Presenciais (Chave: ID_Agendamento)")
        
        if not df_agenda.empty and 'Data_Aula' in df_agenda.columns:
            dias_semana = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
            dia_filtro = st.selectbox("Filtrar por dia da semana da Agenda Central:", ["Todos"] + dias_semana)
            
            if dia_filtro != "Todos":
                agenda_filtrada = df_agenda[df_agenda['Data_Aula'] == dia_filtro]
            else:
                agenda_filtrada = df_agenda
                
            st.dataframe(agenda_filtrada[['ID_Agendamento', 'ID_Aluno', 'Nome_Aluno', 'Data_Aula', 'Horario_Inicio', 'Horario_Fim', 'Status_Aula', 'Observacoes_Agenda']], use_container_width=True)
        else:
            st.error("Aba 'Agendamento_Aulas' indisponível ou sem a coluna 'Data_Aula'.")

    # CORREÇÃO 5: PRESCRIÇÃO DE TREINOS (Filtro por ID_Aluno sem estourar se tiver vazio)
    elif menu_treinador == "🏋️ Prescrição de Treinos":
        st.subheader("Central de Fichas de Exercícios (Chave: ID_Exercicio)")
        
        if not df_alunos.empty and 'Nome_Completo' in df_alunos.columns:
            aluno_selecionado = st.selectbox("Selecione o aluno para analisar:", df_alunos['Nome_Completo'].tolist())
            
            # Pega o ID único do Aluno selecionado
            id_aluno = df_alunos[df_alunos['Nome_Completo'] == aluno_selecionado]['ID_Aluno'].values[0]
            
            # Filtra na tabela de treinos usando o ID_Aluno como critério relacional
            if not df_treinos.empty and 'ID_Aluno' in df_treinos.columns:
                treino_especifico = df_treinos[df_treinos['ID_Aluno'] == id_aluno]
                
                st.write(f"Histórico de Exercícios vinculados ao código do aluno: **{id_aluno}**")
                
                # Se a busca voltar vazia porque você ainda não digitou os treinos na planilha
                if treino_especifico.empty or treino_especifico['Nome_Exercicio'].isna().all():
                    st.info(f"O aluno {aluno_selecionado} ({id_aluno}) está cadastrado, mas a ficha técnica de exercícios (EXE) está vazia na planilha.")
                else:
                    st.dataframe(treino_especifico, use_container_width=True)
            else:
                st.error("Aba de Prescrição de Treinos não possui a coluna estrutural 'ID_Aluno'.")

# ==========================================
# 🏃 INTERFACE DO ALUNO
# ==========================================
elif perfil == "🏃 Área do Aluno":
    st.title("Portal do Aluno - Team Muniz")
    
    if not df_alunos.empty and 'Nome_Completo' in df_alunos.columns:
        lista_nomes = df_alunos["Nome_Completo"].dropna().tolist()
        aluno_selecionado = st.selectbox("Quem está acessando?", lista_nomes)
        
        # Captura o ID único do Aluno para cruzar as outras abas
        id_aluno = df_alunos[df_alunos["Nome_Completo"] == aluno_selecionado]["ID_Aluno"].values[0]
        st.write(f"Seu ID de Acesso: **{id_aluno}**")
        
        aba_treino, aba_evolucao, aba_financeiro = st.tabs(["🏋️ Meu Treino", "📈 Minha Evolução", "💳 Meu Financeiro"])
        
        with aba_treino:
            st.subheader("Minha Ficha de Treino Ativa")
            if not df_treinos.empty and 'ID_Aluno' in df_treinos.columns:
                treino_do_aluno = df_treinos[df_treinos["ID_Aluno"] == id_aluno]
                if not treino_do_aluno.empty and not treino_do_aluno["Nome_Exercicio"].isna().all():
                    st.dataframe(treino_do_aluno.dropna(subset=['Nome_Exercicio']), use_container_width=True)
                else:
                    st.info("Fábio está preparando sua nova periodização técnica. Prepare-se!")
            else:
                st.warning("Estrutura de treinos indisponível.")
                
        with aba_evolucao:
            st.subheader("Histórico de Avaliações Físicas (Bioimpedância)")
            if not df_bio.empty and 'ID_Aluno' in df_bio.columns:
                bio_do_aluno = df_bio[df_bio["ID_Aluno"] == id_aluno]
                st.dataframe(bio_do_aluno, use_container_width=True)
            else:
                st.info("Nenhuma avaliação registrada para este ID.")
            
        with aba_financeiro:
            st.subheader("Minhas Faturas")
            if not df_fin = df_financeiro: # Aponta para a base carregada no topo
                fin_do_aluno = df_financeiro[df_financeiro["ID_Aluno"] == id_aluno]
                st.dataframe(fin_do_aluno[['Mes_Referencia', 'Valor_Cobrado', 'Data_Vencimento', 'Status_Pagamento']], use_container_width=True)
