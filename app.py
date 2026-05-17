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

# URL Base estrita do seu Google Sheets para exportação de CSV
URL_BASE = "https://docs.google.com/spreadsheets/d/1tqfyKLolU1P7AVOYw7vJcOtG19QOM9tSVu6OK09j668/export?format=csv&gid="

# MAPEAMENTO DOS GIDS DAS SUAS ABAS REALMENTE CONFERIDAS
GIDS = {
    "Cadastro_Alunos": "896837375",
    "Historico_Bioimpedancia": "736167025",
    "Controle_Financeiro": "266431932",   # <--- ENTRADAS (RECEITAS)
    "Fluxo_Caixa_Geral": "1156715922",     # <--- SAÍDAS (GASTOS)
    "Prescricao_Treinos": "181621672",
    "Agendamento_Aulas": "1168521543"
}

def carregar_dados_aba(nome_aba):
    """Carrega a aba garantindo o isolamento total pelo GID correto"""
    url_completa = f"{URL_BASE}{GIDS[nome_aba]}"
    try:
        df = pd.read_csv(url_completa)
        df = df.dropna(how='all')
        
        # Limpeza de cabeçalhos contra poeira textual
        df.columns = df.columns.astype(str).str.replace(r'\\', '', regex=True).str.replace('*', '', regex=False).str.strip()
        df.columns = df.columns.str.replace(' ', '_', regex=False)
        return df
    except Exception as e:
        st.error(f"Erro crítico ao conectar na aba {nome_aba}: {e}")
        return pd.DataFrame()

# --- CARREGAMENTO ISOLADO DE CADA TABELA ---
df_alunos = carregar_dados_aba("Cadastro_Alunos")
df_financeiro = carregar_dados_aba("Controle_Financeiro") # Entradas
df_fluxo_caixa = carregar_dados_aba("Fluxo_Caixa_Geral")    # Saídas
df_agenda = carregar_dados_aba("Agendamento_Aulas")
df_treinos = carregar_dados_aba("Prescricao_Treinos")
df_bio = carregar_dados_aba("Historico_Bioimpedancia")

def tratar_coluna_numerica(df, possíveis_colunas):
    """Transforma colunas de texto monetário (R$ 150,00) em float limpo para cálculo"""
    if df.empty:
        return pd.Series(dtype=float)
    col_encontrada = None
    for col in possíveis_colunas:
        if col in df.columns:
            col_encontrada = col
            break
    if col_encontrada:
        return df[col_encontrada].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
    return pd.Series([0.0] * len(df))

# Tratamento Numérico Seguro de Entradas (Receitas)
df_financeiro['Valor_Num'] = tratar_coluna_numerica(df_financeiro, ['Valor_Cobrado', 'Valor', 'Preco'])

# Tratamento Numérico Seguro de Saídas (Gastos no Fluxo de Caixa)
df_fluxo_caixa['Valor_Num'] = tratar_coluna_numerica(df_fluxo_caixa, ['Valor_Pago', 'Valor', 'Saida', 'Gasto'])

# --- NAVEGAÇÃO LATERAL ---
st.sidebar.title("🏆 Team Muniz Hub")
st.sidebar.write("---")
perfil = st.sidebar.radio("Selecione o Portal de Acesso:", ["🏃 Portal do Aluno", "👑 Painel do Treinador"])

# =====================================================================
# 👑 PERFIL ADMINISTRATIVO: TREINADOR (FÁBIO)
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
        # MÓDULO 1: DASHBOARD & CADASTRO (Cálculos de Balanço Corrigidos)
        # -------------------------------------------------------------
        if menu == "📊 Dashboard & Cadastro":
            st.title("Indicadores e Perfis de Clientes")
            
            # Contagens baseadas estritamente na nova regra de negócio orientada
            total_alunos_count = len(df_alunos) if not df_alunos.empty else 0
            
            entradas_totais = df_financeiro['Valor_Num'].sum() if not df_financeiro.empty else 0.0
            saidas_totais = df_fluxo_caixa['Valor_Num'].sum() if not df_fluxo_caixa.empty else 0.0
            saldo_liquido = entradas_totais - saidas_totais
            
            # Exibição dos KPIs macro do negócio
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"<div class='kpi-box'><span style='color:gray;'>Alunos Ativos</span><br><h2>{total_alunos_count}</h2></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='kpi-box'><span style='color:green;'>Entradas (Receitas)</span><br><h2>R$ {entradas_totais:,.2f}</h2></div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='kpi-box'><span style='color:red;'>Saídas (Gastos)</span><br><h2>R$ {saidas_totais:,.2f}</h2></div>", unsafe_allow_html=True)
            with c4:
                cor_saldo = "cyan" if saldo_liquido >= 0 else "orange"
                st.markdown(f"<div class='kpi-box'><span style='color:gray;'>Saldo Real Líquido</span><br><h2 style='color:{cor_saldo} !important;'>R$ {saldo_liquido:,.2f}</h2></div>", unsafe_allow_html=True)
            
            st.write("---")
            st.subheader("Filtro Individual de Aluno (Dados Cadastrais)")
            
            col_nome_cad = 'Nome_Completo' if 'Nome_Completo' in df_alunos.columns else ('Nome_Aluno' if 'Nome_Aluno' in df_alunos.columns else None)
            
            if not df_alunos.empty and col_nome_cad:
                lista_nomes = df_alunos[col_nome_cad].dropna().tolist()
                aluno_selecionado = st.selectbox("Selecione o Aluno para Ver a Ficha Cadastral:", lista_nomes)
                dados_do_aluno = df_alunos[df_alunos[col_nome_cad] == aluno_selecionado].iloc[0]
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Código de Identificação:** {dados_do_aluno.get('ID_Aluno', 'N/A')}")
                    st.markdown(f"**WhatsApp / Celular:** {dados_do_aluno.get('WhatsApp', dados_do_aluno.get('Telefone', 'N/A'))}")
                with col_b:
                    st.markdown(f"**Modalidade Contratada:** {dados_do_aluno.get('Modalidade', 'N/A')}")
                    st.markdown(f"**Status no Sistema:** {dados_do_aluno.get('Status_Aluno', 'N/A')}")
            else:
                st.warning("Aguardando leitura de dados válidos da aba de cadastro.")
            
            st.write("---")
            with st.expander("Ver Planilha Completa de Cadastros"):
                st.dataframe(df_alunos, use_container_width=True)

        # -------------------------------------------------------------
        # MÓDULO 2: COBRANÇA & RECEITAS
        # -------------------------------------------------------------
        elif menu == "💰 Cobrança & Receitas":
            st.title("Gestão de Receitas e Despesas (Fluxo)")
            
            tab_entradas, tab_saidas = st.tabs(["💰 Entradas (Receitas)", "📉 Saídas (Fluxo de Caixa / Gastos)"])
            
            with tab_entradas:
                col_status = 'Status_Pagamento' if 'Status_Pagamento' in df_financeiro.columns else ('Status' if 'Status' in df_financeiro.columns else None)
                
                if not df_financeiro.empty and col_status and 'Valor_Num' in df_financeiro.columns:
                    st.write("### Divisão de Receitas por Categoria")
                    df_pizza = df_financeiro.dropna(subset=[col_status]).groupby(col_status, as_index=False)['Valor_Num'].sum()
                    try:
                        st.pie_chart(df_pizza, theme=None, names=col_status, values='Valor_Num')
                    except Exception:
                        st.dataframe(df_pizza.rename(columns={col_status: 'Status', 'Valor_Num': 'Total (R$)'}), use_container_width=True)
                    
                    st.write("---")
                    st.subheader("Filtros das Faturas de Alunos")
                    col_b1, col_b2, col_b3 = st.columns(3)
                    filtro_financeiro = "Todos"
                    with col_b1:
                        if st.button("Ver Apenas Cobranças Pendentes"): filtro_financeiro = "Pendente"
                    with col_b2:
                        if st.button("Ver Apenas Mensalidades Pagas"): filtro_financeiro = "Pago"
                    with col_b3:
                        if st.button("Redefinir Filtros (Ver Tudo)"): filtro_financeiro = "Todos"
                    
                    if filtro_financeiro != "Todos":
                        df_exibicao_fin = df_financeiro[df_financeiro[col_status].astype(str).str.contains(filtro_financeiro, na=False, case=False)]
                    else:
                        df_exibicao_fin = df_financeiro
                        
                    st.dataframe(df_exibicao_fin, use_container_width=True)
                    
                    # Central de Cobrança Automatizada via WhatsApp
                    st.write("---")
                    st.subheader("⚠️ Central de Mensagens Automáticas de Cobrança")
                    devedores = df_financeiro[df_financeiro[col_status].astype(str).str.contains('Pendente', na=False, case=False)]
                    
                    if not devedores.empty:
                        for idx, row in devedores.iterrows():
                            id_alvo = row.get('ID_Aluno')
                            aluno_info = df_alunos[df_alunos['ID_Aluno'] == id_alvo] if not df_alunos.empty and 'ID_Aluno' in df_alunos.columns else pd.DataFrame()
                            
                            lbl_nome = 'Nome_Completo' if 'Nome_Completo' in df_alunos.columns else 'Nome_Aluno'
                            nome_aluno = row.get('Nome_Aluno', (aluno_info.iloc[0][lbl_nome] if not aluno_info.empty else "Aluno"))
                            telefone = str(aluno_info.iloc[0]['WhatsApp']).strip() if not aluno_info.empty and 'WhatsApp' in aluno_info.columns else ""
                            val_txt = row.get('Valor_Cobrado', row.get('Valor', 'Mensalidade'))
                            
                            if telefone and telefone != "nan" and telefone != "":
                                mensagem = f"Olá {nome_aluno}, tudo bem? Passando para lembrar que a mensalidade da sua assessoria Team Muniz ({val_txt}) está aberta. Caso já tenha realizado o pagamento, desconsidere! 💪"
                                mensagem_codificada = urllib.parse.quote(mensagem)
                                link_whatsapp = f"https://api.whatsapp.com/send?phone={telefone}&text={mensagem_codificada}"
                                
                                col_txt, col_btn = st.columns([4, 1])
                                with col_txt:
                                    st.write(f"🔴 **{nome_aluno}** - Fatura Pendente de {val_txt}.")
                                with col_btn:
                                    st.markdown(f"[📩 Cobrar no Zap]({link_whatsapp})", unsafe_allow_html=True)
                    else:
                        st.success("Tudo em dia! Nenhuma cobrança pendente identificada.")
                else:
                    st.info("Aba de controle financeiro vazia ou sem colunas compatíveis.")
            
            with tab_saidas:
                st.write("### Histórico e Lançamento de Gastos (Fluxo de Caixa)")
                if not df_fluxo_caixa.empty:
                    st.dataframe(df_fluxo_caixa, use_container_width=True)
                else:
                    st.info("Nenhum registro de gasto/saída encontrado na aba do Fluxo de Caixa ainda.")

        # -------------------------------------------------------------
        # MÓDULO 3: AGENDA DE ATENDIMENTOS
        # -------------------------------------------------------------
        elif menu == "📅 Organização da Agenda":
            st.title("Agenda de Atendimentos Presenciais")
            
            lbl_nome_age = 'Nome_Aluno' if 'Nome_Aluno' in df_agenda.columns else ('Nome' if 'Nome' in df_agenda.columns else None)
            
            if not df_agenda.empty and lbl_nome_age:
                tipo_agenda = st.radio("Selecione a Modalidade da Agenda:", ["Treinamento Fixo Individual", "Treinamento em Grupo"])
                
                col_obs = 'Observacoes_Agenda' if 'Observacoes_Agenda' in df_agenda.columns else ('Observacoes' if 'Observacoes' in df_agenda.columns else None)
                if col_obs:
                    if tipo_agenda == "Treinamento Fixo Individual":
                        df_filtrado_agenda = df_agenda[df_agenda[col_obs].astype(str).str.contains('Fixo', na=False, case=False)]
                    else:
                        df_filtrado_agenda = df_agenda[df_agenda[col_obs].astype(str).str.contains('Grupo', na=False, case=False)]
                else:
                    df_filtrado_agenda = df_agenda
                    
                if not df_filtrado_agenda.empty:
                    lista_alunos_agenda = df_filtrado_agenda[lbl_nome_age].unique()
                    for aluno in lista_alunos_agenda:
                        with st.expander(f"👤 Ver Horários da Agenda de: {aluno}"):
                            dados_agenda_aluno = df_filtrado_agenda[df_filtrado_agenda[lbl_nome_age] == aluno]
                            st.dataframe(dados_agenda_aluno, use_container_width=True)
                else:
                    st.info("Nenhum horário registrado para esta modalidade específica.")
            else:
                st.warning("Aba de Agendamento vazia ou sem mapeamento de nomes.")

        # -------------------------------------------------------------
        # MÓDULO 4: PRESCRIÇÃO DE TREINOS
        # -------------------------------------------------------------
        elif menu == "🏋️ Central de Exercícios":
            st.title("Fichas de Exercícios Técnicos")
            
            col_nome_cad = 'Nome_Completo' if 'Nome_Completo' in df_alunos.columns else 'Nome_Aluno'
            if not df_alunos.empty and col_nome_cad in df_alunos.columns:
                aluno_treino_sel = st.selectbox("Selecione o Aluno para Abrir a Ficha:", df_alunos[col_nome_cad].tolist())
                id_aluno_sel = df_alunos[df_alunos[col_nome_cad] == aluno_treino_sel]['ID_Aluno'].values[0]
                
                with st.expander(f"📂 Abrir Ficha Completa (ID: {id_aluno_sel})"):
                    if not df_treinos.empty and 'ID_Aluno' in df_treinos.columns:
                        treino_filtrado_muniz = df_treinos[df_treinos['ID_Aluno'] == id_aluno_sel]
                        if treino_filtrado_muniz.empty:
                            st.info("A ficha deste aluno está criada, mas nenhum exercício (EXE) foi digitado nela ainda.")
                        else:
                            st.dataframe(treino_filtrado_muniz, use_container_width=True)
                    else:
                        st.warning("Aba de treinos indisponível ou sem a coluna 'ID_Aluno'.")
            else:
                st.error("Dados cadastrais indisponíveis para listagem de alunos.")
                
    elif senha_treinador != "":
        st.sidebar.error("Chave incorreta. Digite a senha administrativa do Team Muniz.")

# =====================================================================
# 🏃 PORTAL SEGURO DO ALUNO
# =====================================================================
elif perfil == "🏃 Portal do Aluno":
    st.title("Portal do Aluno - Team Muniz")
    st.write("Insira suas credenciais de segurança para liberar o acesso à sua ficha.")
    
    input_id = st.text_input("Digite seu Código de Acesso (ID Aluno):", placeholder="Ex: ALU001")
    input_tel = st.text_input("Digite seu Telefone Cadastrado (Com DDD):", placeholder="Ex: 5521974754210")
    
    if input_id and input_tel and not df_alunos.empty and 'ID_Aluno' in df_alunos.columns:
        col_tel = 'WhatsApp' if 'WhatsApp' in df_alunos.columns else ('Telefone' if 'Telefone' in df_alunos.columns else None)
        
        if col_tel:
            aluno_validado = df_alunos[(df_alunos['ID_Aluno'].astype(str) == input_id.strip()) & (df_alunos[col_tel].astype(str) == input_tel.strip())]
            
            if not aluno_validado.empty:
                col_nome_cad = 'Nome_Completo' if 'Nome_Completo' in df_alunos.columns else 'Nome_Aluno'
                nome_aluno_logado = aluno_validado.iloc[0][col_nome_cad]
                st.success(f"Acesso Liberado! Bem-vindo, {nome_aluno_logado}!")
                
                t_treino, t_evolucao, t_fin = st.tabs(["🏋️ Minha Ficha de Exercícios", "📈 Minha Evolução Física", "💳 Meu Financeiro"])
                
                with t_treino:
                    if not df_treinos.empty and 'ID_Aluno' in df_treinos.columns:
                        treino_aluno = df_treinos[df_treinos['ID_Aluno'] == input_id.strip()]
                        if not treino_aluno.empty: st.dataframe(treino_aluno, use_container_width=True)
                        else: st.info("Seu plano tático de treino está sendo montado por Fábio Muniz.")
                            
                with t_evolucao:
                    if not df_bio.empty and 'ID_Aluno' in df_bio.columns:
                        st.dataframe(df_bio[df_bio['ID_Aluno'] == input_id.strip()], use_container_width=True)
                        
                with t_fin:
                    if not df_financeiro.empty and 'ID_Aluno' in df_financeiro.columns:
                        st.dataframe(df_financeiro[df_financeiro['ID_Aluno'] == input_id.strip()], use_container_width=True)
            else:
                st.error("Credenciais incorretas. Verifique seu ID ou Telefone cadastrado.")
