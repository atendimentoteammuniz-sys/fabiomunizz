import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA E DESIGN PREMIUM
st.set_page_config(
    page_title="Team Muniz - Dashboard",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Visual Customizada (Preto, Branco e Dourado)
st.markdown("""
    <style>
    .main { background-color: #111111; color: #FFFFFF; }
    .sidebar .sidebar-content { background-color: #1A1A1A; }
    h1, h2, h3 { color: #D4AF37 !important; }
    div.stButton > button:first-child {
        background-color: #D4AF37; color: #111111; font-weight: bold; border-radius: 5px;
    }
    .stMetric { background-color: #1A1A1A; padding: 15px; border-radius: 8px; border: 1px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE CONEXÃO E LIMPEZA DE ENDPOINTS (API GOOGLE VISUALIZATION)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1tqfyKLolU1P7AVOYw7vJcOtG19QOM9tSVu6OK09j668/gviz/tq?tqx=out:csv&gid="

GIDS = {
    "Cadastro_Alunos": "1168521543",
    "Controle_Financeiro": "439294975",
    "Agendamento_Aulas": "1486576823",
    "Historico_Bioimpedancia": "2134988451",
    "Prescricao_Treinos": "1619478144",
    "Fluxo_Caixa_Geral": "1809059737"
}

@st.cache_data(ttl=2) # Atualização quase instantânea para digitação na planilha
def carregar_e_higienizar_aba(aba_nome):
    url = URL_PLANILHA + GIDS[aba_nome]
    try:
        # Puxa os dados brutos da API do Google
        df = pd.read_csv(url, dtype=str)
        
        # Remove linhas completamente nulas jogadas pelo Sheets
        df = df.dropna(how='all')
        
        # TRATAMENTO CRÍTICO DE CABEÇALHOS: Elimina \r, \n, asteriscos, barras e espaços invisíveis
        df.columns = (
            df.columns.astype(str)
            .str.replace(r'[\r\n]', '', regex=True)
            .str.replace(r'\\', '', regex=True)
            .str.replace('*', '', regex=False)
            .str.strip()
        )
        
        # TRATAMENTO CRÍTICO DE DADOS: Passa um pente fino em todas as células eliminando quebras de linha ocultas (\r)
        for col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[\r\n]', '', regex=True).str.strip()
            
        return df
    except Exception as e:
        st.error(f"Erro de comunicação na aba '{aba_nome}': {e}")
        return pd.DataFrame()

# 3. CARREGAMENTO DAS BASES HIGIENIZADAS
df_alunos = carregar_e_higienizar_aba("Cadastro_Alunos")
df_financeiro = carregar_e_higienizar_aba("Controle_Financeiro")
df_agenda = carregar_e_higienizar_aba("Agendamento_Aulas")
df_treinos = carregar_e_higienizar_aba("Prescricao_Treinos")
df_bio = carregar_e_higienizar_aba("Historico_Bioimpedancia")

# Mapeamento dinâmico para encontrar a coluna de ID do Aluno de forma flexível (independente de como foi escrita)
def localizar_coluna_id(df):
    for col in df.columns:
        if col.lower() in ['id_aluno', 'alunoid', 'id aluno']:
            return col
    return None

# Mapeamento dinâmico para encontrar a coluna de Nome do Aluno
def localizar_coluna_nome(df):
    for col in df.columns:
        if col.lower() in ['nome_completo', 'nome_aluno', 'nome completo', 'nome aluno']:
            return col
    return None

# Processamento numérico seguro do faturamento
if not df_financeiro.empty and 'Valor_Cobrado' in df_financeiro.columns:
    df_financeiro['Valor_Num'] = (
        df_financeiro['Valor_Cobrado']
        .astype(str)
        .str.replace('R$', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .str.strip()
    )
    df_financeiro['Valor_Num'] = pd.to_numeric(df_financeiro['Valor_Num'], errors='coerce').fillna(0.0)
else:
    df_financeiro['Valor_Num'] = 0.0

# 4. PAINEL DE NAVEGAÇÃO LATERAL
st.sidebar.title("🏆 Team Muniz App")
st.sidebar.write("---")
perfil = st.sidebar.radio("Selecione o Perfil de Entrada:", ["👑 Treinador (Fábio)", "🏃 Área do Aluno"])

# ==========================================
# 👑 VISÃO DO TREINADOR (FÁBIO)
# ==========================================
if perfil == "👑 Treinador (Fábio)":
    st.title("Painel de Controle Executivo")
    
    menu_treinador = st.sidebar.selectbox(
        "Módulo de Gerenciamento:", 
        ["📊 Dashboard Geral", "💰 Financeiro Detalhado", "📅 Agenda de Atendimentos", "🏋️ Prescrição de Treinos"]
    )
    
    # 📊 FILTRO: DASHBOARD GERAL
    if menu_treinador == "📊 Dashboard Geral":
        st.subheader("Indicadores Operacionais em Tempo Real")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            # Conta estritamente as linhas da aba Cadastro_Alunos
            total_clientes = len(df_alunos) if not df_alunos.empty else 0
            st.metric("Alunos Cadastrados (Total)", total_clientes)
        with col2:
            # Soma real processada da coluna financeira
            receita_prevista = df_financeiro['Valor_Num'].sum() if 'Valor_Num' in df_financeiro.columns else 0.0
            st.metric("Faturamento Previsto (Maio)", f"R$ {receita_prevista:,.2f}")
        with col3:
            # Conta estritamente a quantidade de agendamentos montados
            total_aulas = len(df_agenda) if not df_agenda.empty else 0
            st.metric("Total de Aulas Agendadas", total_aulas)
            
        st.write("---")
        st.subheader("Visualização Cadastral Primária (Aba Cadastro)")
        if not df_alunos.empty:
            st.dataframe(df_alunos, use_container_width=True, hide_index=True)
        else:
            st.warning("Aba Cadastro_Alunos está inacessível ou vazia.")

    # 💰 FILTRO: FINANCEIRO DETALHADO
    elif menu_treinador == "💰 Financeiro Detalhado":
        st.subheader("Performance Financeira de Cobranças")
        
        if not df_financeiro.empty and 'Status_Pagamento' in df_financeiro.columns:
            resumo_grafico = df_financeiro.groupby('Status_Pagamento')['Valor_Num'].sum()
            st.bar_chart(resumo_grafico)
            
            st.write("---")
            st.subheader("Todos os Lançamentos Financeiros (Chave: ID_Lancamento)")
            st.dataframe(df_financeiro, use_container_width=True, hide_index=True)
        else:
            st.warning("Não há dados financeiros estruturados para exibição.")

    # 📅 FILTRO: AGENDA DE ATENDIMENTOS
    elif menu_treinador == "📅 Agenda de Atendimentos":
        st.subheader("Cronograma Geral de Aulas (Chave: ID_Agendamento)")
        
        if not df_agenda.empty:
            col_dia = 'Data_Aula' if 'Data_Aula' in df_agenda.columns else (df_agenda.columns[3] if len(df_agenda.columns) > 3 else None)
            
            if col_dia and col_dia in df_agenda.columns:
                lista_dias = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
                dia_selecionado = st.selectbox("Filtrar Visão do Cronograma Semanal:", ["Todos os Dias"] + lista_dias)
                
                if dia_selecionado != "Todos os Dias":
                    agenda_exibicao = df_agenda[df_agenda[col_dia].str.lower() == dia_selecionado.lower()]
                else:
                    agenda_exibicao = df_agenda
                    
                st.dataframe(agenda_exibicao, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_agenda, use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum dado encontrado na aba Agendamento_Aulas.")

    # 🏋️ FILTRO: PRESCRIÇÃO DE TREINOS
    elif menu_treinador == "🏋️ Prescrição de Treinos":
        st.subheader("Fichas Técnicas de Exercícios (Chave: ID_Exercicio)")
        
        col_nome_aluno = localizar_coluna_nome(df_alunos)
        col_id_aluno = localizar_coluna_id(df_alunos)
        
        if col_nome_aluno and not df_alunos.empty:
            aluno_alvo = st.selectbox("Selecione o Aluno para Auditoria de Treino:", df_alunos[col_nome_aluno].unique().tolist())
            id_do_alvo = df_alunos[df_alunos[col_nome_aluno] == aluno_alvo][col_id_aluno].values[0]
            
            st.write(f"Buscando treinos vinculados ao ID do Aluno: **{id_do_alvo}**")
            
            col_id_treino = localizar_coluna_id(df_treinos)
            if col_id_treino and not df_treinos.empty:
                treino_filtrado = df_treinos[df_treinos[col_id_treino].str.upper() == id_do_alvo.upper()]
                
                # Se a planilha tiver as linhas dos IDs criadas mas sem o nome do exercício digitado ainda
                if treino_filtrado.empty or ('Nome_Exercicio' in treino_filtrado.columns and treino_filtrado['Nome_Exercicio'].isna().all()):
                    st.info(f"O aluno {aluno_alvo} ({id_do_alvo}) está integrado no app, mas as especificações técnicas de exercícios estão vazias na planilha.")
                else:
                    st.dataframe(treino_filtrado, use_container_width=True, hide_index=True)
            else:
                st.warning("Aba de Prescrição de Treinos vazia ou sem coluna indexadora de ID.")
        else:
            st.error("Base cadastral indisponível para carregar a lista de seleção.")

# ==========================================
# 🏃 VISÃO INTERACTIVE: ÁREA DO ALUNO
# ==========================================
elif perfil == "🏃 Área do Aluno":
    st.title("Portal do Aluno - Team Muniz")
    
    col_nome_aluno = localizar_coluna_nome(df_alunos)
    col_id_aluno = localizar_coluna_id(df_alunos)
    
    if col_nome_aluno and not df_alunos.empty:
        aluno_user = st.selectbox("Selecione seu Nome Cadastrado para Acesso:", df_alunos[col_nome_aluno].unique().tolist())
        id_cripto = df_alunos[df_alunos[col_nome_aluno] == aluno_user][col_id_aluno].values[0]
        
        st.info(f"Acesso Autorizado! Identificador de Matrícula: **{id_cripto}**")
        
        t1, t2, t3 = st.tabs(["🏋️ Minha Ficha de Treino", "📈 Minha Evolução Física", "💳 Minhas Mensalidades"])
        
        with t1:
            st.subheader("Prescrição de Treino Ativa")
            col_id_treinos = localizar_coluna_id(df_treinos)
            if col_id_treinos and not df_treinos.empty:
                meu_treino = df_treinos[df_treinos[col_id_treinos].str.upper() == id_cripto.upper()]
                if not meu_treino.empty and 'Nome_Exercicio' in meu_treino.columns and not meu_treino['Nome_Exercicio'].isna().all():
                    st.dataframe(meu_treino, use_container_width=True, hide_index=True)
                else:
                    st.info("Fábio está estruturando a sua nova planilha de treinamento técnico. Aguarde as atualizações!")
            else:
                st.warning("Módulo de treinos indisponível.")
                
        with t2:
            st.subheader("Histórico de Avaliações (Bioimpedância)")
            col_id_bio = localizar_coluna_id(df_bio)
            if col_id_bio and not df_bio.empty:
                minha_bio = df_bio[df_bio[col_id_bio].str.upper() == id_cripto.upper()]
                if not minha_bio.empty:
                    st.dataframe(minha_bio, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum registro de avaliação física associado a este ID.")
            else:
                st.warning("Módulo de bioimpedância inacessível.")
                
        with t3:
            st.subheader("Controle de Faturas")
            col_id_fin = localizar_coluna_id(df_financeiro)
            if col_id_fin and not df_financeiro.empty:
                meu_financeiro = df_financeiro[df_financeiro[col_id_fin].str.upper() == id_cripto.upper()]
                if not meu_financeiro.empty:
                    exibir_faturas = [c for c in ['Mes_Referencia', 'Valor_Cobrado', 'Data_Vencimento', 'Status_Pagamento'] if c in meu_financeiro.columns]
                    st.dataframe(meu_financeiro[exibir_faturas], use_container_width=True, hide_index=True)
                else:
                    st.info("Não constam cobranças ativas vinculadas a esta matrícula.")
            else:
                st.warning("Painel financeiro indisponível.")
