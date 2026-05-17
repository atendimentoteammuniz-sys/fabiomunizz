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

# URL base de exportação para CSV
URL_BASE = "https://docs.google.com/spreadsheets/d/1tqfyKLolU1P7AVOYw7vJcOtG19QOM9tSVu6OK09j668/export?format=csv&gid="

# REORGANIZAÇÃO COMPLETA DOS GIDS DA PLANILHA (Mapeamento Estrito)
GIDS = {
    "Cadastro_Alunos": "1168521543",
    "Controle_Financeiro": "439294975",
    "Agendamento_Aulas": "1486576823",
    "Historico_Bioimpedancia": "2134988451",
    "Prescricao_Treinos": "1619478144",
    "Fluxo_Caixa_Geral": "1809059737"
}

# Função padrão para ler e limpar colunas do Sheets
def carregar_aba_especifica(nome_aba):
    url = URL_BASE + GIDS[nome_aba]
    try:
        df = pd.read_csv(url)
        df = df.dropna(how='all') # Remove linhas fantasmas
        # Limpa os cabeçalhos de poeira do Markdown (\ e *)
        df.columns = df.columns.astype(str).str.replace(r'\\', '', regex=True).str.replace('*', '', regex=False).str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a tabela {nome_aba}: {e}")
        return pd.DataFrame()

# --- MENU LATERAL DE NAVEGAÇÃO ---
st.sidebar.title("🏆 Team Muniz App")
st.sidebar.write("---")
perfil = st.sidebar.radio("Escolha o Perfil:", ["👑 Treinador (Fábio)", "🏃 Área do Aluno"])

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
    # MÓDULO 1: DASHBOARD GERAL (Isolado: Cadastro + Financeiro + Agenda)
    # -----------------------------------------------------------------
    if menu_treinador == "📊 Dashboard Geral":
        st.subheader("Indicadores Operacionais em Tempo Real")
        
        # Puxa as tabelas necessárias de forma isolada
        base_cad = carregar_aba_especifica("Cadastro_Alunos")
        base_fin = carregar_aba_especifica("Controle_Financeiro")
        base_age = carregar_aba_especifica("Agendamento_Aulas")
        
        # Tratamento numérico do financeiro para evitar o erro de zerado
        if not base_fin.empty and 'Valor_Cobrado' in base_fin.columns:
            base_fin['Valor_Num'] = base_fin['Valor_Cobrado'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
        else:
            base_fin['Valor_Num'] = 0.0

        col1, col2, col3 = st.columns(3)
        with col1:
            # Conta estritamente linhas com ID de Aluno (ALU)
            total_alunos = base_cad[base_cad['ID_Aluno'].astype(str).str.contains('ALU', na=False)] if not base_cad.empty else []
            st.metric("Alunos Cadastrados (Total)", len(total_alunos))
        with col2:
            # Soma estritamente os valores da aba de finanças
            faturamento = base_fin['Valor_Num'].sum() if 'Valor_Num' in base_fin.columns else 0.0
            st.metric("Faturamento Previsto (Maio)", f"R$ {faturamento:,.2f}")
        with col3:
            # Conta estritamente os códigos de agendamento (AGE)
            total_aulas = base_age[base_age['ID_Agendamento'].astype(str).str.contains('AGE', na=False)] if not base_age.empty else []
            st.metric("Total de Aulas Agendadas", len(total_aulas))
            
        st.write("---")
        st.subheader("Visualização Cadastral Primária (Base de Alunos Ativos)")
        if not base_cad.empty:
            st.dataframe(base_cad[['ID_Aluno', 'Nome_Completo', 'WhatsApp', 'Modalidade', 'Status_Aluno']], use_container_width=True)
        else:
            st.warning("Sem dados cadastrais para exibir.")

    # -----------------------------------------------------------------
    # MÓDULO 2: FINANCEIRO DETALHADO (Isolado: Apenas ID Financeiro)
    # -----------------------------------------------------------------
    elif menu_treinador == "💰 Financeiro Detalhado":
        st.subheader("Gestão de Receitas & Cobranças")
        
        base_fin = carregar_aba_especifica("Controle_Financeiro")
        
        if not base_fin.empty and 'ID_Lancamento' in base_fin.columns:
            # Converte valores para o gráfico funcionar
            base_fin['Valor_Num'] = base_fin['Valor_Cobrado'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
            
            # Gráfico por Status de Pagamento
            if 'Status_Pagamento' in base_fin.columns:
                resumo_grafico = base_fin.groupby('Status_Pagamento')['Valor_Num'].sum()
                st.bar_chart(resumo_grafico)
            
            st.write("---")
            st.subheader("Lista de Cobranças Estruturadas (Chave: ID_Lancamento)")
            st.dataframe(base_fin[['ID_Lancamento', 'ID_Aluno', 'Nome_Aluno', 'Mes_Referencia', 'Valor_Cobrado', 'Status_Pagamento']], use_container_width=True)
        else:
            st.info("Aguardando preenchimento ou sincronização dos IDs de Lançamentos (FIN001...) na planilha.")

    # -----------------------------------------------------------------
    # MÓDULO 3: AGENDA DE ATENDIMENTOS (Isolado: Apenas ID Agendamento)
    # -----------------------------------------------------------------
    elif menu_treinador == "📅 Agenda de Atendimentos":
        st.subheader("Cronograma de Aulas Semanais")
        
        base_age = carregar_aba_especifica("Agendamento_Aulas")
        
        if not base_age.empty and 'ID_Agendamento' in base_age.columns:
            dias_semana = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
            dia_filtro = st.selectbox("Filtrar por Dia da Semana:", ["Todos"] + dias_semana)
            
            # Executa o filtro focado na aba real de agendamentos
            if dia_filtro != "Todos" and 'Data_Aula' in base_age.columns:
                agenda_filtrada = base_age[base_age['Data_Aula'] == dia_filtro]
            else:
                agenda_filtrada = base_age
                
            st.dataframe(agenda_filtrada[['ID_Agendamento', 'ID_Aluno', 'Nome_Aluno', 'Data_Aula', 'Horario_Inicio', 'Horario_Fim', 'Status_Aula']], use_container_width=True)
        else:
            st.info("Aguardando sincronização dos códigos de Agendamento (AGE001...) na planilha.")

    # -----------------------------------------------------------------
    # MÓDULO 4: PRESCRIÇÃO DE TREINOS (Isolado: Apenas ID Exercício)
    # -----------------------------------------------------------------
    elif menu_treinador == "🏋️ Prescrição de Treinos":
        st.subheader("Central Técnica de Exercícios")
        
        base_cad = carregar_aba_especifica("Cadastro_Alunos")
        base_tre = carregar_aba_especifica("Prescricao_Treinos")
        
        if not base_cad.empty and 'Nome_Completo' in base_cad.columns:
            aluno_alvo = st.selectbox("Selecione o Aluno para puxar a Ficha:", base_cad['Nome_Completo'].tolist())
            id_aluno_alvo = base_cad[base_cad['Nome_Completo'] == aluno_alvo]['ID_Aluno'].values[0]
            
            st.write(f"Buscando exercícios vinculados ao código do aluno: **{id_aluno_alvo}**")
            
            if not base_tre.empty and 'ID_Aluno' in base_tre.columns:
                treino_filtrado = base_tre[base_tre['ID_Aluno'] == id_aluno_alvo]
                
                if treino_filtrado.empty or treino_filtrado['Nome_Exercicio'].isna().all():
                    st.info(f"O aluno está indexado corretamente, mas a tabela de exercícios (EXE) está vazia para ele na planilha.")
                else:
                    st.dataframe(treino_filtrado[['ID_Exercicio', 'ID_Aluno', 'Nome_Aluno', 'Divisao_Treino', 'Grupo_Muscular', 'Nome_Exercicio', 'Series', 'Repeticoes', 'Descanso']], use_container_width=True)
            else:
                st.warning("A aba de Prescrição de Treinos ainda não possui colunas preenchidas.")

# =====================================================================
# 🏃 PORTAL DO ALUNO (TEAM MUNIZ)
# =====================================================================
elif perfil == "🏃 Área do Aluno":
    st.title("Portal do Aluno - Team Muniz")
    
    base_cad = carregar_aba_especifica("Cadastro_Alunos")
    
    if not base_cad.empty and 'Nome_Completo' in base_cad.columns:
        aluno_logado = st.selectbox("Quem está acessando o portal?", base_cad["Nome_Completo"].dropna().tolist())
        id_aluno_logado = base_cad[base_cad["Nome_Completo"] == aluno_logado]["ID_Aluno"].values[0]
        
        st.write(f"Código do Aluno: **{id_aluno_logado}**")
        
        tab_t, tab_e, tab_f = st.tabs(["🏋️ Meu Treino", "📈 Minha Evolução", "💳 Meu Financeiro"])
        
        with tab_t:
            base_tre = carregar_aba_especifica("Prescricao_Treinos")
            if not base_tre.empty and 'ID_Aluno' in base_tre.columns:
                treino_aluno = base_tre[base_tre["ID_Aluno"] == id_aluno_logado].dropna(subset=['Nome_Exercicio'])
                if not treino_aluno.empty:
                    st.dataframe(treino_aluno, use_container_width=True)
                else:
                    st.info("Treino em fase de montagem estratégica por Fábio Muniz.")
                    
        with tab_e:
            base_bio = carregar_aba_especifica("Historico_Bioimpedancia")
            if not base_bio.empty and 'ID_Aluno' in base_bio.columns:
                bio_aluno = base_bio[base_bio["ID_Aluno"] == id_aluno_logado]
                st.dataframe(bio_aluno, use_container_width=True)
                
        with tab_f:
            base_fin = carregar_aba_especifica("Controle_Financeiro")
            if not base_fin.empty and 'ID_Aluno' in base_fin.columns:
                fin_aluno = base_fin[base_fin["ID_Aluno"] == id_aluno_logado]
                st.dataframe(fin_aluno[['Mes_Referencia', 'Valor_Cobrado', 'Data_Vencimento', 'Status_Pagamento']], use_container_width=True)
