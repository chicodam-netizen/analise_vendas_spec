# PRD: Painel de Gráficos Interativos e Análise Preditiva de Vendas

## 1. Contexto e Motivação
Para complementar a análise tabular e as respostas em linguagem natural do chat assistente, a FD Consultoria de Dados necessita de representações gráficas interativas e suporte a projeções de negócio (forecasting) integrados à tela principal da aplicação. 

Visualizações interativas e previsões estatísticas apoiam a liderança na tomada de decisões estratégicas sobre estoque, foco de marketing e metas de faturamento.

---

## 2. Requisitos Funcionais

### RF1: Filtro Temporal Global na Interface Principal
* **Descrição**: Permitir parametrizar as visualizações de vendas por um período dinâmico de início e fim.
* **Comportamento**: 
  - Dois seletores de caixa suspensa (selectbox) na tela principal contendo a lista única de "Mês/Ano" presentes no histórico de vendas.
  - O filtro inicial deve ser menor ou igual ao final; caso contrário, emitir um alerta visual informando o erro.
  - Ao alterar o período, atualizar automaticamente métricas principais, tabelas e gráficos da tela principal.

### RF2: Evolução Temporal das Vendas (Linhas)
* **Descrição**: Gráfico de linha mostrando a evolução temporal das vendas ao longo do período selecionado.
* **Comportamento**:
  - Permitir alternar dinamicamente a métrica visualizada entre "Faturamento (R$)" e "Quantidade de Unidades".
  - Plotar os meses no eixo X e os valores agregados no eixo Y.

### RF3: Comparativo de Top 10 Produtos por Loja
* **Descrição**: Exibir os 10 principais produtos do período selecionado com a distribuição de suas vendas pelas diferentes filiais/lojas.
* **Comportamento**:
  - Identificar os 10 produtos com maior faturamento no período selecionado.
  - Exibir um gráfico de barras horizontais empilhadas.
  - O eixo Y deve listar os produtos de forma ordenada (do maior para o menor faturamento).
  - O eixo X deve apresentar o volume acumulado (faturamento ou unidades).
  - O empilhamento por cores representa a contribuição de cada loja.

### RF4: Previsão de Vendas (Próximos 12 Meses)
* **Descrição**: Realizar projeção estatística de vendas/faturamento para os próximos 12 meses a partir do último período selecionado.
* **Comportamento**:
  - Utilizar Decomposição de Série Temporal com regressão linear e fatores sazonais aditivos.
  - Exibir no mesmo gráfico a linha sólida com o histórico real e uma linha pontilhada correspondente aos próximos 12 meses.
  - Apresentar uma região sombreada ao redor da previsão indicando o intervalo de confiança de 95%, que se expande à medida que se projeta mais distante no futuro.
  - Funcionar dinamicamente de acordo com a métrica selecionada (faturamento ou quantidade).

---

## 3. Requisitos Não Funcionais
* **Aparência e Usabilidade**: Utilizar a biblioteca Plotly Express para gráficos interativos premium que suportam foco (hover tooltips), zoom e ocultação de séries através da legenda.
* **Robustez de Dados**: Implementar tratamentos de fallback no algoritmo preditivo para bases pequenas (menos de 24 meses) para evitar falhas ou erros matemáticos.
* **Compatibilidade**: Layout 100% responsivo compatível com temas claro e escuro do Streamlit.
