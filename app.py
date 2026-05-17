import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA E INTERFACE PREMIUM
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

# 2. ESTRUTURA DE LINKS E CONEXÃO COM O GOOGLE SHEETS
URL_BASE = "https://docs.google.com/spreadsheets/d/1tqfyKLolU1P7AVOYw7vJcOtG19QOM9tSVu6OK09j668/export?format=csv&gid="

GIDS = {
    "Cadastro_Alunos": "1168521543",
    "Controle_Financeiro": "439294975",
    "Agendamento_Aulas": "1486576823",
    "Historico_Bioimpedancia": "2134988451",
    "Prescricao_Treinos": "1619478144",
    "Fluxo_Caixa_Geral": "1809059737"
}

@st.cache_data(ttl=5) # Atualização rápida (5 segundos) para feedback imediato
def puxar_e_saneamentos_de_dados(aba_nome):
    url = URL_BASE + GIDS[aba_nome]
    try:
        # Força o pandas a ler a planilha tratando tudo como texto inicialmente para evitar perda de zeros à esquerda
        df = pd.read_csv(url, dtype=str)
        
        # Elimina linhas completamente em branco da planilha
        df = df.dropna(how='all')
        
        # BRECHA CORRIGIDA: Limpeza profunda de cabeçalhos de colunas contra Markdown invasivo
        df.columns = df.columns.astype(str).str.replace(r'\\', '', regex=True)
        df.columns = df.columns.str.replace('*', '', regex=False)
        df.columns = df.columns.str.strip()
        
        # BRECHA CORRIGIDA: Padronização de dados internos de identificação para evitar falhas de digitação
        for col in df.columns:
            if 'ID_' in col:
                df[col] = df[col].astype(str).str.strip().str.upper()
                
        return df
    except Exception as e:
        st.error(f"Instabilidade técnica ao conectar com a tabela '{aba_nome}': {e}")
        return pd.DataFrame()

# 3. CARREGAMENTO OPERACIONAL DAS BASES DE DADOS
df_alunos = puxar_e_saneamentos_de_dados("Cadastro_Alunos")
df_financeiro = puxar_e_saneamentos_de_dados("Controle_Financeiro")
df_agenda = puxar_e_saneamentos_de_dados("Agendamento_Aulas")
df_treinos = puxar_e_saneamentos_de_dados("Prescricao_Treinos")
df_bio = puxar_e_saneamentos_de_dados("Historico_Bioimpedancia")
df_caixa = puxar_e_saneamentos_de_dados("Fluxo_Caixa_Geral")

# BRECHA CORRIGIDA: Conversão monetária segura tratando valores nulos ou strings inválidas
if not df_financeiro.empty and 'Valor_Cobrado' in df_financeiro.columns:
    df_financeiro['Valor_Num'] = (
        df_financeiro['Valor_Cobrado']
        .fillna('0')
        .astype(str)
        .str.replace('R$', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .str.strip()
    )
    df_financeiro['Valor_Num'] = pd.to_numeric(df_financeiro['Valor_Num'], errors='coerce').fillna(0.0)
else:
    df_financeiro['Valor_Num'] = 0.0

# 4. MENU DE CONTEXTO LATERAL
st.sidebar.title("🏆 Team Muniz App")
st.sidebar.write("---")
perfil = st.sidebar.radio("Selecione o Perfil de Entrada:", ["👑 Treinador (Fábio)", "🏃 Área do Aluno"])

# ==========================================
# 👑 INTERFACE DE GESTÃO: TREINADOR (FÁBIO)
# ==========================================
if perfil == "👑 Treinador (Fábio)":
    st.title("Painel de Controle Executivo")
    
    menu_treinador = st.sidebar.selectbox(
        "Módulo de Gerenciamento:", 
        ["📊 Dashboard Geral", "💰 Financeiro Detalhado", "📅 Agenda de Atendimentos", "🏋️ Prescrição de Treinos"]
    )
    
    # MÓDULO: DASHBOARD GERAL
    if menu_treinador == "📊 Dashboard Geral":
        st.subheader("Indicadores de Desempenho do Negócio")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            total_alunos = len(df_alunos) if not df_alunos.empty else 0
            st.metric("Alunos Ativos Base", total_alunos)
        with col2:
            faturamento_total = df_financeiro['Valor_Num'].sum() if 'Valor_Num' in df_financeiro.columns else 0.0
            st.metric("Previsão de Receita Mensal", f"R$ {faturamento_total:,.2f}")
        with col3:
            total_agendamentos = len(df_agenda) if not df_agenda.empty else 0
            st.metric("Aulas Totais na Agenda", total_agendamentos)
            
        st.write("---")
        st.subheader("Ficha de Cadastro Centralizada")
        if not df_alunos.empty:
            exibir_colunas = [c for c in ['ID_Aluno', 'Nome_Completo', 'WhatsApp', 'Modalidade', 'Status_Aluno'] if c in df_alunos.columns]
            st.dataframe(df_alunos[exibir_colunas], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum dado cadastral localizado na planilha master.")

    # MÓDULO: GESTÃO FINANCEIRA
    elif menu_treinador == "💰 Financeiro Detalhado":
        st.subheader("Análise Gráfica de Entradas")
        
        if not df_financeiro.empty and 'Status_Pagamento' in df_financeiro.columns:
            # Agrupamento seguro protegendo o sistema contra quebras se houver apenas um tipo de status
            resumo_status = df_financeiro.groupby('Status_Pagamento')['Valor_Num'].sum()
            st.bar_chart(resumo_status)
            
            st.write("---")
            st.subheader("Livro de Lançamentos de Cobrança")
            st.dataframe(df_financeiro, use_container_width=True, hide_index=True)
        else:
            st.warning("Base financeira vazia ou colunas de controle ausentes.")

    # MÓDULO: AGENDA CENTRAL DE AULAS
    elif menu_treinador == "📅 Agenda de Atendimentos":
        st.subheader("Visão por Cronograma Semanal")
        
        if not df_agenda.empty and 'Data_Aula' in df_agenda.columns:
            dias_semana = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
            dia_filtro = st.selectbox("Escolha o Dia para Auditoria:", ["Todos os Dias"] + dias_semana)
            
            # Padroniza a string de busca para evitar quebras por acentuação ou caixa alta
            if dia_filtro != "Todos os Dias":
                agenda_filtrada = df_agenda[df_agenda['Data_Aula'].str.strip().str.lower() == dia_filtro.lower()]
            else:
                agenda_filtrada = df_agenda
                
            st.dataframe(agenda_filtrada, use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhuma rotina de agendamento de aulas foi estruturada na planilha.")

    # MÓDULO: PRESCRIÇÃO E FICHA TÉCNICA
    elif menu_treinador == "🏋️ Prescrição de Treinos":
        st.subheader("Gestor de Treinos Relacional")
        
        if not df_alunos.empty and 'Nome_Completo' in df_alunos.columns:
            aluno_treino = st.selectbox("Selecione o Aluno Alvo:", df_alunos['Nome_Completo'].dropna().unique().tolist())
            
            # Captura o ID do aluno associado de forma estrita
            linha_aluno = df_alunos[df_alunos['Nome_Completo'] == aluno_treino]
            if not linha_aluno.empty:
                id_aluno = str(linha_aluno['ID_Aluno'].values[0]).strip().upper()
                
                st.write(f"Código do Aluno Selecionado: **{id_aluno}**")
                
                if not df_treinos.empty and 'ID_Aluno' in df_treinos.columns:
                    # Filtra cruzando estritamente os IDs tratados
                    treino_especifico = df_treinos[df_treinos['ID_Aluno'].str.strip().str.upper() == id_aluno]
                    
                    if treino_especifico.empty or treino_especifico['Nome_Exercicio'].isna().all():
                        st.info(f"O sistema localizou o cadastro de {aluno_treino}, mas a tabela de exercícios técnicos (EXE) está aguardando inserção de dados no Sheets.")
                    else:
                        st.dataframe(treino_especifico, use_container_width=True, hide_index=True)
                else:
                    st.error("Aba de Prescrição de Treinos sem coluna relacional indexadora 'ID_Aluno'.")
        else:
            st.error("Impossível carregar módulo de prescrição: Lista de alunos inválida.")

# ==========================================
# 🏃 INTERFACE DE ACESSO: ÁREA DO ALUNO
# ==========================================
elif perfil == "🏃 Área do Aluno":
    st.title("Portal do Aluno - Team Muniz")
    
    if not df_alunos.empty and 'Nome_Completo' in df_alunos.columns:
        lista_nomes = df_alunos["Nome_Completo"].dropna().unique().tolist()
        aluno_selecionado = st.selectbox("Selecione seu Nome de Usuário para Login:", lista_nomes)
        
        # Pega o ID de amarração de forma blindada
        id_aluno = str(df_alunos[df_alunos["Nome_Completo"] == aluno_selecionado]["ID_Aluno"].values[0]).strip().upper()
        st.info(f"Bem-vindo! Seu ID Identificador de Segurança é: **{id_aluno}**")
        
        aba_treino, aba_evolucao, aba_financeiro = st.tabs(["🏋️ Minha Ficha de Treino", "📈 Gráficos de Evolução", "💳 Situação Financeira"])
        
        # ABA ALUNO: TREINOS
        with aba_treino:
            st.subheader("Sua Rotina Exclusiva de Exercícios")
            if not df_treinos.empty and 'ID_Aluno' in df_treinos.columns:
                treino_do_aluno = df_treinos[df_treinos["ID_Aluno"].str.strip().str.upper() == id_aluno]
                
                if not treino_do_aluno.empty and not treino_do_aluno["Nome_Exercicio"].isna().all():
                    st.dataframe(treino_do_aluno.dropna(subset=['Nome_Exercicio']), use_container_width=True, hide_index=True)
                else:
                    st.info("Sua nova periodização técnica está em desenvolvimento pelo treinador Fábio. Aguarde a liberação!")
            else:
                st.warning("Sistema de treinos fora de alcance temporariamente.")
                
        # ABA ALUNO: AVALIAÇÃO FÍSICA
        with aba_evolucao:
            st.subheader("Histórico Clínico e Bioimpedância")
            if not df_bio.empty and 'ID_Aluno' in df_bio.columns:
                bio_do_aluno = df_bio[df_bio["ID_Aluno"].str.strip().str.upper() == id_aluno]
                if not bio_do_aluno.empty:
                    st.dataframe(bio_do_aluno, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum registro de bioimpedância lançado para o seu ID até o momento.")
            else:
                st.warning("Módulo de evolução indisponível.")
            
        # ABA ALUNO: FINANCEIRO
        with aba_financeiro:
            st.subheader("Histórico de Mensalidades")
            if not df_financeiro.empty and 'ID_Aluno' in df_financeiro.columns:
                fin_do_aluno = df_financeiro[df_financeiro["ID_Aluno"].str.strip().str.upper() == id_aluno]
                if not fin_do_aluno.empty:
                    colunas_aluno_fin = [c for c in ['Mes_Referencia', 'Valor_Cobrado', 'Data_Vencimento', 'Status_Pagamento'] if c in fin_do_aluno.columns]
                    st.dataframe(fin_do_aluno[colunas_aluno_fin], use_container_width=True, hide_index=True)
                else:
                    st.info("Não existem faturas em aberto ou processadas vinculadas a este perfil.")
            else:
                st.warning("Painel financeiro do aluno fora do ar.")
