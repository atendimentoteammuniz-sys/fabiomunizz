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

# URL base pública da sua planilha
URL_BASE = "https://docs.google.com/spreadsheets/d/1tqfyKLolU1P7AVOYw7vJcOtG19QOM9tSVu6OK09j668/export?format=csv&gid="

# GIDs OFICIAIS mapeados diretamente dos links fornecidos por você
GIDS = {
    "Cadastro_Alunos": "896837375",
    "Historico_Bioimpedancia": "736167025",
    "Controle_Financeiro": "266431932",
    "Fluxo_Caixa_Geral": "1156715922",
    "Prescricao_Treinos": "181621672",
    "Agendamento_Aulas": "1168521543"
}

def carregar_e_limpar_aba(nome_aba):
    url = URL_BASE + GIDS[nome_aba]
    try:
        # Lê a aba e força todas as colunas a serem tratadas como texto limpo
        df = pd.read_csv(url, dtype=str)
        df = df.dropna(how='all')
        
        # Padroniza os cabeçalhos: remove espaços e joga para maiúsculo
        df.columns = df.columns.astype(str).str.strip().str.upper()
        
        # Limpa espaços em branco de todas as células do dataframe
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
        return df
    except Exception as e:
        st.error(f"Erro de comunicação com a tabela '{nome_aba}': {e}")
        return pd.DataFrame()

# --- MENU LATERAL DE NAVEGAÇÃO ---
st.sidebar.title("🏆 Team Muniz App")
st.sidebar.write("---")
perfil = st.sidebar.radio("Escolha o Perfil:", ["👑 Treinador (Fábio)", "🏃 Área do Aluno"])

# Carregamento global e centralizado das tabelas limpas
base_cad = carregar_e_limpar_aba("Cadastro_Alunos")
base_fin = carregar_e_limpar_aba("Controle_Financeiro")
base_age = carregar_e_limpar_aba("Agendamento_Aulas")
base_tre = carregar_e_limpar_aba("Prescricao_Treinos")
base_bio = carregar_e_limpar_aba("Historico_Bioimpedancia")

# =====================================================================
# 👑 PAINEL DO TREINADOR (FÁBIO MUNIZ)
# =====================================================================
if perfil == "👑 Treinador (Fábio)":
    st.title("Painel de Controle Executivo")
    
    menu_treinador = st.sidebar.selectbox(
        "Gerenciar Módulo:", 
        ["📊 Dashboard Geral", "💰 Financeiro Detalhado", "📅 Agenda de Atendimentos", "🏋️ Prescrição de Treinos"]
    )
    
    # -----------------------------------------------------------------
    # MÓDULO 1: DASHBOARD GERAL
    # -----------------------------------------------------------------
    if menu_treinador == "📊 Dashboard Geral":
        st.subheader("Indicadores Operacionais em Tempo Real")
        
        # Cálculo de Faturamento puramente numérico
        faturamento = 0.0
        if not base_fin.empty and 'VALOR_COBRADO' in base_fin.columns:
            base_fin['VAL_NUM'] = base_fin['VALOR_COBRADO'].str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
            faturamento = base_fin['VAL_NUM'].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            total_alunos = len(base_cad[base_cad['ID_ALUNO'].str.contains('ALU', na=False, case=False)]) if not base_cad.empty and 'ID_ALUNO' in base_cad.columns else 0
            st.metric("Alunos Cadastrados (Total)", total_alunos)
        with col2:
            st.metric("Faturamento Previsto", f"R$ {faturamento:,.2f}")
        with col3:
            total_aulas = len(base_age[base_age['ID_AGENDAMENTO'].str.contains('AGE', na=False, case=False)]) if not base_age.empty and 'ID_AGENDAMENTO' in base_age.columns else 0
            st.metric("Total de Aulas Agendadas", total_aulas)
            
        st.write("---")
        st.subheader("Visualização Cadastral Primária (Base de Alunos Ativos)")
        if not base_cad.empty:
            st.dataframe(base_cad, use_container_width=True)
        else:
            st.warning("Aguardando dados da aba 'Cadastro_Alunos'.")

    # -----------------------------------------------------------------
    # MÓDULO 2: FINANCEIRO DETALHADO
    # -----------------------------------------------------------------
    elif menu_treinador == "💰 Financeiro Detalhado":
        st.subheader("Gestão de Receitas & Cobranças")
        
        if not base_fin.empty and 'VALOR_COBRADO' in base_fin.columns:
            base_fin['VAL_NUM'] = base_fin['VALOR_COBRADO'].str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
            
            if 'STATUS_PAGAMENTO' in base_fin.columns:
                resumo_grafico = base_fin.groupby('STATUS_PAGAMENTO')['VAL_NUM'].sum()
                st.bar_chart(resumo_grafico)
            
            st.write("---")
            st.dataframe(base_fin, use_container_width=True)
        else:
            st.info("Nenhum dado financeiro estruturado encontrado.")

    # -----------------------------------------------------------------
    # MÓDULO 3: AGENDA DE ATENDIMENTOS
    # -----------------------------------------------------------------
    elif menu_treinador == "📅 Agenda de Atendimentos":
        st.subheader("Cronograma de Aulas Semanais")
        
        if not base_age.empty:
            if 'DATA_AULA' in base_age.columns:
                dias_semana = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
                dia_filtro = st.selectbox("Filtrar por Dia da Semana:", ["Todos"] + dias_semana)
                
                if dia_filtro != "Todos":
                    agenda_filtrada = base_age[base_age['DATA_AULA'].str.lower() == dia_filtro.lower()]
                else:
                    agenda_filtrada = base_age
                st.dataframe(agenda_filtrada, use_container_width=True)
            else:
                st.dataframe(base_age, use_container_width=True)
        else:
            st.info("Nenhum agendamento encontrado.")

    # -----------------------------------------------------------------
    # MÓDULO 4: PRESCRIÇÃO DE TREINOS
    # -----------------------------------------------------------------
    elif menu_treinador == "🏋️ Prescrição de Treinos":
        st.subheader("Central Técnico de Exercícios")
        
        if not base_cad.empty and 'ID_ALUNO' in base_cad.columns and 'NOME_ALUNO' in base_cad.columns:
            base_cad['SELECAO'] = base_cad['ID_ALUNO'] + " - " + base_cad['NOME_ALUNO']
            aluno_selecionado = st.selectbox("Selecione o Aluno para puxar a Ficha:", base_cad['SELECAO'].tolist())
            
            id_aluno_alvo = aluno_selecionado.split(" - ")[0].strip().upper()
            st.write(f"Filtrando treinos para o ID: **{id_aluno_alvo}**")
            
            if not base_tre.empty and 'ID_ALUNO' in base_tre.columns:
                treino_filtrado = base_tre[base_tre['ID_ALUNO'].str.upper() == id_aluno_alvo]
                
                if treino_filtrado.empty:
                    st.info(f"Nenhum exercício vinculado ao ID {id_aluno_alvo} na planilha.")
                else:
                    st.dataframe(treino_filtrado, use_container_width=True)
            else:
                st.warning("Tabela de Prescrição de Treinos sem coluna 'ID_ALUNO' ou vazia.")

# =====================================================================
# 🏃 PORTAL DO ALUNO (TEAM MUNIZ)
# =====================================================================
elif perfil == "🏃 Área do Aluno":
    st.title("Portal do Aluno - Team Muniz")
    
    if not base_cad.empty and 'ID_ALUNO' in base_cad.columns:
        if 'NOME_ALUNO' in base_cad.columns:
            base_cad['SELECAO'] = base_cad['ID_ALUNO'] + " - " + base_cad['NOME_ALUNO']
            aluno_logado = st.selectbox("Selecione seu ID para acessar o portal:", base_cad['SELECAO'].tolist())
            id_aluno_puro = aluno_logado.split(" - ")[0].strip().upper()
        else:
            id_aluno_puro = st.selectbox("Selecione seu ID de Aluno:", base_cad['ID_ALUNO'].tolist())
            
        st.write(f"Acessando dados do ID: **{id_aluno_puro}**")
        
        # Criação das Abas com a Bioimpedância reativada
        tab_t, tab_e, tab_f = st.tabs(["🏋️ Meu Treino", "📈 Minha Evolução", "💳 Meu Financeiro"])
        
        with tab_t:
            if not base_tre.empty and 'ID_ALUNO' in base_tre.columns:
                treino_aluno = base_tre[base_tre['ID_ALUNO'].str.upper() == id_aluno_puro]
                st.dataframe(treino_aluno, use_container_width=True)
            else:
                st.info("Nenhuma ficha de treino disponível no momento.")
                
        with tab_e:
            if not base_bio.empty and 'ID_ALUNO' in base_bio.columns:
                bio_aluno = base_bio[base_bio['ID_ALUNO'].str.upper() == id_aluno_puro]
                st.dataframe(bio_aluno, use_container_width=True)
            else:
                st.info("Nenhum histórico de evolução ou bioimpedância registrado para este ID.")
                            
        with tab_f:
            if not base_fin.empty and 'ID_ALUNO' in base_fin.columns:
                fin_aluno = base_fin[base_fin['ID_ALUNO'].str.upper() == id_aluno_puro]
                st.dataframe(fin_aluno, use_container_width=True)
            else:
                st.info("Histórico financeiro não encontrado para este ID.")
