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

# Estilização Visual Premium
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
        
        # Super Limpeza de Cabeçalhos: Remove asteriscos, barras, espaços e força padronização
        df.columns = df.columns.astype(str).str.replace(r'\\', '', regex=True).str.replace('*', '', regex=False).str.strip()
        # Substitui espaços por underline para bater com o código se você tiver escrito "Nome Completo" na planilha
        df.columns = df.columns.str.replace(' ', '_', regex=False)
        
        return df
    except Exception as e:
        return pd.DataFrame()

# --- CARGA GLOBAL DAS ABAS ---
df_alunos = carregar_dados("Cadastro_Alunos")
df_financeiro = carregar_dados("Controle_Financeiro")
df_agenda = carregar_dados("Agendamento_Aulas")
df_treinos = carregar_dados("Prescricao_Treinos")
df_bio = carregar_dados("Historico_Bioimpedancia")

# Tratamento Numérico Financeiro Seguro
if not df_financeiro.empty and 'Valor_Cobrado' in df_financeiro.columns:
    df_financeiro['Valor_Num'] = df_financeiro['Valor_Cobrado'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
else:
    if not df_financeiro.empty:
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
            
            # Cards de Performance Superior Protegidos
            total_alunos_count = len(df_alunos) if not df_alunos.empty else 0
            faturamento_total = df_financeiro['Valor_Num'].sum() if not df_financeiro.empty and 'Valor_Num' in df_financeiro.columns else 0.0
            total_sessoes = len(df_agenda) if not df_agenda.empty else 0
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"<div class='kpi-box'><span style='color:gray;'>Alunos Ativos</span><br><h2>{total_alunos_count}</h2></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='kpi-box'><span style='color:gray;'>Faturamento de Maio</span><br><h2>R$ {faturamento_total:,.2f}</h2></div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='kpi-box'><span style='color:gray;'>Sessões Agendadas</span><br><h2>{total_sessoes}</h2></div>", unsafe_allow_html=True)
            
            st.write("---")
            st.subheader("Filtro Individual de Aluno (Dados Cadastrais)")
            
            # PROTEÇÃO DO KEYERROR AQUI: Verifica se a tabela e a coluna existem
            if not df_alunos.empty and 'Nome_Completo' in df_alunos.columns:
                lista_nomes = df_alunos['Nome_Completo'].dropna().tolist()
                
                if lista_nomes:
                    aluno_selecionado = st.selectbox("Selecione o Aluno para Ver a Ficha Cadastral:", lista_nomes)
                    dados_do_aluno = df_alunos[df_alunos['Nome_Completo'] == aluno_selecionado].iloc[0]
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**Código de Identificação:** {dados_do_aluno.get('ID_Aluno', 'N/A')}")
                        st.markdown(f"**WhatsApp:** {dados_do_aluno.get('WhatsApp', 'N/A')}")
                    with col_b:
                        st.markdown(f"**Modalidade Contratada:** {dados_do_aluno.get('Modalidade', 'N/A')}")
                        st.markdown(f"**Status no Sistema:** {dados_do_aluno.get('Status_Aluno', 'N/A')}")
                else:
                    st.warning("Nenhum nome de aluno válido foi encontrado na coluna 'Nome_Completo'.")
            else:
                st.error("Erro estrutural: A coluna 'Nome_Completo' não foi encontrada na aba Cadastro_Alunos ou a aba está vazia. Verifique o cabeçalho na planilha.")
                if not df_alunos.empty:
                    st.write("Colunas detectadas no seu Sheets atual:", list(df_alunos.columns))
                
            st.write("---")
            with st.expander("Ver Planilha Completa de Cadastros"):
                st.dataframe(df_alunos, use_container_width=True)

        # -------------------------------------------------------------
        # MÓDULO: COBRANÇA & RECEITAS
        # -------------------------------------------------------------
        elif menu == "💰 Cobrança & Receitas":
            st.title("Gestão de Receitas (Gráfico Pizza e Filtros)")
            
            if not df_financeiro.empty and 'Status_Pagamento' in df_financeiro.columns and 'Valor_Num' in df_financeiro.columns:
                resumo_pizza = df_financeiro.groupby('Status_Pagamento')['Valor_Num'].sum()
                st.write("### Divisão de Receitas por Categoria")
                st.pie_chart(resumo_pizza)
                
                st.write("---")
                st.subheader("Relatórios Dinâmicos por Botão")
                
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
                    
                colunas_fin_exibir = [c for c in ['ID_Lancamento', 'ID_Aluno', 'Nome_Aluno', 'Mes_Referencia', 'Valor_Cobrado', 'Status_Pagamento'] if c in df_exibicao_fin.columns]
                st.dataframe(df_exibicao_fin[colunas_fin_exibir], use_container_width=True)
                
                # Central de Automação de WhatsApp para devedores
                st.write("---")
                st.subheader("⚠️ Central de Mensagens Automáticas de Cobrança")
                
                devedores = df_financeiro[df_financeiro['Status_Pagamento'] == 'Pendente']
                
                if not devedores.empty and not df_alunos.empty and 'ID_Aluno' in df_alunos.columns:
                    for idx, row in devedores.iterrows():
                        aluno_info = df_alunos[df_alunos['ID_Aluno'] == row['ID_Aluno']]
                        if not aluno_info.empty and 'WhatsApp' in aluno_info.columns:
                            telefone = str(aluno_info.iloc[0]['WhatsApp']).strip()
                            nome_aluno = row.get('Nome_Aluno', 'Aluno')
                            valor = row.get('Valor_Cobrado', 'Valor Corrente')
                            
                            mensagem = f"Olá {nome_aluno}, tudo bem? Passando para lembrar que a mensalidade da sua assessoria Team Muniz ({valor}) está aberta. Caso já tenha realizado o pagamento, desconsidere! 💪"
                            mensagem_codificada = urllib.parse.quote(mensagem)
                            
                            link_whatsapp = f"https://api.whatsapp.com/send?phone={telefone}&text={mensagem_codificada}"
                            
                            col_nome, col_link = st.columns([4, 1])
                            with col_nome:
                                st.write(f"🔴 **{nome_aluno}** possui fatura pendente de {valor}.")
                            with col_link:
                                st.markdown(f"[📩 Cobrar no Zap]({link_whatsapp})", unsafe_allow_html=True)
                else:
                    st.info("Nenhuma cobrança pendente identificada no momento.")
            else:
                st.error("A aba Controle_Financeiro está vazia ou não possui as colunas estruturais básicas.")

        # -------------------------------------------------------------
        # MÓDULO: AGENDA DE ATENDIMENTOS
        # -------------------------------------------------------------
        elif menu == "📅 Organização da Agenda":
            st.title("Agenda de Atendimentos Presenciais")
            
            if not df_agenda.empty and 'Observacoes_Agenda' in df_agenda.columns and 'Nome_Aluno' in df_agenda.columns:
                tipo_agenda = st.radio("Selecione a Modalidade da Agenda:", ["Treinamento Fixo Individual", "Treinamento em Grupo"])
                
                if tipo_agenda == "Treinamento Fixo Individual":
                    df_filtrado_agenda = df_agenda[df_agenda['Observacoes_Agenda'] == 'Treino Fixo']
                else:
                    df_filtrado_agenda = df_agenda[df_agenda['Observacoes_Agenda'] == 'Treino em Grupo']
                    
                if not df_filtrado_agenda.empty:
                    lista_alunos_agenda = df_filtrado_agenda['Nome_Aluno'].unique()
                    
                    for aluno in lista_alunos_agenda:
                        with st.expander(f"👤 Ver Horários da Agenda de: {aluno}"):
                            dados_agenda_aluno = df_filtrado_agenda[df_filtrado_agenda['Nome_Aluno'] == aluno]
                            colunas_age_exibir = [c for c in ['ID_Agendamento', 'Data_Aula', 'Horario_Inicio', 'Horario_Fim', 'Status_Aula'] if c in dados_agenda_aluno.columns]
                            st.dataframe(dados_agenda_aluno[colunas_age_exibir], use_container_width=True)
                else:
                    st.info("Nenhum horário registrado para esta modalidade.")
            else:
                st.error("A aba de Agendamento_Aulas está inacessível ou sem as colunas 'Observacoes_Agenda' e 'Nome_Aluno'.")

        # -------------------------------------------------------------
        # MÓDULO: PRESCRIÇÃO DE TREINOS
        # -------------------------------------------------------------
        elif menu == "🏋️ Central de Exercícios":
            st.title("Fichas de Exercícios Técnicos")
            
            if not df_alunos.empty and 'Nome_Completo' in df_alunos.columns:
                aluno_treino_sel = st.selectbox("Selecione o Aluno para Abrir a Ficha Tática:", df_alunos['Nome_Completo'].tolist())
                id_aluno_sel = df_alunos[df_alunos['Nome_Completo'] == aluno_treino_sel]['ID_Aluno'].values[0]
                
                with st.expander(f"📂 Abrir Ficha Completa (ID: {id_aluno_sel})"):
                    if not df_treinos.empty and 'ID_Aluno' in df_treinos.columns:
                        treino_filtrado_muniz = df_treinos[df_treinos['ID_Aluno'] == id_aluno_sel]
                        
                        if treino_filtrado_muniz.empty:
                            st.info("A ficha deste aluno está indexada, mas não há nenhum exercício (EXE) digitado nela ainda.")
                        else:
                            st.dataframe(treino_filtrado_muniz, use_container_width=True)
                    else:
                        st.warning("A aba de Prescrição de Treinos ainda não possui colunas preenchidas ou falta a coluna 'ID_Aluno'.")
            else:
                st.error("Base de dados de cadastro indisponível para selecionar alunos.")
                
    elif senha_treinador != "":
        st.sidebar.error("Chave incorreta. Digite a senha administrativa correta.")

# =====================================================================
# 🏃 PORTAL DO ALUNO - COMPACTO COM VALIDAÇÃO DE SEGURANÇA
# =====================================================================
elif perfil == "🏃 Portal do Aluno":
    st.title("Portal do Aluno - Team Muniz")
    st.write("Insira suas credenciais de segurança fornecidas pela assessoria para liberar sua ficha de treinos.")
    
    input_id = st.text_input("Digite seu Código de Acesso (ID Aluno):", placeholder="Ex: ALU001")
    input_tel = st.text_input("Digite seu Telefone Cadastrado (Apenas números com DDD):", placeholder="Ex: 5511999999999")
    
    if input_id and input_tel and not df_alunos.empty and 'ID_Aluno' in df_alunos.columns and 'WhatsApp' in df_alunos.columns:
        aluno_validado = df_alunos[(df_alunos['ID_Aluno'].astype(str) == input_id.strip()) & (df_alunos['WhatsApp'].astype(str) == input_tel.strip())]
        
        if not aluno_validado.empty:
            nome_aluno_logado = aluno_validado.iloc[0]['Nome_Completo'] if 'Nome_Completo' in aluno_validado.columns else "Aluno"
            st.success(f"Bem-vindo de volta, {nome_aluno_logado}!")
            
            t_treino, t_evolucao, t_fin = st.tabs(["🏋️ Minha Ficha de Exercícios", "📈 Minha Evolução Física", "💳 Meu Financeiro"])
            
            with t_treino:
                st.subheader("Treino do Dia")
                if not df_treinos.empty and 'ID_Aluno' in df_treinos.columns:
                    treino_aluno = df_treinos[df_treinos['ID_Aluno'] == input_id.strip()]
                    if not treino_aluno.empty:
                        st.dataframe(treino_aluno, use_container_width=True)
                    else:
                        st.info("Seu plano tático de treino está sendo montado pela equipe Team Muniz!")
                        
            with t_evolucao:
                st.subheader("Histórico de Avaliações")
                if not df_bio.empty and 'ID_Aluno' in df_bio.columns:
                    bio_aluno = df_bio[df_bio['ID_Aluno'] == input_id.strip()]
                    st.dataframe(bio_aluno, use_container_width=True)
                    
            with t_fin:
                st.subheader("Minhas Mensalidades")
                if not df_financeiro.empty and 'ID_Aluno' in df_financeiro.columns:
                    fin_aluno = df_financeiro[df_financeiro['ID_Aluno'] == input_id.strip()]
                    colunas_aluno_fin = [c for c in ['Mes_Referencia', 'Valor_Cobrado', 'Data_Vencimento', 'Status_Pagamento'] if c in fin_aluno.columns]
                    st.dataframe(fin_aluno[colunas_aluno_fin], use_container_width=True)
        else:
            st.error("Credenciais de segurança não coincidem. Verifique o ID ou o Telefone digitado.")
    elif input_id and input_tel:
        st.error("A base de dados de alunos não pôde ser verificada. Fale com o administrador.")
