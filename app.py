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
    h1, h2, h3, h4 { color: #D4AF37 !important; font-family: 'Helvetica', sans-serif; }
    div.stButton > button:first-child {
        background-color: #D4AF37; color: #000000; font-weight: bold; border-radius: 6px; width: 100%;
    }
    .kpi-box { background-color: #1a1a1a; padding: 20px; border-radius: 8px; border-left: 4px solid #D4AF37; margin-bottom: 15px; }
    .kpi-box-red { background-color: #1a1a1a; padding: 20px; border-radius: 8px; border-left: 4px solid #FF4B4B; margin-bottom: 15px; }
    .card-exercicio { background-color: #1c1c1c; padding: 15px; border-radius: 8px; border: 1px solid #333; margin-bottom: 10px; }
    .card-cadastro { background-color: #161616; padding: 12px; border-radius: 6px; border: 1px solid #D4AF37; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# URL Base de exportação corrigida conforme os novos links
URL_BASE = "https://docs.google.com/spreadsheets/d/1tqfyKLolU1P7AVOYw7vJcOtG19QOM9tSVu6OK09j668/export?format=csv&gid="

# DICIONÁRIO DE GIDS ATUALIZADO
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

# --- MAPEAMENTO DINÂMICO DE COLUNAS (Evita KeyError se mudarem os nomes) ---
coluna_status_fin = None
coluna_nome_fin = None
coluna_valor_fin = None

if not df_financeiro.empty:
    for col in df_financeiro.columns:
        col_lower = col.lower()
        if 'status' in col_lower or 'pagamento' in col_lower:
            coluna_status_fin = col
        elif 'aluno' in col_lower or 'nome' in col_lower:
            coluna_nome_fin = col
        elif 'valor' in col_lower or 'cobrado' in col_lower or 'mensalidade' in col_lower:
            coluna_valor_fin = col

if not coluna_status_fin: coluna_status_fin = 'Status_Pagamento'
if not coluna_nome_fin: coluna_nome_fin = 'Nome_Aluno'
if not coluna_valor_fin: coluna_valor_fin = 'Valor_Cobrado'

# Tratamento Numérico Financeiro (Receitas)
if not df_financeiro.empty and coluna_valor_fin in df_financeiro.columns:
    df_financeiro['Valor_Num'] = df_financeiro[coluna_valor_fin].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
else:
    df_financeiro['Valor_Num'] = 0.0

# Mapeamento e Tratamento Numérico de Saídas (Fluxo de Caixa)
coluna_valor_saida = None
if not df_caixa.empty:
    for col in df_caixa.columns:
        col_lower = col.lower()
        if 'valor' in col_lower or 'saida' in col_lower or 'pago' in col_lower or 'gasto' in col_lower:
            coluna_valor_saida = col
            break

if not coluna_valor_saida: coluna_valor_saida = 'Valor_Saida'

if not df_caixa.empty and coluna_valor_saida in df_caixa.columns:
    df_caixa['Saida_Num'] = df_caixa[coluna_valor_saida].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip().astype(float)
else:
    df_caixa['Saida_Num'] = 0.0

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
            ["📊 Dashboard Geral", "👥 Central de Cadastros", "💰 Cobranças & Receitas", "📅 Organização da Agenda", "🏋️ Central de Exercícios"]
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
                st.markdown(f"<div class='kpi-box-red'><span style='color:#aaa;font-size:14px;'>Saídas (Fluxo)</span><br><h2 style='margin:0;color:#FF4B4B;'>R$ {saidas:,.2f}</h2></div>", unsafe_allow_html=True)
            with c4:
                cor_saldo = "#D4AF37" if saldo_liquido >= 0 else "#FF4B4B"
                st.markdown(f"<div class='kpi-box'><span style='color:#aaa;font-size:14px;'>Saldo Real Líquido</span><br><h2 style='margin:0;color:{cor_saldo};'>R$ {saldo_liquido:,.2f}</h2></div>", unsafe_allow_html=True)
            
            # CENTRAL DE COBRANÇA DIRETO NO DASHBOARD
            st.write("---")
            st.subheader("📲 Central de Mensagens e Cobranças Ativas")
            
            if coluna_status_fin in df_financeiro.columns and coluna_nome_fin in df_financeiro.columns:
                devedores = df_financeiro[df_financeiro[coluna_status_fin] == 'Pendente']
                
                if not devedores.empty:
                    for idx, row in devedores.iterrows():
                        aluno_info = df_alunos[df_alunos['ID_Aluno'] == row['ID_Aluno']] if not df_alunos.empty else pd.DataFrame()
                        if not aluno_info.empty:
                            telefone = str(aluno_info.iloc[0]['WhatsApp']).strip()
                            nome_aluno = row[coluna_nome_fin]
                            vencimento = row['Data_Vencimento'] if 'Data_Vencimento' in row else "Mês Atual"
                            valor = row[coluna_valor_fin] if coluna_valor_fin in row else "Valor em Aberto"
                            
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
                st.warning("Ajuste as colunas na planilha para ativar o envio automático de WhatsApp.")

        # -------------------------------------------------------------
        # MÓDULO 2: CENTRAL DE CADASTROS (Modificado para Cards Dinâmicos)
        # -------------------------------------------------------------
        elif menu == "👥 Central de Cadastros":
            st.title("Central de Cadastro de Alunos")
            
            if not df_alunos.empty:
                aluno_selecionado = st.selectbox("Selecione o Aluno para visualizar o perfil:", df_alunos['Nome_Completo'].tolist())
                
                dados_aluno = df_alunos[df_alunos['Nome_Completo'] == aluno_selecionado]
                
                if not dados_aluno.empty:
                    row_aluno = dados_aluno.iloc[0]
                    st.write(f"### 📇 Ficha Cadastral: {aluno_selecionado}")
                    
                    # Definição das colunas solicitadas
                    colunas_cards = ['ID_Aluno', 'Nome_Completo', 'WhatsApp', 'Data_Matricula', 'Modalidade', 'Plano', 'Status_Aluno']
                    
                    for col_card in colunas_cards:
                        if col_card in df_alunos.columns:
                            valor_card = row_aluno[col_card]
                            st.markdown(f"""
                            <div class='card-cadastro'>
                                <span style='color:#D4AF37; font-weight:bold; font-size:12px; text-transform: uppercase;'>{col_card.replace('_', ' ')}</span><br>
                                <span style='color:#FFFFFF; font-size:16px; font-weight:500;'>{valor_card}</span>
                            </div>
                            """, unsafe_allow_html=True)
                st.write("---")
            else:
                st.error("Planilha de cadastro vazia ou inacessível.")

        # -------------------------------------------------------------
        # MÓDULO 3: COBRANÇAS & RECEITAS (Sem gráfico de pizza)
        # -------------------------------------------------------------
        elif menu == "💰 Cobranças & Receitas":
            st.title("Gestão de Receitas por Categoria")
            
            if coluna_status_fin in df_financeiro.columns:
                pago_total = df_financeiro[df_financeiro[coluna_status_fin] == 'Pago']['Valor_Num'].sum()
                pendente_total = df_financeiro[df_financeiro[coluna_status_fin] == 'Pendente']['Valor_Num'].sum()
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.markdown(f"<div class='kpi-box'><span style='color:#aaa;'>Total Recebido (Pago)</span><br><h3 style='color:#D4AF37;'>R$ {pago_total:,.2f}</h3></div>", unsafe_allow_html=True)
                with col_p2:
                    st.markdown(f"<div class='kpi-box-red'><span style='color:#aaa;'>Total Em Aberto (Pendente)</span><br><h3 style='color:#FF4B4B;'>R$ {pendente_total:,.2f}</h3></div>", unsafe_allow_html=True)
            else:
                st.error("⚠️ Coluna de validação de pagamento não identificada na aba Controle_Financeiro.")

        # -------------------------------------------------------------
        # MÓDULO 4: ORGANIZAÇÃO DA AGENDA (Apenas cards por aluno)
        # -------------------------------------------------------------
        elif menu == "📅 Organização da Agenda":
            st.title("Cards de Agendamentos Semanais")
            
            if not df_agenda.empty:
                coluna_nome_agenda = 'Nome_Aluno' if 'Nome_Aluno' in df_agenda.columns else (df_agenda.columns[1] if len(df_agenda.columns) > 1 else df_agenda.columns[0])
                
                for aluno in df_agenda[coluna_nome_agenda].unique():
                    if pd.isna(aluno): continue
                    st.write(f"#### 👤 Cronograma de Treino: {aluno}")
                    
                    df_aluno_agenda = df_agenda[df_agenda[coluna_nome_agenda] == aluno]
                    
                    for idx, row in df_aluno_agenda.iterrows():
                        data_aula = row['Data_Aula'] if 'Data_Aula' in row else 'Agendado'
                        horario = f"{row['Horario_Inicio']} - {row['Horario_Fim']}" if 'Horario_Inicio' in row and 'Horario_Fim' in row else 'Horário a definir'
                        status_aula = row['Status_Aula'] if 'Status_Aula' in row else 'Confirmado'
                        obs = row['Observacoes_Agenda'] if 'Observacoes_Agenda' in row else ''
                        
                        st.markdown(f"""
                        <div class='card-exercicio'>
                            <b style='color:#D4AF37;'>📅 {data_aula}</b> | 🕒 Horário: {horario} <br>
                            Status do Atendimento: <b>{status_aula}</b> {f'| Direcionamento: {obs}' if obs else ''}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Nenhum dado encontrado na aba de Agendamentos.")

        # -------------------------------------------------------------
        # MÓDULO 5: CENTRAL DE EXERCÍCIOS (Layout intocado)
        # -------------------------------------------------------------
        elif menu == "🏋️ Central de Exercícios":
            st.title("Fichas de Treino por Aluno")
            
            aluno_sel = st.selectbox("Selecione o Aluno para auditar a ficha:", df_alunos['Nome_Completo'].tolist() if not df_alunos.empty else [])
            if aluno_sel:
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
                    exibir_cols = ['Mes_Referencia', coluna_valor_fin, 'Data_Vencimento', coluna_status_fin] if coluna_status_fin in fin_aluno.columns else ['Mes_Referencia', 'Data_Vencimento']
                    st.dataframe(fin_aluno[exibir_cols], use_container_width=True)
        else:
            st.error("Dados de acesso incorretos. Verifique suas credenciais.")
