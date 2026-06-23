import pytest
import pandas as pd
import numpy as np
from forecaster import prever_vendas_12_meses

def test_prever_vendas_insufficient_data():
    # Test None
    df, status, msg = prever_vendas_12_meses(None)
    assert df is None
    assert status == "erro_dados_insuficientes"

    # Test empty dataframe
    df, status, msg = prever_vendas_12_meses(pd.DataFrame())
    assert df is None
    assert status == "erro_dados_insuficientes"

    # Test less than 3 months
    df_short = pd.DataFrame({'mes_ano': ['2026-01', '2026-02'], 'faturamento': [100, 110]})
    df, status, msg = prever_vendas_12_meses(df_short)
    assert df is None
    assert status == "erro_dados_insuficientes"

def test_prever_vendas_linear_only():
    # Test with 5 months of data (>= 3 and < 24)
    df_mensal = pd.DataFrame({
        'mes_ano': ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05'],
        'faturamento': [100.0, 110.0, 120.0, 130.0, 140.0]
    })
    
    df_proj, status, msg = prever_vendas_12_meses(df_mensal, coluna_valor='faturamento')
    
    assert status == "sucesso"
    assert "baseada apenas em Tendência Linear" in msg
    assert df_proj is not None
    # Total rows = 5 (history) + 12 (forecast) = 17 rows
    assert len(df_proj) == 17
    
    # Check historical rows
    hist = df_proj[df_proj['tipo'] == 'Histórico']
    assert len(hist) == 5
    assert hist['real'].iloc[0] == 100.0
    assert hist['previsto'].iloc[0] == 100.0
    
    # Check forecast rows
    forecast = df_proj[df_proj['tipo'] == 'Previsão']
    assert len(forecast) == 12
    assert forecast['real'].isna().all()
    # Check that predicted trend continues upwards: 150, 160, ...
    assert forecast['previsto'].iloc[0] == pytest.approx(150.0, 0.01)
    assert forecast['previsto'].iloc[11] == pytest.approx(260.0, 0.01)

def test_prever_vendas_with_seasonality():
    # Test with 24 months of data (>= 24)
    # Let's construct a pattern with linear trend + a strong seasonality
    # Month 12 and 24 (December) have high sales, Month 1 and 13 (January) have low sales.
    meses = []
    valores = []
    base_year = 2024
    for i in range(24):
        year = base_year + (i // 12)
        month = (i % 12) + 1
        mes_ano = f"{year}-{month:02d}"
        meses.append(mes_ano)
        
        # Linear trend: 100 + i * 5
        trend = 100.0 + i * 5.0
        # Seasonality: December (+50), January (-50), others (0)
        seasonal_effect = 0.0
        if month == 12:
            seasonal_effect = 50.0
        elif month == 1:
            seasonal_effect = -50.0
        valores.append(trend + seasonal_effect)
        
    df_mensal = pd.DataFrame({
        'mes_ano': meses,
        'faturamento': valores
    })
    
    df_proj, status, msg = prever_vendas_12_meses(df_mensal, coluna_valor='faturamento')
    
    assert status == "sucesso"
    assert "Sazonalidade Mensal Histórica" in msg
    assert df_proj is not None
    # Total rows = 24 + 12 = 36 rows
    assert len(df_proj) == 36
    
    forecast = df_proj[df_proj['tipo'] == 'Previsão']
    assert len(forecast) == 12
    
    # Trend for first forecast month (fut_x = 24, i = 1): 100 + 24 * 5 = 220
    # January seasonality should be negative (around -50)
    # So forecast previsto for Jan 2026 (index 0 of forecast) should be around 220 - 50 = 170
    assert forecast['previsto'].iloc[0] == pytest.approx(170.0, 10.0)
    
    # Trend for Dec 2026 (index 11 of forecast, fut_x = 35): 100 + 35 * 5 = 275
    # December seasonality should be positive (+50)
    # So forecast previsto for Dec 2026 should be around 275 + 50 = 325
    assert forecast['previsto'].iloc[11] == pytest.approx(325.0, 10.0)

def test_prever_vendas_non_negative_boundary():
    # Test boundary condition where trend goes negative
    # Descending trend: 100, 80, 60, 40, 20
    df_mensal = pd.DataFrame({
        'mes_ano': ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05'],
        'faturamento': [100.0, 80.0, 60.0, 40.0, 20.0]
    })
    
    df_proj, status, msg = prever_vendas_12_meses(df_mensal, coluna_valor='faturamento')
    
    forecast = df_proj[df_proj['tipo'] == 'Previsão']
    # The trend is y = -20 * x + 100.
    # For future indices, it goes to 0, -20, -40, etc.
    # The function max(0.0, val_pred) should ensure previsto and limite_inferior are non-negative.
    for val in forecast['previsto']:
        assert val >= 0.0
    for val in forecast['limite_inferior']:
        assert val >= 0.0
