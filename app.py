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

# GIDs Estritos das suas abas coletados da planilha ativa
GIDS = {
    "Cadastro_Alunos": "1168521543",
    "Controle_Financeiro": "439294975",
    "Agendamento_Aulas": "1486576823",
    "Historico_Bioimpedancia": "2134988451",
    "Prescricao_Treinos": "1619478144",
    "Fluxo_Caixa_Geral": "1809059737"
}

def carregar_e_normalizar_aba(nome_aba):
    url = URL_BASE + GIDS[nome_aba]
    try:
        # Força o pandas a ler tudo como texto inicialmente para evitar quebras
        df = pd.read_csv(url, dtype=str)
        
        # Remove linhas totalmente vazias
        df = df.dropna(how='all')
        
        # SUPER BLINDAGEM DE CABEÇALHOS: Limpa espaços, asteriscos, barras e joga tudo para minúsculo
        df.columns = (df.columns.astype(str)
                      .str.replace(r'\\', '', regex=True)
                      .str.replace('*', '', regex=False)
                      .str.strip()
                      .str.lower())
        
        return df
    except Exception as e:
        st.error(f"Erro de comunicação com a tabela '{nome_aba}': {e}")
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
    
    # Carregamento isolado e blindado das bases
    base_cad = carregar_e_normalizar_aba("Cadastro_Alunos")
    base_fin = carregar_e_normalizar_aba("Controle_Financeiro")
    base_age = carregar_e_normalizar_aba("Agendamento_Aulas")
    base_tre = carregar_e_normalizar_aba("Prescricao_Treinos")

    # -----------------------------------------------------------------
    # MÓDULO 1: DASHBOARD GERAL
    # -----------------------------------------------------------------
    if menu_treinador == "📊 Dashboard Geral":
        st.subheader("Indicadores Operacionais em Tempo Real")
        
        # Tratamento do faturamento usando busca por coluna normalizada (minúscula)
        faturamento = 0.0
        if not base_fin.empty:
            col_valor = [c for c in base_fin.columns if 'valor' in c]
            if col_valor:
                base_fin['val_num'] = base_fin[col_valor[0]].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
                faturamento = base_fin['val_num'].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            # Conta apenas os IDs válidos de alunos (contendo alu)
            col_id_aluno = [c for c in base_cad.columns if 'id_aluno' in c] if not base_cad.empty else []
            total_alunos = len(base_cad[base_cad[col_id_aluno[0]].str.contains('ALU', na=False, case=False)]) if col_id_aluno else 0
            st.metric("Alunos Cadastrados (Total)", total_alunos)
        with col2:
            st.metric("Faturamento Previsto (Maio)", f"R$ {faturamento:,.2f}")
        with col3:
            # Conta os agendamentos ativos válidos (contendo age)
            col_id_age = [c for c in base_age.columns if 'id_agendamento' in c] if not base_age.empty else []
            total_aulas = len(base_age[base_age[col_id_age[0]].str.contains('AGE', na=False, case=False)]) if col_id_age else 0
            st.metric("Total de Aulas Agendadas", total_aulas)
            
        st.write("---")
        st.subheader("Visualização Cadastral Primária (Base de Alunos Ativos)")
        if not base_cad.empty:
            st.dataframe(base_cad, use_container_width=True)
        else:
            st.warning("Sem dados cadastrais para exibir na planilha.")

    # -----------------------------------------------------------------
    # MÓDULO 2: FINANCEIRO DETALHADO
    # -----------------------------------------------------------------
    elif menu_treinador == "💰 Financeiro Detalhado":
        st.subheader("Gestão de Receitas & Cobranças")
        
        if not base_fin.empty:
            col_valor = [c for c in base_fin.columns if 'valor' in c]
            col_status = [c for c in base_fin.columns if 'status' in c]
            
            if col_valor:
                base_fin['val_num'] = base_fin[col_valor[0]].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
                
                if col_status:
                    resumo_grafico = base_fin.groupby(col_status[0])['val_num'].sum()
                    st.bar_chart(resumo_grafico)
            
            st.write("---")
            st.subheader("Lista de Cobranças Estruturadas")
            st.dataframe(base_fin, use_container_width=True)
        else:
            st.info("Aguardando preenchimento de lançamentos financeiros na planilha.")

    # -----------------------------------------------------------------
    # MÓDULO 3: AGENDA DE ATENDIMENTOS
    # -----------------------------------------------------------------
    elif menu_treinador == "📅 Agenda de Atendimentos":
        st.subheader("Cronograma de Aulas Semanais")
        
        if not base_age.empty:
            col_data = [c for c in base_age.columns if 'data' in c]
            
            dias_semana = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
            dia_filtro = st.selectbox("Filtrar por Dia da Semana:", ["Todos"] + dias_semana)
            
            if dia_filtro != "Todos" and col_data:
                agenda_filtrada = base_age[base_age[col_data[0]].str.strip().str.lower() == dia_filtro.lower()]
            else:
                agenda_filtrada = base_age
                
            st.dataframe(agenda_filtrada, use_container_width=True)
        else:
            st.info("Aguardando inserção de agendamentos de aulas na planilha.")

    # -----------------------------------------------------------------
    # MÓDULO 4: PRESCRIÇÃO DE TREINOS
    # -----------------------------------------------------------------
    elif menu_treinador == "🏋️ Prescrição de Treinos":
        st.subheader("Central Técnica de Exercícios")
        
        col_nome_cad = [c for c in base_cad.columns if 'nome' in c] if not base_cad.empty else []
        
        if col_nome_cad:
            aluno_alvo = st.selectbox("Selecione o Aluno para puxar a Ficha:", base_cad[col_nome_cad[0]].tolist())
            
            col_id_cad = [c for c in base_cad.columns if 'id_aluno' in c]
            id_aluno_alvo = base_cad[base_cad[col_nome_cad[0]] == aluno_alvo][col_id_cad[0]].values[0]
            
            st.write(f"Buscando exercícios vinculados ao código do aluno: **{id_aluno_alvo.upper()}**")
            
            col_id_tre = [c for c in base_tre.columns if 'id_aluno' in c] if not base_tre.empty else []
            
            if col_id_tre:
                treino_filtrado = base_tre[base_tre[col_id_tre[0]].astype(str).str.strip().str.lower() == id_aluno_alvo.strip().lower()]
                
                col_nome_exe = [c for c in base_tre.columns if 'exercicio' in c or 'nome_ex' in c]
                if treino_filtrado.empty or (col_nome_exe and treino_filtrado[col_nome_exe[0]].isna().all()):
                    st.info(f"O aluno está indexado corretamente, mas a tabela de exercícios (EXE) está vazia para ele na planilha.")
                else:
                    st.dataframe(treino_filtrado, use_container_width=True)
            else:
                st.warning("A aba de Prescrição de Treinos não pôde ser lida ou está sem colunas estruturadas.")

# =====================================================================
# 🏃 PORTAL DO ALUNO (TEAM MUNIZ)
# =====================================================================
elif perfil == "🏃 Área do Aluno":
    st.title("Portal do Aluno - Team Muniz")
    
    base_cad = carregar_e_normalizar_aba("Cadastro_Alunos")
    col_nome_cad = [c for c in base_cad.columns if 'nome' in c] if not base_cad.empty else []
    
    if col_nome_cad:
        aluno_logado = st.selectbox("Quem está acessando o portal?", base_cad[col_nome_cad[0]].dropna().tolist())
        col_id_cad = [c for c in base_cad.columns if 'id_aluno' in c]
        id_aluno_logado = base_cad[base_cad[col_nome_cad[0]] == aluno_logado][col_id_cad[0]].values[0]
        
        st.write(f"Seu Código de Aluno: **{id_aluno_logado.upper()}**")
        
        tab_t, tab_e, tab_f = st.tabs(["🏋️ Meu Treino", "📈 Minha Evolução", "💳 Meu Financeiro"])
        
        with tab_t:
            base_tre = carregar_e_normalizar_aba("Prescricao_Treinos")
            col_id_tre = [c for c in base_tre.columns if 'id_aluno' in c] if not base_tre.empty else []
            if col_id_tre:
                treino_aluno = base_tre[base_tre[col_id_tre[0]].astype(str).str.strip().str.lower() == id_aluno_logado.strip().lower()]
                st.dataframe(treino_aluno, use_container_width=True)
                    
        with tab_e:
            base_bio = carregar_e_normalizar_aba("Historico_Bioimpedancia")
            col_id_bio = [c for c in base_bio.columns if 'id_aluno' in c] if not base_bio.empty else []
            if col_id_bio:
                bio_aluno = base_bio[base_bio[col_id_bio[0]].astype(str).str.strip().str.lower() == id_aluno_logado.strip().lower()]
                st.dataframe(bio_aluno, use_container_width=True)
                
        with tab_f:
            base_fin = carregar_e_normalizar_aba("Controle_Financeiro")
            col_id_fin = [c for c in base_fin.columns if 'id_aluno' in c] if not base_fin.empty else []
            if col_id_fin:
                fin_aluno = base_fin[base_fin[col_id_fin[0]].astype(str).str.strip().str.lower() == id_aluno_logado.strip().lower()]
                st.dataframe(fin_aluno, use_container_width=True)
