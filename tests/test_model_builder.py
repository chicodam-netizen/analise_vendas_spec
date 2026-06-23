import pytest
import pandas as pd
from model_builder import construir_modelo_dimensional

def test_construir_modelo_dimensional_success():
    # Setup mock tables
    df_vendas = pd.DataFrame({
        'cod_produto': [1, 2],
        'cod_cliente': [101, 102],
        'cod_loja': [10, 20],
        'quantidade': [2, 5],
        'Valor_Unitario': [100.0, 50.0],
        'Data': ['2026-06-22', '2026-07-23']
    })
    df_produtos = pd.DataFrame({
        'cod_produto': [1, 2],
        'nome_produto': ['Produto A', 'Produto B'],
        'custo': [60.0, 45.0]
    })
    df_clientes = pd.DataFrame({
        'cod_cliente': [101, 102],
        'nome_cliente': ['Cliente A', 'Cliente B']
    })
    df_lojas = pd.DataFrame({
        'cod_loja': [10, 20],
        'descricao': ['Loja Centro', 'Loja Sul']
    })

    arquivos = {
        'vendas': {'df_original': df_vendas},
        'produtos': {'df_original': df_produtos},
        'clientes': {'df_original': df_clientes},
        'lojas': {'df_original': df_lojas}
    }

    df_completo, err = construir_modelo_dimensional(arquivos)
    
    assert err is None
    assert df_completo is not None
    assert len(df_completo) == 2
    
    # Test merged columns
    assert 'nome_produto' in df_completo.columns
    assert 'nome_cliente' in df_completo.columns
    assert 'descricao' in df_completo.columns
    
    # Test calculations
    # Row 0: Valor_Unitario=100.0, custo=60.0, quantidade=2
    # lucro_unitario = 40.0, lucro_total = 80.0, margem_percentual = 40.0
    assert df_completo['lucro_unitario'].iloc[0] == 40.0
    assert df_completo['lucro_total'].iloc[0] == 80.0
    assert df_completo['margem_percentual'].iloc[0] == 40.0
    
    # Row 1: Valor_Unitario=50.0, custo=45.0, quantidade=5
    # lucro_unitario = 5.0, lucro_total = 25.0, margem_percentual = 10.0
    assert df_completo['lucro_unitario'].iloc[1] == 5.0
    assert df_completo['lucro_total'].iloc[1] == 25.0
    assert df_completo['margem_percentual'].iloc[1] == 10.0

    # Test date extractions
    assert df_completo['ano'].iloc[0] == 2026
    assert df_completo['mes'].iloc[0] == 6
    assert df_completo['dia'].iloc[0] == 22
    assert df_completo['dia_semana'].iloc[0] == 'Monday'
    assert df_completo['mes_ano'].iloc[0] == '2026-06'
    
    assert df_completo['ano'].iloc[1] == 2026
    assert df_completo['mes'].iloc[1] == 7
    assert df_completo['dia'].iloc[1] == 23
    assert df_completo['dia_semana'].iloc[1] == 'Thursday'
    assert df_completo['mes_ano'].iloc[1] == '2026-07'

def test_construir_modelo_dimensional_zero_price():
    # Setup mock tables with zero/negative price to verify division safety
    df_vendas = pd.DataFrame({
        'cod_produto': ['1'],
        'cod_cliente': ['101'],
        'cod_loja': ['10'],
        'quantidade': [2],
        'Valor_Unitario': [0.0], # Zero price
        'Data': ['2026-06-22']
    })
    df_produtos = pd.DataFrame({
        'cod_produto': ['1'],
        'custo': [10.0]
    })
    df_clientes = pd.DataFrame({'cod_cliente': ['101']})
    df_lojas = pd.DataFrame({'cod_loja': ['10']})

    arquivos = {
        'vendas': {'df_original': df_vendas},
        'produtos': {'df_original': df_produtos},
        'clientes': {'df_original': df_clientes},
        'lojas': {'df_original': df_lojas}
    }

    df_completo, err = construir_modelo_dimensional(arquivos)
    assert err is None
    assert df_completo['lucro_unitario'].iloc[0] == -10.0
    assert df_completo['lucro_total'].iloc[0] == -20.0
    # margem_percentual should be NaN or not set for Valor_Unitario <= 0
    assert pd.isna(df_completo['margem_percentual'].iloc[0])

def test_construir_modelo_dimensional_failure():
    # Trigger an error, e.g. passing None or missing critical keys
    df_completo, err = construir_modelo_dimensional(None)
    assert df_completo is None
    assert err is not None
