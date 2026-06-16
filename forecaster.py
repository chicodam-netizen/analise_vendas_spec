import pandas as pd
import numpy as np

def prever_vendas_12_meses(df_mensal, coluna_valor='faturamento'):
    """
    Realiza uma análise preditiva para os próximos 12 meses.
    Recebe um DataFrame agrupado por 'mes_ano' (formato YYYY-MM) e a coluna de valores.
    Retorna (df_projeção, status_code, mensagem)
    
    O DataFrame de retorno contém:
    - 'mes_ano': string YYYY-MM
    - 'real': valor real (ou None se for projeção)
    - 'previsto': valor previsto
    - 'limite_inferior': limite inferior do intervalo de confiança
    - 'limite_superior': limite superior do intervalo de confiança
    - 'tipo': 'Histórico' ou 'Previsão'
    """
    if df_mensal is None or df_mensal.empty or len(df_mensal) < 3:
        return None, "erro_dados_insuficientes", "Quantidade de dados históricos insuficiente (mínimo de 3 meses necessário para projeção)."

    # Ordenar cronologicamente
    df = df_mensal.sort_values('mes_ano').reset_index(drop=True)
    n = len(df)
    
    # Índices de tempo (0, 1, 2, ..., n-1)
    x = np.arange(n)
    y = df[coluna_valor].values
    
    # Regressão linear simples para obter a tendência: y = a * x + b
    a, b = np.polyfit(x, y, 1)
    y_trend = a * x + b
    
    # Calcular resíduos
    residuos = y - y_trend
    std_residuos = np.std(residuos) if len(residuos) > 1 else (y.mean() * 0.1)
    
    # Sazonalidade
    sazonalidade = np.zeros(12) # padrão sem sazonalidade (aditiva = 0)
    has_seasonality = False
    
    if n >= 24:
        # Se temos 24 meses ou mais, calculamos sazonalidade mensal
        # Extrair o mês calendário (1-12) para cada mês no histórico
        df['mes_calendario'] = pd.to_datetime(df['mes_ano']).dt.month
        df['residuo'] = residuos
        
        # Sazonalidade aditiva: média dos resíduos por mês calendário
        fatores_residuos = df.groupby('mes_calendario')['residuo'].mean()
        
        # Normalizar para que a soma dos fatores sazonais aditivos seja exatamente 0
        fatores_residuos = fatores_residuos - fatores_residuos.mean()
        
        # Guardar os fatores
        for m in range(1, 13):
            if m in fatores_residuos.index:
                sazonalidade[m-1] = fatores_residuos[m]
        has_seasonality = True
    
    # Histórico no formato de saída
    historico = []
    for i in range(n):
        val_real = float(y[i])
        val_pred = float(y_trend[i] + (sazonalidade[pd.to_datetime(df.loc[i, 'mes_ano']).month - 1] if has_seasonality else 0))
        # Ajustar para não ter valores negativos em previsões de faturamento/vendas
        val_pred = max(0.0, val_pred)
        
        historico.append({
            'mes_ano': df.loc[i, 'mes_ano'],
            'real': val_real,
            'previsto': val_real, # No histórico, mantemos o real como valor principal
            'limite_inferior': val_real,
            'limite_superior': val_real,
            'tipo': 'Histórico'
        })
        
    # Gerar os próximos 12 meses
    last_period = pd.Period(df['mes_ano'].max(), freq='M')
    previsoes = []
    
    # Se a tendência for decrescente e levar a valores negativos, amortecemos a queda
    for i in range(1, 13):
        fut_period = last_period + i
        fut_mes_ano = str(fut_period)
        fut_x = n + i - 1
        
        # Projeção da tendência
        fut_trend = a * fut_x + b
        
        # Adicionar sazonalidade correspondente se houver
        mes_cal = fut_period.month
        fut_saz = sazonalidade[mes_cal - 1] if has_seasonality else 0
        
        val_pred = fut_trend + fut_saz
        val_pred = max(0.0, val_pred) # Evitar faturamento ou quantidade negativa
        
        # Incerteza aumenta com o tempo (fator multiplicador simples)
        fator_tempo = np.sqrt(1 + 0.15 * i)
        margem = 1.96 * std_residuos * fator_tempo
        
        lim_inf = max(0.0, val_pred - margem)
        lim_sup = val_pred + margem
        
        previsoes.append({
            'mes_ano': fut_mes_ano,
            'real': None,
            'previsto': float(val_pred),
            'limite_inferior': float(lim_inf),
            'limite_superior': float(lim_sup),
            'tipo': 'Previsão'
        })
        
    df_resultado = pd.DataFrame(historico + previsoes)
    
    # Criar mensagem de status
    if has_seasonality:
        msg = "Previsão calculada com base em Tendência Linear e Sazonalidade Mensal Histórica (24+ meses)."
    else:
        msg = f"Previsão baseada apenas em Tendência Linear (histórico contém {n} meses; mínimo de 24 meses necessários para computar sazonalidade)."
        
    return df_resultado, "sucesso", msg
