import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from forecaster import prever_vendas_12_meses

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

def exibir_graficos(df_filtrado, df_completo_original, mes_inicio, mes_fim):
    """Exibe os 3 gráficos principais solicitados pelo usuário."""
    st.markdown("### 📊 Painel de Gráficos e Previsões")
    
    if df_filtrado is None or df_filtrado.empty:
        st.warning("Sem dados disponíveis no período selecionado.")
        return

    # Controles locais para o gráfico
    col_sel, _ = st.columns([2, 2])
    with col_sel:
        metric_selector = st.radio(
            "Visualizar métrica nos gráficos 1 e 3:",
            ["Faturamento (R$)", "Quantidade de Unidades"],
            horizontal=True,
            key="metrica_graficos"
        )
    
    col1, col2 = st.columns(2)
    
    # ------------------ GRÁFICO 1: EVOLUÇÃO DAS VENDAS ------------------
    with col1:
        coluna_grafico = 'Valor_Final' if metric_selector == "Faturamento (R$)" else 'quantidade'
        rotulo_y = 'Faturamento (R$)' if metric_selector == "Faturamento (R$)" else 'Unidades Vendidas'
        
        # Agrupar por mes_ano
        df_evolucao = df_filtrado.groupby('mes_ano')[coluna_grafico].sum().reset_index()
        df_evolucao = df_evolucao.sort_values('mes_ano')
        
        fig_evolucao = px.line(
            df_evolucao,
            x='mes_ano',
            y=coluna_grafico,
            labels={'mes_ano': 'Mês/Ano', coluna_grafico: rotulo_y},
            title=f'Evolução de Vendas no Período ({rotulo_y})',
            markers=True
        )
        
        # Cores elegantes (azul FD)
        fig_evolucao.update_traces(line_color='#2A6F97', line_width=3, marker=dict(size=7))
        fig_evolucao.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.15)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.15)'),
            margin=dict(l=20, r=20, t=50, b=20),
            height=400
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)

    # ------------------ GRÁFICO 2: TOP 10 PRODUTOS POR LOJA ------------------
    with col2:
        # Criar nomes de exibição amigáveis
        df_prod = df_filtrado.copy()
        if 'marca' in df_prod.columns and 'tipo' in df_prod.columns:
            df_prod['produto_nome'] = df_prod['marca'].astype(str) + " - " + df_prod['tipo'].astype(str)
        else:
            df_prod['produto_nome'] = df_prod['cod_produto'].astype(str)
            
        if 'descricao' in df_prod.columns:
            df_prod['loja_nome'] = df_prod['descricao'].astype(str)
        else:
            df_prod['loja_nome'] = "Loja " + df_prod['cod_loja'].astype(str)
            
        # Encontrar top 10 produtos globais no período filtrado
        top_10_prod = df_prod.groupby('produto_nome')['Valor_Final'].sum().nlargest(10).index.tolist()
        
        df_top_10 = df_prod[df_prod['produto_nome'].isin(top_10_prod)]
        
        # Agrupar por produto e loja
        df_grouped = df_top_10.groupby(['produto_nome', 'loja_nome'])[coluna_grafico].sum().reset_index()
        
        # Criar gráfico de barras horizontais empilhadas
        fig_barras = px.bar(
            df_grouped,
            x=coluna_grafico,
            y='produto_nome',
            color='loja_nome',
            orientation='h',
            title=f'Top 10 Produtos por Loja ({rotulo_y})',
            labels={coluna_grafico: rotulo_y, 'produto_nome': 'Produto', 'loja_nome': 'Loja'},
            category_orders={"produto_nome": top_10_prod[::-1]}, # Ordenado do maior para o menor
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        
        fig_barras.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.15)'),
            yaxis=dict(showgrid=False),
            margin=dict(l=20, r=20, t=50, b=100),
            height=400,
            legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_barras, use_container_width=True)

    # ------------------ GRÁFICO 3: PREVISÃO DE VENDAS ------------------
    st.markdown("#### 🔮 Análise Preditiva de Vendas (Próximos 12 Meses)")
    
    # Agrupar dados históricos completos ATÉ o período final selecionado (mes_fim)
    df_mensal_original = df_completo_original[df_completo_original['mes_ano'] <= mes_fim].groupby('mes_ano').agg(
        faturamento=('Valor_Final', 'sum'),
        quantidade=('quantidade', 'sum')
    ).reset_index()
    
    coluna_pred = 'faturamento' if metric_selector == "Faturamento (R$)" else 'quantidade'
    
    df_proj, status, msg_pred = prever_vendas_12_meses(df_mensal_original, coluna_valor=coluna_pred)
    
    if df_proj is not None:
        fig_pred = go.Figure()
        
        df_hist = df_proj[df_proj['tipo'] == 'Histórico']
        df_future = df_proj[df_proj['tipo'] == 'Previsão']
        
        # Histórico Real
        fig_pred.add_trace(go.Scatter(
            x=df_hist['mes_ano'],
            y=df_hist['real'],
            mode='lines+markers',
            name='Histórico Real',
            line=dict(color='#2A6F97', width=3),
            marker=dict(size=6)
        ))
        
        # Previsão Conectada
        if not df_hist.empty and not df_future.empty:
            df_future_conn = pd.concat([df_hist.tail(1), df_future])
        else:
            df_future_conn = df_future
            
        fig_pred.add_trace(go.Scatter(
            x=df_future_conn['mes_ano'],
            y=df_future_conn['previsto'],
            mode='lines+markers',
            name='Previsão Futura',
            line=dict(color='#E65F2B', width=3, dash='dash'),
            marker=dict(size=6)
        ))
        
        # Intervalo de Confiança Sombreado
        if not df_future.empty:
            fig_pred.add_trace(go.Scatter(
                x=pd.concat([df_future['mes_ano'], df_future['mes_ano'].iloc[::-1]]),
                y=pd.concat([df_future['limite_superior'], df_future['limite_inferior'].iloc[::-1]]),
                fill='toself',
                fillcolor='rgba(230, 95, 43, 0.12)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                name='Intervalo de Confiança (95%)'
            ))
            
        fig_pred.update_layout(
            title=f'Previsão de Vendas ({rotulo_y})',
            xaxis_title='Mês/Ano',
            yaxis_title=rotulo_y,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.15)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.15)'),
            margin=dict(l=20, r=20, t=50, b=20),
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_pred, use_container_width=True)
        
        # Exibe status/mensagem do forecaster
        if status == "sucesso":
            st.info(f"💡 **Modelo de Previsão**: {msg_pred}")
        else:
            st.warning(f"⚠️ {msg_pred}")
    else:
        st.warning(f"Não foi possível gerar a previsão de vendas: {msg_pred}")