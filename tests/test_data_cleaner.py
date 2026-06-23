import pytest
import pandas as pd
import numpy as np
from data_cleaner import limpar_valor_numerico, converter_para_datetime, identificar_tipos_colunas, limpar_dataframe

def test_limpar_valor_numerico():
    assert limpar_valor_numerico("R$ 1.250,50") == 1250.50
    assert limpar_valor_numerico("123,45") == 123.45
    assert limpar_valor_numerico("  -1.200,99  ") == -1200.99
    assert limpar_valor_numerico(100.5) == 100.5
    assert limpar_valor_numerico(None) is None
    assert limpar_valor_numerico("") is None
    assert limpar_valor_numerico("1.250.300,45") == 1250300.45
    assert limpar_valor_numerico("not a number") is None

def test_converter_para_datetime():
    # Test series with various valid date formats
    s1 = pd.Series(['2026-06-22', '2026/06/22'])
    c1 = converter_para_datetime(s1)
    assert c1.iloc[0] == pd.Timestamp('2026-06-22')

    s2 = pd.Series(['22/06/2026', '22-06-2026'])
    c2 = converter_para_datetime(s2)
    assert c2.iloc[0] == pd.Timestamp('2026-06-22')

    # Test series with mix of valid dates and empty values
    s3 = pd.Series(['22/06/2026', None, ''])
    c3 = converter_para_datetime(s3)
    assert c3.iloc[0] == pd.Timestamp('2026-06-22')
    assert pd.isna(c3.iloc[1])

def test_identificar_tipos_colunas():
    df = pd.DataFrame({
        'cod_produto': [str(i) for i in range(20)],
        'Data_Venda': ['2026-06-22'] * 20,
        'Valor_Unitario': ['10,50'] * 20,
        'Descricao': [f'Produto {i}' for i in range(20)],
        'categoria': ['Cat A'] * 20
    })
    
    tipos = identificar_tipos_colunas(df)
    assert 'cod_produto' in tipos['ids']
    assert 'Data_Venda' in tipos['datas']
    assert 'Valor_Unitario' in tipos['numericas']
    assert 'Descricao' in tipos['texto']
    assert 'categoria' in tipos['categorias']

def test_limpar_dataframe():
    df = pd.DataFrame({
        'cod_produto': ['  1  ', '2', 'None'],
        'Data_Venda': ['22/06/2026', '23/06/2026', None],
        'Valor_Unitario': ['R$ 1.250,50', '300,00', ''],
        'Descricao': ['  Produto A  ', 'Produto B', 'nan']
    })

    df_limpo, tipos = limpar_dataframe(df)

    assert df_limpo['cod_produto'].iloc[0] == '1'
    assert df_limpo['cod_produto'].iloc[2] is None
    assert df_limpo['Data_Venda'].iloc[0] == pd.Timestamp('2026-06-22')
    assert df_limpo['Valor_Unitario'].iloc[0] == 1250.50
    assert df_limpo['Valor_Unitario'].iloc[1] == 300.00
    assert pd.isna(df_limpo['Valor_Unitario'].iloc[2])
    assert df_limpo['Descricao'].iloc[0] == 'Produto A'
    assert df_limpo['Descricao'].iloc[2] is None
