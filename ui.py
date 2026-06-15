import streamlit as st
import pandas as pd

def formatar_numero_br(valor):
    """Formata número no padrão brasileiro R$ 1.234,56"""
    try:
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "R$ 0,00"

def exibir_sidebar():
    """Exibe a barra lateral com configurações."""
    with st.sidebar:
        import os
        logo_path = os.path.join(os.path.dirname(__file__), "LOGO_FD.png")
        if os.path.exists(logo_path):
            try:
                with open(logo_path, "rb") as f:
                    logo_bytes = f.read()
                st.image(logo_bytes, width="stretch")
            except Exception as e:
                st.error(f"Erro ao carregar logotipo: {e}")
                st.title("📊 FD Consultoria de Dados")
        else:
            st.title("📊 FD Consultoria de Dados")
        st.markdown("### Análise de Vendas")
        groq_key = st.text_input("🔑 Sua API Key Groq", type="password", help="Chave da Groq para consultas")
        st.divider()
        st.subheader("📁 Configuração")
        
        # Seleção de modo de dados
        input_method = st.radio("Origem dos dados", ["📁 Diretório Local", "☁️ Upload de Arquivos"])
        
        path = None
        uploaded_files = None
        
        if input_method == "📁 Diretório Local":
            path = st.text_input("Diretório dos arquivos", value=r"D:\AMOSTRAS_TESTES\ENGENHARIA_IA")
        else:
            uploaded_files = st.file_uploader(
                "Upload dos arquivos CSV", 
                type=["csv"], 
                accept_multiple_files=True, 
                help="Selecione Produtos.csv, clientes.csv, Loja.csv, Vendas.csv"
            )
            
        carregar = st.button("🔄 Carregar Arquivos", type="primary")
        st.divider()
        if st.button("🧹 Limpar Sessão"):
            for key in ['arquivos', 'df_completo', 'indicadores', 'validacoes', 'messages']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        st.caption("Versão Spec-Driven - FD Consultoria")
    return groq_key, input_method, path, uploaded_files, carregar

def exibir_metricas(indicadores):
    """Exibe os cards de métricas principais."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Faturamento Total", formatar_numero_br(indicadores['visao_geral'].get('faturamento_total', 0)))
    with col2:
        st.metric("Total de Vendas", f"{indicadores['visao_geral'].get('total_vendas', 0):,}")
    with col3:
        st.metric("Ticket Médio", formatar_numero_br(indicadores['visao_geral'].get('ticket_medio', 0)))
    with col4:
        st.metric("Produtos Vendidos", f"{indicadores['visao_geral'].get('total_produtos_vendidos', 0):,}")

    if 'lucro_total' in indicadores['visao_geral']:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Lucro Total", formatar_numero_br(indicadores['visao_geral']['lucro_total']))
        with col2:
            st.metric("Margem Média", f"{indicadores['visao_geral'].get('margem_media', 0):.1f}%")

def exibir_abas(df_completo, indicadores):
    """Cria as abas de dados (sem o chat, que ficará fora)."""
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dados Completos", "🏆 Top Produtos", "👥 Top Clientes", "🏬 Desempenho Lojas"
    ])

    with tab1:
        st.dataframe(df_completo.head(100), width="stretch")
        st.caption(f"Mostrando 100 de {len(df_completo)} registros")

    with tab2:
        if indicadores['por_produto']:
            st.dataframe(pd.DataFrame(indicadores['por_produto']), width="stretch")
        else:
            st.info("Sem dados de produtos")

    with tab3:
        if indicadores['por_cliente']:
            st.dataframe(pd.DataFrame(indicadores['por_cliente']), width="stretch")
        else:
            st.info("Sem dados de clientes")

    with tab4:
        if indicadores['por_loja']:
            st.dataframe(pd.DataFrame(indicadores['por_loja']), width="stretch")
        else:
            st.info("Sem dados de lojas")

def exibir_chat(groq_key, indicadores):
    """Exibe o chat fora das tabs para evitar erro do Streamlit."""
    st.subheader("💬 Chat de Análise")
    
    # Histórico
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Input (agora fora das tabs)
    if prompt := st.chat_input("Faça sua pergunta sobre as vendas..."):
        if not groq_key:
            st.warning("⚠️ Insira sua API Key na barra lateral")
            return
        
        from llm_client import consultar_llm
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Analisando dados..."):
                try:
                    resposta = consultar_llm(groq_key, prompt, indicadores)
                    st.markdown(resposta)
                    st.session_state.messages.append({"role": "assistant", "content": resposta})
                except Exception as e:
                    st.error(f"Erro ao consultar LLM: {str(e)}")