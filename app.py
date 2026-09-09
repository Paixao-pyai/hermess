import re
import time
import pandas as pd
import streamlit as st

# Configuração visual da página
st.set_page_config(
    page_title="Central Privada de Automações",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# CONFIGURAÇÕES DE SEGURANÇA E CREDENCIAIS
# ==========================================
try:
    USUARIO_CORRETO = st.secrets["USUARIO"]
    SENHA_CORRETA = st.secrets["SENHA"]
except Exception:
    # Valores padrão caso rode localmente sem o secrets.toml
    USUARIO_CORRETO = "admin"
    SENHA_CORRETA = "Pidiry@n3ymar2213!"


# ==========================================
# SISTEMA DE LOGIN COM TEMPO DE ESPERA INCREMENTAL
# ==========================================
def verificar_autenticacao():
    # Inicializa variáveis de estado
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if "tentativas" not in st.session_state:
        st.session_state["tentativas"] = 0
    if "bloqueado_ate" not in st.session_state:
        st.session_state["bloqueado_ate"] = 0
    if "minutos_espera" not in st.session_state:
        st.session_state["minutos_espera"] = 1

    if not st.session_state["autenticado"]:
        st.markdown("## 🔒 Acesso Restrito")

        agora = time.time()
        tempo_restante = int(st.session_state["bloqueado_ate"] - agora)

        # SE AINDA ESTIVER NO TEMPO DE ESPERA DE BLOQUEIO
        if tempo_restante > 0:
            minutos = tempo_restante // 60
            segundos = tempo_restante % 60

            st.error(
                f"🚨 **SISTEMA TEMPORARIAMENTE BLOQUEADO!**\n\n"
                f"Você excedeu o limite de tentativas. "
                f"Aguarde **{minutos}m {segundos}s** para tentar novamente."
            )
            st.info(
                f"💡 A cada novo bloqueio, o tempo de espera aumenta em +1 minuto. "
                f"Próxima penalidade: {st.session_state['minutos_espera'] + 1} minuto(s)."
            )

            # Botão para atualizar a página e checar o tempo
            if st.button("🔄 Atualizar Contagem"):
                st.rerun()

            return False

        # TELA NORMAL DE LOGIN
        else:
            tentativas_restantes = 3 - (st.session_state["tentativas"] % 3)
            st.caption(
                f"Tentativas restantes antes do próximo bloqueio: `{tentativas_restantes}` de 3"
            )

            col_login, _ = st.columns([1, 2])
            with col_login:
                user = st.text_input("Usuário")
                password = st.text_input("Senha", type="password")

                if st.button("Entrar", type="primary"):
                    if user == USUARIO_CORRETO and password == SENHA_CORRETA:
                        # Sucesso: Reseta todas as métricas de bloqueio
                        st.session_state["autenticado"] = True
                        st.session_state["tentativas"] = 0
                        st.session_state["minutos_espera"] = 1
                        st.session_state["bloqueado_ate"] = 0
                        st.rerun()
                    else:
                        st.session_state["tentativas"] += 1

                        # A cada 3 erros, aplica o tempo de espera incremental
                        if st.session_state["tentativas"] % 3 == 0:
                            tempo_penalidade = (
                                st.session_state["minutos_espera"] * 60
                            )
                            st.session_state["bloqueado_ate"] = (
                                time.time() + tempo_penalidade
                            )
                            # Incrementa +1 minuto para o próximo bloqueio
                            st.session_state["minutos_espera"] += 1
                            st.rerun()
                        else:
                            st.error(
                                f"❌ Usuário ou senha incorretos! "
                                f"Tentativa {st.session_state['tentativas'] % 3} de 3."
                            )
            return False

    return True


# ==========================================
# APLICAÇÃO PRINCIPAL (SÓ CARREGA SE LOGADO)
# ==========================================
if verificar_autenticacao():

    # Botão de Sair na Barra Lateral
    st.sidebar.success("🔑 Autenticado com sucesso")
    if st.sidebar.button("🚪 Sair da Conta"):
        st.session_state["autenticado"] = False
        st.rerun()

    st.sidebar.markdown("---")

    # Menu Lateral de Navegação
    setor = st.sidebar.radio(
        "📌 Escolha o Módulo:",
        [
            "📊 Tratar Dados (Geral)",
            "👥 Recursos Humanos (RH)",
            "📞 Telemarketing & Atendimento",
        ],
    )

    st.title("⚡ Central de Automações & Gestão de Dados")

    # ------------------------------------------
    # MÓDULO 1: TRATAMENTO GERAL DE DADOS
    # ------------------------------------------
    if setor == "📊 Tratar Dados (Geral)":
        st.header("🧹 Limpeza e Padronização Universal de Arquivos")
        uploaded_file = st.file_uploader(
            "Arraste e solte seu arquivo (CSV ou Excel):", type=["csv", "xlsx"]
        )

        if uploaded_file:
            df = (
                pd.read_csv(uploaded_file)
                if uploaded_file.name.endswith(".csv")
                else pd.read_excel(uploaded_file)
            )

            st.subheader("👀 Visão Prévia dos Dados Brutos")
            st.write(
                f"Total de linhas: `{len(df)}` | Total de colunas: `{len(df.columns)}`"
            )
            st.dataframe(df.head(10), use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                remover_dup = st.checkbox(
                    "Remover linhas duplicadas", value=True
                )
                preencher_nulos = st.checkbox(
                    "Preencher campos vazios com 'N/A'", value=True
                )
            with col2:
                limpar_espacos = st.checkbox(
                    "Remover espaços extras em textos", value=True
                )

            if st.button("🚀 Aplicar Tratamento"):
                df_limpo = df.copy()

                if remover_dup:
                    df_limpo = df_limpo.drop_duplicates()
                if preencher_nulos:
                    df_limpo = df_limpo.fillna("N/A")
                if limpar_espacos:
                    cols_str = df_limpo.select_dtypes(
                        include=["object"]
                    ).columns
                    for c in cols_str:
                        df_limpo[c] = df_limpo[c].astype(str).str.strip()

                st.success(
                    f"Tratamento concluído! Linhas restantes: `{len(df_limpo)}`"
                )
                st.dataframe(df_limpo.head(10), use_container_width=True)

                csv_data = df_limpo.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Baixar em CSV",
                    data=csv_data,
                    file_name="base_tratada.csv",
                    mime="text/csv",
                )

    # ------------------------------------------
    # MÓDULO 2: RECURSOS HUMANOS (RH)
    # ------------------------------------------
    elif setor == "👥 Recursos Humanos (RH)":
        st.header("👥 Módulo de Recursos Humanos")

        aba_rh = st.tabs([
            "📋 Triagem de Candidatos",
            "🧮 Calculadora Trabalhista",
            "✉️ Comunicação & E-mails",
            "📢 Gerador de Anúncios de Vaga",
        ])

        with aba_rh[0]:
            st.subheader("Filtragem Rápida de Base de Currículos/Candidatos")
            rh_file = st.file_uploader(
                "Suba a planilha de candidatos:",
                type=["csv", "xlsx"],
                key="rh_triagem",
            )

            if rh_file:
                df_cand = (
                    pd.read_csv(rh_file)
                    if rh_file.name.endswith(".csv")
                    else pd.read_excel(rh_file)
                )
                st.dataframe(df_cand.head(), use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    col_filtro = st.selectbox(
                        "Coluna para Filtrar:", df_cand.columns
                    )
                with col2:
                    opcoes = df_cand[col_filtro].unique()
                    val_filtro = st.selectbox("Valor desejado:", opcoes)

                df_res = df_cand[df_cand[col_filtro] == val_filtro]
                st.write(f"Candidatos encontrados: `{len(df_res)}`")
                st.dataframe(df_res, use_container_width=True)

        with aba_rh[1]:
            st.subheader("Simulador de Benefícios / Horas Extras")
            col1, col2, col3 = st.columns(3)
            with col1:
                salario_base = st.number_input(
                    "Salário Base (R$):", min_value=0.0, value=3000.0
                )
            with col2:
                horas_extras = st.number_input(
                    "Horas Extras (50%):", min_value=0.0, value=8.0
                )
            with col3:
                dias_uteis = st.number_input(
                    "Dias Úteis Trabalhados:", min_value=1, value=22
                )

            valor_hora = salario_base / 220
            total_he = horas_extras * (valor_hora * 1.5)
            salario_bruto = salario_base + total_he

            st.metric("Valor estimado da hora", f"R$ {valor_hora:.2f}")
            st.metric("Total Adicional de Horas Extras", f"R$ {total_he:.2f}")
            st.metric("Salário Bruto Projetado", f"R$ {salario_bruto:.2f}")

        with aba_rh[2]:
            st.subheader("Gerador de Mensagens Padrão")
            tipo = st.selectbox(
                "Selecione o Modelo:",
                [
                    "Convocação para Entrevista",
                    "Feedback Desqualificação",
                    "Boas-Vindas",
                ],
            )
            nome = st.text_input("Nome do Candidato:", "Maria Silva")
            vaga = st.text_input("Cargo/Vaga:", "Analista de Dados")

            if tipo == "Convocação para Entrevista":
                msg = f"Olá {nome},\n\nSua candidatura para a vaga de {vaga} foi selecionada! Gostaria de agendar uma entrevista nesta semana.\n\nQual o seu melhor horário?"
            elif tipo == "Feedback Desqualificação":
                msg = f"Olá {nome},\n\nAgradecemos seu interesse na oportunidade de {vaga}. Neste momento, seguimos com candidatos que possuem maior alinhamento com o perfil. Manteremos seu currículo em nosso banco de dados."
            else:
                msg = f"Seja bem-vindo(a) ao time, {nome}!\n\nEstamos ansiosos para sua estreia na vaga de {vaga}."

            st.text_area("Copie o texto abaixo:", msg, height=140)

        with aba_rh[3]:
            st.subheader("Gerador de Post de Vaga")
            cargo = st.text_input("Título do Cargo:", "Assistente Administrativo")
            reqs = st.text_area(
                "Requisitos (um por linha):",
                "Excel Intermediário\nBoa comunicação\nEnsino Médio Completo",
            )
            modelo_post = f"🚨 OPORTUNIDADE ABERTA: {cargo} 🚨\n\n📌 Requisitos:\n{reqs}\n\n📥 Envie seu currículo respondendo a este anúncio!"
            st.code(modelo_post, language="markdown")

    # ------------------------------------------
    # MÓDULO 3: TELEMARKETING & ATENDIMENTO
    # ------------------------------------------
    elif setor == "📞 Telemarketing & Atendimento":
        st.header("📞 Módulo de Operações e Atendimento")

        aba_tmk = st.tabs([
            "🧹 Limpeza de Telefones/CPF",
            "📊 Calculadora de TMA & Produção",
            "💬 Scripts de Atendimento",
        ])

        with aba_tmk[0]:
            st.subheader("Formatador de Números de Telefone / CPFs")
            st.caption(
                "Remove parênteses, traços, espaços e caracteres inválidos de uma lista."
            )

            tmk_file = st.file_uploader(
                "Insira a lista de mailing:",
                type=["csv", "xlsx"],
                key="tmk_clean",
            )
            if tmk_file:
                df_tmk = (
                    pd.read_csv(tmk_file)
                    if tmk_file.name.endswith(".csv")
                    else pd.read_excel(tmk_file)
                )
                col_tel = st.selectbox(
                    "Selecione a coluna com os Telefones/CPFs:", df_tmk.columns
                )

                if st.button("🧼 Limpar e Manter Apenas Números"):
                    df_tmk[col_tel] = (
                        df_tmk[col_tel]
                        .astype(str)
                        .apply(lambda x: re.sub(r"\D", "", x))
                    )
                    st.success("Números padronizados com sucesso!")
                    st.dataframe(df_tmk.head(10), use_container_width=True)

                    csv_tmk = df_tmk.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Baixar Lista Formatada",
                        csv_tmk,
                        "mailing_limpo.csv",
                        "text/csv",
                    )

        with aba_tmk[1]:
            st.subheader("Cálculo de Indicadores (TMA / Produção)")
            c1, c2 = st.columns(2)
            with c1:
                total_chamadas = st.number_input(
                    "Total de Ligações/Atendimentos:", min_value=1, value=60
                )
            with c2:
                minutos_trabalhados = st.number_input(
                    "Tempo Total Trabalhado (em minutos):",
                    min_value=1.0,
                    value=360.0,
                )

            tma = minutos_trabalhados / total_chamadas
            st.metric("TMA (Tempo Médio de Atendimento)", f"{tma:.2f} min/ligação")

        with aba_tmk[2]:
            st.subheader("Banco de Scripts Rápidos")
            opcao_script = st.selectbox(
                "Cenário:",
                [
                    "Negociação de Débito",
                    "Suporte Técnico",
                    "Confirmação de Consulta/Agendamento",
                ],
            )
            cliente_nome = st.text_input("Nome do Cliente:", "Carlos")

            if opcao_script == "Negociação de Débito":
                script_txt = f"Olá, {cliente_nome}! Constamos uma oportunidade especial de quitação de débitos com isenção de juros válida para hoje. Podemos negociar?"
            elif opcao_script == "Suporte Técnico":
                script_txt = f"Olá, {cliente_nome}. Sou do suporte. Para adiantar seu atendimento, por favor, me informe o código do titular e descreva o ocorrido."
            else:
                script_txt = f"Olá, {cliente_nome}. Passando para confirmar seu agendamento programado para amanhã. Responda '1' para confirmar ou '2' para remarcar."

            st.text_area("Copie o script:", script_txt, height=120)