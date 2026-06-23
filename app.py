import streamlit as st
from data_loader import carregar_arquivos_upload
from data_cleaner import limpar_dataframe
from data_validator import validar_relacionamentos
from model_builder import construir_modelo_dimensional
from analytics import gerar_indicadores
from ui import exibir_sidebar, exibir_metricas, exibir_abas, exibir_chat, exibir_graficos

def main():
    st.set_page_config(page_title="FD Consultoria - Análise de Vendas", page_icon="📊", layout="wide")
    st.title("📈 Análise de Vendas - FD Consultoria")

    # Inicializa estado da sessão
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar
    groq_key, uploaded_files, carregar = exibir_sidebar()

    if carregar:
        with st.spinner("Carregando arquivos..."):
            # Mapeia os arquivos enviados por upload
            mapeamento_arquivos = {}
            if uploaded_files:
                for f in uploaded_files:
                    name_lower = f.name.lower()
                    if "produto" in name_lower:
                        mapeamento_arquivos['produtos'] = f
                    elif "cliente" in name_lower:
                        mapeamento_arquivos['clientes'] = f
                    elif "loja" in name_lower:
                        mapeamento_arquivos['lojas'] = f
                    elif "venda" in name_lower:
                        mapeamento_arquivos['vendas'] = f
            
            arquivos, msg = carregar_arquivos_upload(mapeamento_arquivos)

        if arquivos:
                # Limpeza de cada DataFrame
                for tipo in arquivos:
                    df_limpo, tipos = limpar_dataframe(arquivos[tipo]['df_original'])
                    arquivos[tipo]['df'] = df_limpo
                    arquivos[tipo]['tipos'] = tipos
                st.session_state.arquivos = arquivos
                st.session_state.mensagem = msg

                # Validação
                validacoes, todos_validos = validar_relacionamentos(arquivos)
                st.session_state.validacoes = validacoes
                if todos_validos:
                    df_completo, erro = construir_modelo_dimensional(arquivos)
                    if df_completo is not None:
                        st.session_state.df_completo = df_completo
                        indicadores = gerar_indicadores(df_completo)
                        st.session_state.indicadores = indicadores
                        st.success("✅ Dados carregados e validados com sucesso!")
                    else:
                        st.error(f"❌ Erro no modelo dimensional: {erro}")
                else:
                    st.warning("⚠️ Atenção: existem registros inválidos nos relacionamentos")
            else:
                st.error(f"❌ {msg}")

    # Exibe logs e conteúdo se houver dados
    if 'mensagem' in st.session_state:
        with st.expander("📋 Log de Carregamento", expanded=False):
            st.text(st.session_state.mensagem)

    if 'validacoes' in st.session_state and st.session_state.validacoes:
        v = st.session_state.validacoes
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Produtos", f"{v['produtos']['validos']}/{v['produtos']['total']}",
                      delta=f"{v['produtos']['invalidos']} inválidos" if v['produtos']['invalidos'] else "OK")
        with col2:
            st.metric("Clientes", f"{v['clientes']['validos']}/{v['clientes']['total']}",
                      delta=f"{v['clientes']['invalidos']} inválidos" if v['clientes']['invalidos'] else "OK")
        with col3:
            st.metric("Lojas", f"{v['lojas']['validos']}/{v['lojas']['total']}",
                      delta=f"{v['lojas']['invalidos']} inválidos" if v['lojas']['invalidos'] else "OK")

    if 'df_completo' in st.session_state and 'indicadores' in st.session_state:
        df_completo = st.session_state.df_completo
        
        # Filtro de Período (Mês/Ano)
        if 'mes_ano' in df_completo.columns:
            meses_anos = sorted(df_completo['mes_ano'].dropna().unique().tolist())
            if meses_anos:
                st.markdown("### 🔍 Filtro de Período")
                col_ini, col_fim = st.columns(2)
                with col_ini:
                    mes_inicio = st.selectbox("Mês/Ano Inicial", meses_anos, index=0)
                with col_fim:
                    mes_fim = st.selectbox("Mês/Ano Final", meses_anos, index=len(meses_anos) - 1)
                
                # Validar período
                idx_ini = meses_anos.index(mes_inicio)
                idx_fim = meses_anos.index(mes_fim)
                
                if idx_ini > idx_fim:
                    st.error("❌ O Mês/Ano Inicial deve ser menor ou igual ao Mês/Ano Final.")
                    df_filtrado = df_completo.copy()
                    indicadores_filtrados = st.session_state.indicadores
                    mes_inicio = meses_anos[0]
                    mes_fim = meses_anos[-1]
                else:
                    df_filtrado = df_completo[(df_completo['mes_ano'] >= mes_inicio) & (df_completo['mes_ano'] <= mes_fim)].copy()
                    indicadores_filtrados = gerar_indicadores(df_filtrado)
            else:
                df_filtrado = df_completo.copy()
                indicadores_filtrados = st.session_state.indicadores
                mes_inicio = None
                mes_fim = None
        else:
            df_filtrado = df_completo.copy()
            indicadores_filtrados = st.session_state.indicadores
            mes_inicio = None
            mes_fim = None

        # Exibição do painel
        exibir_metricas(indicadores_filtrados)
        
        if mes_inicio and mes_fim:
            exibir_graficos(df_filtrado, df_completo, mes_inicio, mes_fim)
            
        exibir_abas(df_filtrado, indicadores_filtrados)
        st.divider()
        exibir_chat(groq_key, indicadores_filtrados)
    else:
        st.info("👋 Clique em 'Carregar Arquivos' na barra lateral para iniciar a análise.")
        with st.expander("📋 Formato esperado dos arquivos"):
            st.markdown("""
            **Produtos.csv**: cod_produto, marca, tipo, categoria, preco_unitario, custo, obs  
            **clientes.csv**: cod_cliente, nome_cliente, cidade, uf  
            **Loja.csv**: cod_loja, descricao  
            **Vendas.csv**: cod_Venda, cod_cliente, cod_loja, Data, cod_produto, quantidade, Valor_Unitario, Valor_Final
            """)

    st.markdown(
        """<div style="text-align: center; color: gray; margin-top: 50px;"><hr><p>FD Consultoria de Dados - Análise de Vendas (Spec-Driven)</p></div>""",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()