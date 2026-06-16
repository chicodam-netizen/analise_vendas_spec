# Especificação Técnica – Sistema de Análise de Vendas (FD Consultoria)

## 1. Visão Geral
Sistema web para análise de dados de vendas, desenvolvido com Streamlit. Permite carregar arquivos CSV (produtos, clientes, lojas, vendas), validar integridade referencial, calcular indicadores de negócio e interagir com um assistente LLM (Groq) para responder perguntas baseadas nos dados.

## 2. Requisitos Funcionais

### RF01 – Carregamento de arquivos
- O sistema deve ler 4 arquivos CSV: `Produtos.csv`, `clientes.csv`, `Loja.csv`, `Vendas.csv`.
- Deve detectar automaticamente o separador (`,`, `;`, `\t`) e o encoding (`utf-8`, `latin1`, `cp1252`).
- Deve suportar duas formas de entrada de arquivos:
  - Diretório local contendo os arquivos (útil para desenvolvimento local).
  - Upload de múltiplos arquivos pela interface web com pareamento inteligente de nomes (essencial para deploy em produção/nuvem).

### RF02 – Limpeza e tipagem de dados
- Colunas numéricas devem ser convertidas para `float` (tratando vírgula, pontos e caracteres não numéricos).
- Colunas de data devem ser convertidas para `datetime` (suporte a múltiplos formatos).
- Colunas de texto devem ter espaços removidos e valores nulos padronizados.
- Colunas de ID/Código devem ser tratadas como string.

### RF03 – Validação de relacionamentos
- Verificar se todos os `cod_produto`, `cod_cliente` e `cod_loja` presentes na tabela `Vendas` existem nas respectivas tabelas de dimensão.
- Exibir quantidade de registros válidos e inválidos.

### RF04 – Construção do modelo dimensional
- Realizar `join` entre `Vendas` e as dimensões (produtos, clientes, lojas).
- Calcular colunas derivadas: `lucro_unitario`, `lucro_total`, `margem_percentual`.
- Extrair componentes da data (ano, mês, dia da semana, mês/ano).

### RF05 – Geração de indicadores
- **Visão geral**: total de vendas, unidades vendidas, faturamento, ticket médio, lucro total, margem média.
- **Por produto**: faturamento, quantidade, margem, ordenado por faturamento.
- **Por cliente**: gasto total, número de compras, ticket médio por cliente.
- **Por loja**: faturamento, quantidade de vendas.
- **Séries temporais**: evolução diária e mensal do faturamento e volume de vendas.

### RF06 – Interface gráfica (Streamlit)
- Barra lateral contendo o logotipo corporativo `LOGO_FD.png` (ou título fallback em texto), campo para API Key da Groq, diretório dos dados, botão de carregamento e botão de limpeza de sessão.
- Filtro de período dinâmico (Mês/Ano Inicial e Final) na interface principal para refinar e re-calcular dados em cascata.
- Painel de Gráficos (Plotly): Linha temporal de vendas, barras empilhadas horizontais dos Top 10 Produtos por Loja, e projeção preditiva para 12 meses.
- Abas para visualização de dados completos, top produtos, top clientes, desempenho por loja e chat de análise.
- Chat interativo que utiliza o LLM (Groq) para responder perguntas com base nos indicadores calculados.

### RF07 – Integração com LLM (Groq)
- Gerar um resumo estruturado dos dados (indicadores + pergunta do usuário).
- Enviar para o modelo `llama-3.3-70b-versatile` com temperature 0.2.
- Exibir a resposta no chat.

## 3. Requisitos Não Funcionais

- **Modularidade**: código organizado em módulos por responsabilidade (loader, cleaner, validator, analytics, llm, ui).
- **Tratamento de erros**: exceções capturadas e mensagens amigáveis ao usuário.
- **Desempenho**: uso de pandas otimizado (groupby com agregadores simples).
- **Manutenibilidade**: constante centralizadas, tipagem explícita, docstrings.
- **Portabilidade**: funcionar em Windows/Linux, com dependências listadas em `requirements.txt`.

## 4. Arquitetura de Módulos

| Módulo               | Responsabilidade                                                                 |
|----------------------|----------------------------------------------------------------------------------|
| `config.py`          | Constantes, caminhos padrão, nomes de arquivos, colunas chave.                   |
| `data_loader.py`     | Leitura de CSV com detecção de separador/encoding.                               |
| `data_cleaner.py`    | Limpeza e conversão de tipos (numérico, data, texto).                            |
| `data_validator.py`  | Validação de integridade referencial entre vendas e dimensões.                   |
| `model_builder.py`   | Criação do modelo dimensional (joins, colunas calculadas).                       |
| `analytics.py`       | Cálculo dos indicadores de vendas (métricas, agregações, séries temporais).      |
| `forecaster.py`      | Análise preditiva e projeções de faturamento/vendas para 12 meses.               |
| `llm_client.py`      | Construção do resumo para LLM e comunicação com a API da Groq.                   |
| `ui.py`              | Componentes da interface Streamlit (sidebar, métricas, abas, chat, gráficos).    |
| `app.py`             | Ponto de entrada, coordena o fluxo de carregamento, filtros e aciona a UI.        |

## 5. Fluxo de Dados

1. Usuário informa caminho dos arquivos e clica em "Carregar".
2. `data_loader` carrega cada CSV (detecta separador/encoding).
3. `data_cleaner` limpa e define tipos de cada DataFrame.
4. `data_validator` verifica relacionamentos e exibe estatísticas.
5. `model_builder` faz merge das tabelas e gera `df_completo`.
6. `analytics` calcula indicadores a partir de `df_completo`.
7. Os dados limpos, o modelo e os indicadores são armazenados em `st.session_state`.
8. A interface (`ui.py`) exibe métricas, abas e habilita o chat.
9. No chat, a pergunta do usuário + resumo dos indicadores é enviada à Groq via `llm_client`.
10. A resposta é exibida e armazenada no histórico.

## 6. Dependências (requirements.txt)