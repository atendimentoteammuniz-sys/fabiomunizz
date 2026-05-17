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

# ATUALIZAÇÃO CRÍTICA: GIDs Reais extraídos diretamente da sua planilha ativa
GIDS = {
    "Cadastro_Alunos": "0",
    "Controle_Financeiro": "1755100010",
    "Agendamento_Aulas": "1419409890",
    "Historico_Bioimpedancia": "107771764",
    "Prescricao_Treinos": "1459524450",
    "Fluxo_Caixa_Geral": "39682540"
}

def carregar_e_normalizar_aba(nome_aba):
    url = URL_BASE + GIDS[nome_aba]
    try:
        # Lê a aba como texto para evitar quebras de formatação
        df = pd.read_csv(url, dtype=str)
        df = df.dropna(how='all') # Remove linhas fantasmas
        
        # Limpa os nomes das colunas (remove espaços extras e joga para minúsculo para busca segura)
        df.columns = df.columns.astype(str).str.strip().str.lower()
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
    
    # Carregamento dinâmico das bases
    base_cad = carregar_e_normalizar_aba("Cadastro_Alunos")
    base_fin = carregar_e_normalizar_aba("Controle_Financeiro")
    base_age = carregar_e_normalizar_aba("Agendamento_Aulas")
    base_tre = carregar_e_normalizar_aba("Prescricao_Treinos")

    # -----------------------------------------------------------------
    # MÓDULO 1: DASHBOARD GERAL
    # -----------------------------------------------------------------
    if menu_treinador == "📊 Dashboard Geral":
        st.subheader("Indicadores Operacionais em Tempo Real")
        
        faturamento = 0.0
        if not base_fin.empty:
            col_valor = [c for c in base_fin.columns if 'valor_cobrado' in c or 'valor' in c]
            if col_valor:
                # Trata R$, pontos e vírgulas para somar corretamente
                base_fin['val_num'] = base_fin[col_valor[0]].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
                faturamento = base_fin['val_num'].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            col_id_aluno = [c for c in base_cad.columns if 'id_aluno' in c]
            total_alunos = len(base_cad[base_cad[col_id_aluno[0]].str.contains('ALU', na=False, case=False)]) if col_id_aluno else 0
            st.metric("Alunos Cadastrados (Total)", total_alunos)
        with col2:
            st.metric("Faturamento Previsto (Maio)", f"R$ {faturamento:,.2f}")
        with col3:
            col_id_age = [c for c in base_age.columns if 'id_agendamento' in c]
            total_aulas = len(base_age[base_age[col_id_age[0]].str.contains('AGE', na=False, case=False)]) if col_id_age else 0
            st.metric("Total de Aulas Agendadas", total_aulas)
            
        st.write("---")
        st.subheader("Visualização Cadastral Primária (Base de Alunos Ativos)")
        if not base_cad.empty:
            st.dataframe(base_cad, use_container_width=True)
        else:
            st.warning("Aguardando carregamento da base de alunos.")

    # -----------------------------------------------------------------
    # MÓDULO 2: FINANCEIRO DETALHADO
    # -----------------------------------------------------------------
    elif menu_treinador == "💰 Financeiro Detalhado":
        st.subheader("Gestão de Receitas & Cobranças")
        
        if not base_fin.empty:
            col_valor = [c for c in base_fin.columns if 'valor_cobrado' in c]
            col_status = [c for c in base_fin.columns if 'status_pagamento' in c]
            
            if col_valor:
                base_fin['val_num'] = base_fin[col_valor[0]].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
                
                if col_status:
                    resumo_grafico = base_fin.groupby(col_status[0])['val_num'].sum()
                    st.bar_chart(resumo_grafico)
            
            st.write("---")
            st.subheader("Lista de Cobranças Estruturadas (Chave: ID_Lancamento)")
            st.dataframe(base_fin, use_container_width=True)
        else:
            st.info("Nenhum dado financeiro encontrado.")

    # -----------------------------------------------------------------
    # MÓDULO 3: AGENDA DE ATENDIMENTOS
    # -----------------------------------------------------------------
    elif menu_treinador == "📅 Agenda de Atendimentos":
        st.subheader("Cronograma de Aulas Semanais")
        
        if not base_age.empty:
            col_data = [c for c in base_age.columns if 'data_aula' in c]
            
            dias_semana = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
            dia_filtro = st.selectbox("Filtrar por Dia da Semana:", ["Todos"] + dias_semana)
            
            if dia_filtro != "Todos" and col_data:
                agenda_filtrada = base_age[base_age[col_data[0]].str.strip().str.lower() == dia_filtro.lower()]
            else:
                agenda_filtrada = base_age
                
            st.dataframe(agenda_filtrada, use_container_width=True)
        else:
            st.info("Nenhum agendamento ativo encontrado.")

    # -----------------------------------------------------------------
    # MÓDULO 4: PRESCRIÇÃO DE TREINOS
    # -----------------------------------------------------------------
    elif menu_treinador == "🏋️ Prescrição de Treinos":
        st.subheader("Central Técnica de Exercícios")
        
        col_nome_cad = [c for c in base_cad.columns if 'nome_completo' in c or 'nome' in c]
        
        if col_nome_cad and not base_cad.empty:
            aluno_alvo = st.selectbox("Selecione o Aluno para puxar a Ficha:", base_cad[col_nome_cad[0]].tolist())
            
            col_id_cad = [c for c in base_cad.columns if 'id_aluno' in c]
            id_aluno_alvo = base_cad[base_cad[col_nome_cad[0]] == aluno_alvo][col_id_cad[0]].values[0]
            
            st.write(f"Buscando exercícios vinculados ao código do aluno: **{id_aluno_alvo.upper()}**")
            
            col_id_tre = [c for c in base_tre.columns if 'id_aluno' in c]
            
            if col_id_tre and not base_tre.empty:
                treino_filtrado = base_tre[base_tre[col_id_tre[0]].astype(str).str.strip().str.lower() == id_aluno_alvo.strip().lower()]
                
                col_nome_exe = [c for c in base_tre.columns if 'nome_exercicio' in c or 'exercicio' in c]
                if treino_filtrado.empty or (col_nome_exe and treino_filtrado[col_nome_exe[0]].isna().all()):
                    st.info(f"O aluno está indexado, mas a tabela de exercícios (EXE) está vazia para ele.")
                else:
                    st.dataframe(treino_filtrado, use_container_width=True)
            else:
                st.warning("A aba de Prescrição de Treinos está vazia ou desalinhada.")

# =====================================================================
# 🏃 PORTAL DO ALUNO (TEAM MUNIZ)
# =====================================================================
elif perfil == "🏃 Área do Aluno":
    st.title("Portal do Aluno - Team Muniz")
    
    col_nome_cad = [c for c in base_cad.columns if 'nome_completo' in c or 'nome' in c]
    
    if col_nome_cad and not base_cad.empty:
        aluno_logado = st.selectbox("Quem está acessando o portal?", base_cad[col_nome_cad[0]].dropna().tolist())
        col_id_cad = [c for c in base_cad.columns if 'id_aluno' in c]
        id_aluno_logado = base_cad[base_cad[col_nome_cad[0]] == aluno_logado][col_id_cad[0]].values[0]
        
        st.write(f"Seu Código de Aluno: **{id_aluno_logado.upper()}**")
        
        tab_t, tab_e, tab_f = st.tabs(["🏋️ Meu Treino", "📈 Minha Evolução", "💳 Meu Financeiro"])
        
        with tab_t:
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
            col_id_fin = [c for c in base_fin.columns if 'id_aluno' in c] if not base_fin.empty else []
            if col_id_fin:
                fin_aluno = base_fin[base_fin[col_id_fin[0]].astype(str).str.strip().str.lower() == id_aluno_logado.strip().lower()]
                st.dataframe(fin_aluno, use_container_width=True)
