import streamlit as st
import pandas as pd
import urllib.parse

# Configuração da página do aplicativo
st.set_page_config(
    page_title="Team Muniz - Sistema de Gestão",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Visual Premium (Preto de fundo e detalhes em Dourado)
st.markdown("""
    <style>
    .main { background-color: #0e0e0e; color: #FFFFFF; }
    .sidebar .sidebar-content { background-color: #161616; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'Helvetica', sans-serif; }
    div.stButton > button:first-child {
        background-color: #D4AF37; color: #000000; font-weight: bold; border-radius: 6px; width: 100%;
    }
    .kpi-box { background-color: #1c1c1c; padding: 20px; border-radius: 8px; border-left: 4px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://docs.google.com/spreadsheets/d/1tqfyKLolU1P7AVOYw7vJcOtG19QOM9tSVu6OK09j668/export?format=csv&gid="

GIDS = {
    "Cadastro_Alunos": "1168521543",
    "Controle_Financeiro": "439294975",
    "Agendamento_Aulas": "1486576823",
    "Historico_Bioimpedancia": "2134988451",
    "Prescricao_Treinos": "1619478144",
    "Fluxo_Caixa_Geral": "1809059737"
}

def carregar_dados(aba_nome):
    url = URL_BASE + GIDS[aba_nome]
    try:
        df = pd.read_csv(url)
        df = df.dropna(how='all')
        df.columns = df.columns.astype(str).str.replace(r'\\', '', regex=True).str.replace('*', '', regex=False).str.strip()
        return df
    except Exception as e:
        return pd.DataFrame()

# --- CARGA GLOBAL DAS ABAS ---
df_alunos = carregar_dados("Cadastro_Alunos")
df_financeiro = carregar_dados("Controle_Financeiro")
df_agenda = carregar_dados("Agendamento_Aulas")
df_treinos = carregar_dados("Prescricao_Treinos")
df_bio = carregar_dados("Historico_Bioimpedancia")

# Tratamento Numérico Financeiro
if not df_financeiro.empty and 'Valor_Cobrado' in df_financeiro.columns:
    df_financeiro['Valor_Num'] = df_financeiro['Valor_Cobrado'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
else:
    df_financeiro['Valor_Num'] = 0.0

# --- SEGURANÇA E SEPARAÇÃO DE PERFIS NO MENU LATERAL ---
st.sidebar.title("🏆 Team Muniz Hub")
st.sidebar.write("---")

perfil = st.sidebar.radio("Selecione o Portal de Acesso:", ["🏃 Portal do Aluno", "👑 Painel do Treinador"])

# =====================================================================
# 👑 PORTAL DO TREINADOR (FÁBIO) - PROTEGIDO POR SENHA
# =====================================================================
if perfil == "👑 Painel do Treinador":
    st.sidebar.write("---")
    senha_treinador = st.sidebar.text_input("Chave de Acesso do Treinador:", type="password")
    
    # Defina sua senha pessoal aqui (Exemplo: "muniz2026")
    if senha_treinador == "muniz2026":
        st.sidebar.success("Acesso Autorizado!")
        
        menu = st.sidebar.selectbox(
            "Selecione o Módulo Administrativo:",
            ["📊 Dashboard & Cadastro", "💰 Cobrança & Receitas", "📅 Organização da Agenda", "🏋️ Central de Exercícios"]
        )
        
        # -------------------------------------------------------------
        # MÓDULO: DASHBOARD & CADASTRO
        # -------------------------------------------------------------
        if menu == "📊 Dashboard & Cadastro":
            st.title("Indicadores e Perfis de Clientes")
            
            # Cards de Performance Superior
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"<div class='kpi-box'><span style='color:gray;'>Alunos Ativos</span><br><h2>{len(df_alunos)}</h2></div>", unsafe_allow_html=True)
            with c2:
                faturamento = df_financeiro['Valor_Num'].sum()
                st.markdown(f"<div class='kpi-box'><span style='color:gray;'>Faturamento de Maio</span><br><h2>R$ {faturamento:,.2f}</h2></div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='kpi-box'><span style='color:gray;'>Sessões Agendadas</span><br><h2>{len(df_agenda)}</h2></div>", unsafe_allow_html=True)
            
            st.write("---")
            st.subheader("Filtro Individual de Aluno (Dados Cadastrais)")
            
            aluno_selecionado = st.selectbox("Selecione o Aluno para Ver a Ficha Cadastral:", df_alunos['Nome_Completo'].tolist())
            dados_do_aluno = df_alunos[df_alunos['Nome_Completo'] == aluno_selecionado].iloc[0]
            
            # Card Customizado com as infos do aluno escolhido
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Código de Identificação:** {dados_do_aluno['ID_Aluno']}")
                st.markdown(f"**WhatsApp:** {dados_do_aluno['WhatsApp']}")
            with col_b:
                st.markdown(f"**Modalidade Contratada:** {dados_do_aluno['Modalidade']}")
                st.markdown(f"**Status no Sistema:** {dados_do_aluno['Status_Aluno']}")
                
            st.write("---")
            with st.expander("Ver Planilha Completa de Cadastros"):
                st.dataframe(df_alunos, use_container_width=True)

        # -------------------------------------------------------------
        # MÓDULO: COBRANÇA & RECEITAS
        # -------------------------------------------------------------
        elif menu == "💰 Cobrança & Receitas":
            st.title("Gestão de Receitas (Gráfico Pizza e Filtros)")
            
            # Gráfico de Pizza de faturamento por status
            if 'Status_Pagamento' in df_financeiro.columns:
                resumo_pizza = df_financeiro.groupby('Status_Pagamento')['Valor_Num'].sum()
                st.write("### Divisão de Receitas por Categoria")
                st.pie_chart(resumo_pizza)
            
            st.write("---")
            st.subheader("Relatórios Dinâmicos por Botão")
            
            # Filtros por botões horizontais
            col_b1, col_b2, col_b3 = st.columns(3)
            filtro_financeiro = "Todos"
            with col_b1:
                if st.button("Ver Apenas Cobranças Pendentes"): filtro_financeiro = "Pendente"
            with col_b2:
                if st.button("Ver Apenas Mensalidades Pagas"): filtro_financeiro = "Pago"
            with col_b3:
                if st.button("Redefinir Filtros (Ver Tudo)"): filtro_financeiro = "Todos"
            
            if filtro_financeiro != "Todos":
                df_exibicao_fin = df_financeiro[df_financeiro['Status_Pagamento'] == filtro_financeiro]
            else:
                df_exibicao_fin = df_financeiro
                
            st.dataframe(df_exibicao_fin[['ID_Lancamento', 'ID_Aluno', 'Nome_Aluno', 'Mes_Referencia', 'Valor_Cobrado', 'Status_Pagamento']], use_container_width=True)
            
            # Central de Automação de WhatsApp para devedores
            st.write("---")
            st.subheader("⚠️ Central de Mensagens Automáticas de Cobrança")
            
            devedores = df_financeiro[df_financeiro['Status_Pagamento'] == 'Pendente']
            
            if not devedores.empty:
                for idx, row in devedores.iterrows():
                    # Localiza o celular do devedor batendo os IDs
                    aluno_info = df_alunos[df_alunos['ID_Aluno'] == row['ID_Aluno']]
                    if not aluno_info.empty:
                        telefone = str(aluno_info.iloc[0]['WhatsApp']).strip()
                        nome_aluno = row['Nome_Aluno']
                        valor = row['Valor_Cobrado']
                        
                        # Texto elegante de cobrança da assessoria
                        mensagem = f"Olá {nome_aluno}, tudo bem? Passando para lembrar que a mensalidade da sua assessoria Team Muniz ({valor}) está aberta. Caso já tenha realizado o pagamento, desconsidere! 💪"
                        mensagem_codificada = urllib.parse.quote(mensagem)
                        
                        # Link da API Oficial do Zap
                        link_whatsapp = f"https://api.whatsapp.com/send?phone={telefone}&text={mensagem_codificada}"
                        
                        col_nome, col_link = st.columns([4, 1])
                        with col_nome:
                            st.write(f"🔴 **{nome_aluno}** possui fatura pendente de {valor}.")
                        with col_link:
                            st.markdown(f"[📩 Cobrar no Zap]({link_whatsapp})", unsafe_allow_html=True)
            else:
                st.success("Sensacional! Nenhum aluno com pendência financeira ativa.")

        # -------------------------------------------------------------
        # MÓDULO: AGENDA DE ATENDIMENTOS (Agrupados por Botão Expandível)
        # -------------------------------------------------------------
        elif menu == "📅 Organização da Agenda":
            st.title("Agenda de Atendimentos Presenciais")
            
            # Divisão por Grupos Técnicos das Categorias
            tipo_agenda = st.radio("Selecione a Modalidade da Agenda:", ["Treinamento Fixo Individual", "Treinamento em Grupo"])
            
            if tipo_agenda == "Treinamento Fixo Individual":
                df_filtrado_agenda = df_agenda[df_agenda['Observacoes_Agenda'] == 'Treino Fixo']
            else:
                df_filtrado_agenda = df_agenda[df_agenda['Observacoes_Agenda'] == 'Treino em Grupo']
                
            # Agrupamento por Botões (Expanders) por Aluno
            if not df_filtrado_agenda.empty:
                lista_alunos_agenda = df_filtrado_agenda['Nome_Aluno'].unique()
                
                for aluno in lista_alunos_agenda:
                    with st.expander(f"👤 Ver Horários da Agenda de: {aluno}"):
                        dados_agenda_aluno = df_filtrado_agenda[df_filtrado_agenda['Nome_Aluno'] == aluno]
                        st.dataframe(dados_agenda_aluno[['ID_Agendamento', 'Data_Aula', 'Horario_Inicio', 'Horario_Fim', 'Status_Aula']], use_container_width=True)
            else:
                st.info("Nenhum horário registrado para esta modalidade.")

        # -------------------------------------------------------------
        # MÓDULO: PRESCRIÇÃO DE TREINOS
        # -------------------------------------------------------------
        elif menu == "🏋️ Central de Exercícios":
            st.title("Fichas de Exercícios Técnicos")
            
            aluno_treino_sel = st.selectbox("Selecione o Aluno para Abrir a Ficha Tática:", df_alunos['Nome_Completo'].tolist())
            id_aluno_sel = df_alunos[df_alunos['Nome_Completo'] == aluno_treino_sel]['ID_Aluno'].values[0]
            
            with st.expander(f"📂 Abrir Ficha Completa (ID: {id_aluno_sel})"):
                if not df_treinos.empty and 'ID_Aluno' in df_treinos.columns:
                    treino_filtrado_muniz = df_treinos[df_treinos['ID_Aluno'] == id_aluno_sel]
                    
                    if treino_filtrado_muniz.empty or treino_filtrado_muniz['Nome_Exercicio'].isna().all():
                        st.info("A ficha deste aluno está indexada, mas não há nenhum exercício (EXE) digitado nela ainda.")
                    else:
                        st.dataframe(treino_filtrado_muniz, use_container_width=True)
    else:
        st.sidebar.error("Chave incorreta. Digite a senha administrativa correta.")

# =====================================================================
# 🏃 PORTAL DO ALUNO - COMPACTO COM VALIDAÇÃO DE SEGURANÇA POR WHATSAPP
# =====================================================================
elif perfil == "🏃 Portal do Aluno":
    st.title("Portal do Aluno - Team Muniz")
    st.write("Insira suas credenciais de segurança fornecidas pela assessoria para liberar sua ficha de treinos.")
    
    # Validação dupla de segurança
    input_id = st.text_input("Digite seu Código de Acesso (ID Aluno):", placeholder="Ex: ALU001")
    input_tel = st.text_input("Digite seu Telefone Cadastrado (Apenas números com DDD):", placeholder="Ex: 5511999999999")
    
    if input_id and input_tel:
        # Busca na planilha se existe um aluno com esse ID e esse número exato
        aluno_validado = df_alunos[(df_alunos['ID_Aluno'].astype(str) == input_id.strip()) & (df_alunos['WhatsApp'].astype(str) == input_tel.strip())]
        
        if not aluno_validado.empty:
            nome_aluno_logado = aluno_validado.iloc[0]['Nome_Completo']
            st.success(f"Bem-vindo de volta, {nome_aluno_logado}!")
            
            t_treino, t_evolucao, t_fin = st.tabs(["🏋️ Minha Ficha de Exercícios", "📈 Minha Evolução Física", "💳 Meu Financeiro"])
            
            with t_treino:
                st.subheader("Treino do Dia")
                if not df_treinos.empty:
                    treino_aluno = df_treinos[df_treinos['ID_Aluno'] == input_id.strip()].dropna(subset=['Nome_Exercicio'])
                    if not treino_aluno.empty:
                        st.dataframe(treino_aluno[['Divisao_Treino', 'Grupo_Muscular', 'Nome_Exercicio', 'Series', 'Repeticoes', 'Descanso', 'Link_Video_Execucao', 'Observacoes_Tecnicas']], use_container_width=True)
                    else:
                        st.info("Seu plano tático de treino está sendo montado pela equipe Team Muniz!")
                        
            with t_evolucao:
                st.subheader("Histórico de Avaliações")
                if not df_bio.empty:
                    bio_aluno = df_bio[df_bio['ID_Aluno'] == input_id.strip()]
                    st.dataframe(bio_aluno, use_container_width=True)
                    
            with t_fin:
                st.subheader("Minhas Mensalidades")
                if not df_financeiro.empty:
                    fin_aluno = df_financeiro[df_financeiro['ID_Aluno'] == input_id.strip()]
                    st.dataframe(fin_aluno[['Mes_Referencia', 'Valor_Cobrado', 'Data_Vencimento', 'Status_Pagamento']], use_container_width=True)
        else:
            st.error("Credenciais de segurança não coincidem. Verifique o ID ou o Telefone digitado.")
