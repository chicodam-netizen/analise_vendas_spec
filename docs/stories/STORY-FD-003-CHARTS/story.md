# STORY-FD-003-CHARTS: Gráficos Interativos e Análise Preditiva

## Descrição
Desenvolver um painel de gráficos interativos integrado com Plotly para apresentar a evolução temporal de vendas, top 10 produtos segmentados por loja, e um gráfico de forecasting estatístico projetando as vendas para os próximos 12 meses, parametrizados por seletores de período globais na interface.

---

## Critérios de Aceitação (AC)

- **AC1: Filtro de Período Principal**: Exibir seletores para Mês/Ano Inicial e Final na tela principal quando os dados estiverem carregados, recalculando dinamicamente as métricas e tabelas de todas as abas.
- **AC2: Gráfico de Evolução de Vendas**: Exibir um gráfico de linha do Plotly que reaja a um seletor de métrica ("Faturamento (R$)" vs. "Quantidade de Unidades") mostrando a evolução das vendas no período.
- **AC3: Gráfico de Distribuição Produto/Loja**: Exibir um gráfico de barras horizontais empilhadas comparando o faturamento ou quantidade dos 10 principais produtos do período selecionado, com empilhamento por loja.
- **AC4: Gráfico de Forecasting de 12 meses**: Exibir um gráfico preditivo que integre o histórico real com a projeção tracejada dos próximos 12 meses acompanhado por um intervalo de confiança sombreado expansível.
- **AC5: Robusteza do Modelo**: O algoritmo de projeção estatística deve se ajustar dinamicamente ao volume de dados históricos (com ou sem sazonalidade) sem travar a aplicação se o histórico for curto.

---

## File List
- [MODIFY] [requirements.txt](file:///d:/FD_CONSULTORIA/DESENVOLVIMENTO/analise_vendas_spec/requirements.txt)
- [NEW] [forecaster.py](file:///d:/FD_CONSULTORIA/DESENVOLVIMENTO/analise_vendas_spec/forecaster.py)
- [MODIFY] [ui.py](file:///d:/FD_CONSULTORIA/DESENVOLVIMENTO/analise_vendas_spec/ui.py)
- [MODIFY] [app.py](file:///d:/FD_CONSULTORIA/DESENVOLVIMENTO/analise_vendas_spec/app.py)
- [MODIFY] [SPEC.md](file:///d:/FD_CONSULTORIA/DESENVOLVIMENTO/analise_vendas_spec/SPEC.md)
