import pytest
import pandas as pd
from data_validator import validar_relacionamentos

def test_validar_relacionamentos_all_valid():
    # Setup mock dataframes where all relation keys exist
    df_vendas = pd.DataFrame({
        'cod_produto': ['1', '2', '1'],
        'cod_cliente': ['101', '102', '101'],
        'cod_loja': ['10', '10', '10']
    })
    df_produtos = pd.DataFrame({'cod_produto': ['1', '2', '3']})
    df_clientes = pd.DataFrame({'cod_cliente': ['101', '102']})
    df_lojas = pd.DataFrame({'cod_loja': ['10']})

    arquivos = {
        'vendas': {'df_original': df_vendas},
        'produtos': {'df_original': df_produtos},
        'clientes': {'df_original': df_clientes},
        'lojas': {'df_original': df_lojas}
    }

    validacoes, todos_validos = validar_relacionamentos(arquivos)
    
    assert todos_validos is True
    assert validacoes['produtos']['invalidos'] == 0
    assert validacoes['produtos']['total'] == 3
    assert validacoes['clientes']['invalidos'] == 0
    assert validacoes['lojas']['invalidos'] == 0

def test_validar_relacionamentos_with_invalid():
    # Setup mock dataframes where some keys are invalid/missing
    df_vendas = pd.DataFrame({
        'cod_produto': ['1', '999', '1'], # 999 is invalid product ID
        'cod_cliente': ['101', '102', '888'], # 888 is invalid client ID
        'cod_loja': ['10', '10', '777'] # 777 is invalid store ID
    })
    df_produtos = pd.DataFrame({'cod_produto': ['1', '2']})
    df_clientes = pd.DataFrame({'cod_cliente': ['101', '102']})
    df_lojas = pd.DataFrame({'cod_loja': ['10']})

    arquivos = {
        'vendas': {'df_original': df_vendas},
        'produtos': {'df_original': df_produtos},
        'clientes': {'df_original': df_clientes},
        'lojas': {'df_original': df_lojas}
    }

    validacoes, todos_validos = validar_relacionamentos(arquivos)
    
    assert todos_validos is False
    assert validacoes['produtos']['invalidos'] == 1
    assert validacoes['clientes']['invalidos'] == 1
    assert validacoes['lojas']['invalidos'] == 1

def test_validar_relacionamentos_missing_keys():
    # Missing 'lojas' table
    arquivos = {
        'vendas': {'df_original': pd.DataFrame()},
        'produtos': {'df_original': pd.DataFrame()},
        'clientes': {'df_original': pd.DataFrame()}
    }

    validacoes, todos_validos = validar_relacionamentos(arquivos)
    assert validacoes is None
    assert todos_validos is False
