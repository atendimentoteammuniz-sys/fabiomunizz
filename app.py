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

# Estilização Visual Premium (Fundo grafite escuro e detalhes em Dourado)
st.markdown("""
    <style>
    .main { background-color: #0d0d0d; color: #FFFFFF; }
    .sidebar .sidebar-content { background-color: #151515; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'Helvetica', sans-serif; }
    div.stButton > button:first-child {
        background-color: #D4AF37; color: #000000; font-weight: bold; border-radius: 6px; width: 100%;
    }
    .kpi-box { background-color: #1a1a1a; padding: 20px; border-radius: 8px; border-left: 4px solid #D4AF37; margin-bottom: 15px; }
    .kpi-box-red { background-color: #1a1a1a; padding: 20px; border-radius: 8px; border-left: 4px solid #FF4B4B; margin-bottom: 15px; }
    .card-exercicio { background-color: #1c1c1c; padding: 15px; border-radius: 8px; border: 1px solid #333; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# URL Base de exportação corrigida conforme os novos links
URL_BASE = "https://docs.google.com/spreadsheets/d/1tqfyKLolU1P7AVOYw7vJcOtG19QOM9tSVu6OK09j668/export?format=csv&gid="

# DICIONÁRIO DE GIDS ATUALIZADO CONFORME SUA SOLICITAÇÃO
GIDS = {
    "Cadastro_Alunos": "896837375",
    "Historico_Bioimpedancia": "736167025",
    "Controle_Financeiro": "266431932",
    "Fluxo_Caixa_Geral": "1156715922",
    "Prescricao_Treinos": "181621672",
    "Agendamento_Aulas": "1168521543"
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
df_caixa = carregar_dados("Fluxo_Caixa_Geral")

# Tratamento Numérico Financeiro (Receitas)
if not df_financeiro.empty and 'Valor_Cobrado' in df_financeiro.columns:
    df_financeiro['Valor_Num'] = df_financeiro['Valor_Cobrado'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
else:
    df_financeiro['Valor_Num'] = 0.0

# Tratamento Numérico (Saídas / Fluxo de Caixa)
if not df_caixa.empty and 'Valor_Saida' in df_caixa.columns:
    df_caixa['Saida_Num'] = df_caixa['Valor_Saida'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
else:
    df_caixa['Saida_Num'] = 0.0

# Identificação Dinâmica da Coluna de Status Financeiro (Evita KeyError)
coluna_status_fin = None
if not df_financeiro.empty:
    for col in df_financeiro.columns:
        if 'status' in col.lower() or 'pagamento' in col.lower():
            coluna_status_fin = col
            break

# --- MENU LATERAL ---
st.sidebar.title("🏆 Team Muniz Hub")
st.sidebar.write("---")
perfil = st.sidebar.radio("Selecione o Portal de Acesso:", ["🏃 Portal do Aluno", "👑 Painel do Treinador"])

# =====================================================================
# 👑 PAINEL DO TREINADOR (FÁBIO)
# =====================================================================
if perfil == "👑 Painel do Treinador":
    st.sidebar.write("---")
    senha_treinador = st.sidebar.text_input("Chave de Acesso do Treinador:", type="password")
    
    if senha_treinador == "muniz2026":
        st.sidebar.success("Acesso Autorizado!")
        
        menu = st.sidebar.selectbox(
            "Selecione o Módulo Administrativo:",
            ["📊 Dashboard Geral", "👥 Auditoria de Cadastros", "💰 Cobranças & Receitas", "📅 Organização da Agenda", "🏋️ Central de Exercícios"]
        )
        
        # -------------------------------------------------------------
        # MÓDULO 1: DASHBOARD GERAL
        # -------------------------------------------------------------
        if menu == "📊 Dashboard Geral":
            st.title("Dashboard de Controle Financeiro e Operacional")
            
            # Cálculos dos Quadrinhos Primários
            ativos = len(df_alunos[df_alunos['Status_Aluno'] == 'Ativo']) if not df_alunos.empty else 0
            entradas = df_financeiro['Valor_Num'].sum() if not df_financeiro.empty else 0.0
            saidas = df_caixa['Saida_Num'].sum() if not df_caixa.empty else 0.0
            saldo_liquido = entradas - saidas
            
            # Renderização dos Quadrinhos de Layout
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"<div class='kpi-box'><span style='color:#aaa;font-size:14px;'>Alunos Ativos</span><br><h2 style='margin:0;'>{ativos}</h2></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='kpi-box'><span style='color:#aaa;font-size:14px;'>Entradas (Receitas)</span><br><h2 style='margin:0;color:#D4AF37;'>R$ {entradas:,.2f}</h2></div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='kpi-box-red'><span style='color:#aaa;font-size:14px;'>Saídas (Gastos)</span><br><h2 style='margin:0;color:#FF4B4B;'>R$ {saidas:,.2f}</h2></div>", unsafe_allow_html=True)
            with c4:
                cor_saldo = "#D4AF37" if saldo_liquido >= 0 else "#FF4B4B"
                st.markdown(f"<div class='kpi-box'><span style='color:#aaa;font-size:14px;'>Saldo Real Líquido</span><br><h2 style='margin:0;color:{cor_saldo};'>R$ {saldo_liquido:,.2f}</h2></div>", unsafe_allow_html=True)
            
            # CENTRAL DE COBRANÇA DIRETO NO DASHBOARD
            st.write("---")
            st.subheader("📲 Central de Mensagens e Cobranças Ativas")
            
            if coluna_status_fin and not df_financeiro.empty:
                devedores = df_financeiro[df_financeiro[coluna_status_fin] == 'Pendente']
                
                if not devedores.empty:
                    for idx, row in devedores.iterrows():
                        aluno_info = df_alunos[df_alunos['ID_Aluno'] == row['ID_Aluno']] if not df_alunos.empty else pd.DataFrame()
                        if not aluno_info.empty:
                            telefone = str(aluno_info.iloc[0]['WhatsApp']).strip()
                            nome_aluno = row['Nome_Aluno']
                            vencimento = row['Data_Vencimento'] if 'Data_Vencimento' in row else "Mês Atual"
                            valor = row['Valor_Cobrado']
                            
                            mensagem = f"Olá {nome_aluno}, tudo bem? Passando para lembrar que a mensalidade da sua assessoria Team Muniz com vencimento em {vencimento} ({valor}) está aberta. Se precisar do pix só avisar! 💪"
                            mensagem_codificada = urllib.parse.quote(mensagem)
                            link_whatsapp = f"https://api.whatsapp.com/send?phone={telefone}&text={mensagem_codificada}"
                            
                            col_txt, col_btn = st.columns([4, 1])
                            with col_txt:
                                st.write(f"🔴 **{nome_aluno}** | Vencimento: {vencimento} | Valor: **{valor}**")
                            with col_btn:
                                st.markdown(f"[📩 Cobrar no Zap]({link_whatsapp})", unsafe_allow_html=True)
                else:
                    st.success("Tudo em dia! Nenhuma cobrança pendente para envio.")
            else:
                st.warning("Aguardando mapeamento da coluna de Status de Pagamento na planilha.")

        # -------------------------------------------------------------
        # MÓDULO 2: AUDITORIA DE CADASTROS
        # -------------------------------------------------------------
        elif menu == "👥 Auditoria de Cadastros":
            st.title("Central de Cadastro de Alunos")
            
            if not df_alunos.empty:
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    total_ativos = len(df_alunos[df_alunos['Status_Aluno'] == 'Ativo'])
                    st.info(f"Quantidade de Alunos Ativos: {total_ativos}")
                with col_f2:
                    total_inativos = len(df_alunos[df_alunos['Status_Aluno'] == 'Inativo'])
                    st.warning(f"Quantidade de Alunos Inativos: {total_inativos}")
                
                st.write("---")
                st.dataframe(df_alunos[['ID_Aluno', 'Nome_Completo', 'WhatsApp', 'Modalidade', 'Status_Aluno']], use_container_width=True)
            else:
                st.error("Planilha de cadastro vazia ou inacessível.")

        # -------------------------------------------------------------
        # MÓDULO 3: COBRANÇAS & RECEITAS
        # -------------------------------------------------------------
        elif menu == "💰 Cobranças & Receitas":
            st.title("Gestão de Receitas por Categoria")
            
            if coluna_status_fin and not df_financeiro.empty:
                pago_total = df_financeiro[df_financeiro[coluna_status_fin] == 'Pago']['Valor_Num'].sum()
                pendente_total = df_financeiro[df_financeiro[coluna_status_fin] == 'Pendente']['Valor_Num'].sum()
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.markdown(f"<div class='kpi-box'><span style='color:#aaa;'>Total Recebido (Pago)</span><br><h3 style='color:#D4AF37;'>R$ {pago_total:,.2f}</h3></div>", unsafe_allow_html=True)
                with col_p2:
                    st.markdown(f"<div class='kpi-box-red'><span style='color:#aaa;'>Total Em Aberto (Pendente)</span><br><h3 style='color:#FF4B4B;'>R$ {pendente_total:,.2f}</h3></div>", unsafe_allow_html=True)
                
                st.write("---")
                st.subheader("Gráfico de Pizza das Finanças")
                resumo_pizza = df_financeiro.groupby(coluna_status_fin)['Valor_Num'].sum()
                st.pie_chart(resumo_pizza)
            else:
                st.error("⚠️ Coluna de validação de pagamento não identificada na aba Controle_Financeiro.")
                st.write("As colunas mapeadas atualmente são:")
                st.code(list(df_financeiro.columns) if not df_financeiro.empty else "Aba sem dados")

        # -------------------------------------------------------------
        # MÓDULO 4: ORGANIZAÇÃO DA AGENDA
        # -------------------------------------------------------------
        elif menu == "📅 Organização da Agenda":
            st.title("Agenda de Atendimentos Semanais")
            tipo_agenda = st.radio("Modalidade:", ["Treinamento Fixo Individual", "Treinamento em Grupo"])
            
            df_filtrado_agenda = df_agenda[df_agenda['Observacoes_Agenda'] == ('Treino Fixo' if tipo_agenda == "Treinamento Fixo Individual" else 'Treino em Grupo')] if not df_agenda.empty else pd.DataFrame()
            
            if not df_filtrado_agenda.empty:
                for aluno in df_filtrado_agenda['Nome_Aluno'].unique():
                    with st.expander(f"👤 Agenda de: {aluno}"):
                        st.dataframe(df_filtrado_agenda[df_filtrado_agenda['Nome_Aluno'] == aluno][['ID_Agendamento', 'Data_Aula', 'Horario_Inicio', 'Horario_Fim', 'Status_Aula']], use_container_width=True)

        # -------------------------------------------------------------
        # MÓDULO 5: CENTRAL DE EXERCÍCIOS (Quadrinhos de Layout)
        # -------------------------------------------------------------
        elif menu == "🏋️ Central de Exercícios":
            st.title("Fichas de Treino por Aluno")
            
            aluno_sel = st.selectbox("Selecione o Aluno para auditar a ficha:", df_alunos['Nome_Completo'].tolist())
            id_aluno_sel = df_alunos[df_alunos['Nome_Completo'] == aluno_sel]['ID_Aluno'].values[0]
            
            st.write(f"### Ficha Tática Técnica de: {aluno_sel} ({id_aluno_sel})")
            
            treino_filtrado = df_treinos[df_treinos['ID_Aluno'] == id_aluno_sel] if not df_treinos.empty else pd.DataFrame()
            
            if not treino_filtrado.empty and not treino_filtrado['Nome_Exercicio'].isna().all():
                for idx, row in treino_filtrado.dropna(subset=['Nome_Exercicio']).iterrows():
                    st.markdown(f"""
                    <div class='card-exercicio'>
                        <span style='color:#D4AF37; font-weight:bold; font-size:16px;'>{row['Nome_Exercicio']}</span><br>
                        <span style='color:#aaa;'>Divisão:</span> {row['Divisao_Treino']} | 
                        <span style='color:#aaa;'>Grupo:</span> {row['Grupo_Muscular']}<br>
                        <span style='color:#D4AF37;'>{row['Series']} Séries x {row['Repeticoes']} Repetições</span> | Descanso: {row['Descanso']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum exercício cadastrado para este aluno ainda.")
    else:
        st.sidebar.error("Chave inválida ou aguardando preenchimento.")

# =====================================================================
# 🏃 PORTAL DO ALUNO
# =====================================================================
elif perfil == "🏃 Portal do Aluno":
    st.title("Portal do Aluno - Team Muniz")
    
    input_id = st.text_input("Seu Código (ID Aluno):", placeholder="ALU001")
    input_tel = st.text_input("Seu WhatsApp Cadastrado (Com DDD):", placeholder="5511999999999")
    
    if input_id and input_tel:
        validado = df_alunos[(df_alunos['ID_Aluno'].astype(str) == input_id.strip()) & (df_alunos['WhatsApp'].astype(str) == input_tel.strip())] if not df_alunos.empty else pd.DataFrame()
        
        if not validado.empty:
            st.success(f"Logado com Sucesso, {validado.iloc[0]['Nome_Completo']}!")
            
            # LINK DE AGENDAMENTO INTEGRADO
            st.subheader("📅 Marcação de Aulas")
            st.markdown('<a href="https://calendar.google.com" target="_blank"><button style="background-color:#D4AF37;color:black;font-weight:bold;padding:10px;border-radius:5px;width:100%;border:none;cursor:pointer;">🗓️ Confirmar Presença ou Agendar Nova Aula</button></a>', unsafe_allow_html=True)
            st.write("---")
            
            t_treino, t_fin = st.tabs(["🏋️ Minha Ficha de Treino", "💳 Meu Histórico Financeiro"])
            
            with t_treino:
                st.subheader("Meus Exercícios Prescritos")
                treino_aluno = df_treinos[df_treinos['ID_Aluno'] == input_id.strip()].dropna(subset=['Nome_Exercicio']) if not df_treinos.empty else pd.DataFrame()
                
                if not treino_aluno.empty:
                    for idx, row in treino_aluno.iterrows():
                        st.markdown(f"""
                        <div class='card-exercicio'>
                            <b style='color:#D4AF37; font-size:16px;'>{row['Nome_Exercicio']}</b><br>
                            Foco: {row['Grupo_Muscular']} ({row['Divisao_Treino']})<br>
                            <span style='color:#D4AF37; font-size:15px;'><b>{row['Series']} x {row['Repeticoes']}</b></span> (Descanso: {row['Descanso']})<br>
                            <small style='color:#888;'>Obs: {row['Observacoes_Tecnicas'] if 'Observacoes_Tecnicas' in row else 'Executar com cadência controlada.'}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Fábio Muniz está estruturando sua nova periodização tática!")
                    
            with t_fin:
                st.subheader("Minhas Mensalidades")
                fin_aluno = df_financeiro[df_financeiro['ID_Aluno'] == input_id.strip()] if not df_financeiro.empty else pd.DataFrame()
                if not fin_aluno.empty:
                    exibir_cols = ['Mes_Referencia', 'Valor_Cobrado', 'Data_Vencimento', coluna_status_fin] if coluna_status_fin else ['Mes_Referencia', 'Valor_Cobrado', 'Data_Vencimento']
                    st.dataframe(fin_aluno[exibir_cols], use_container_width=True)
        else:
            st.error("Dados de acesso incorretos. Verifique suas credenciais.")
