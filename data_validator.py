import pandas as pd

def validar_relacionamentos(arquivos):
    """
    Verifica integridade referencial entre vendas e as demais tabelas.
    Retorna (dict_validacoes, bool_todos_validos).
    """
    if not all(k in arquivos for k in ['vendas', 'produtos', 'clientes', 'lojas']):
        return None, False

    df_vendas = arquivos['vendas']['df_original']
    df_produtos = arquivos['produtos']['df_original']
    df_clientes = arquivos['clientes']['df_original']
    df_lojas = arquivos['lojas']['df_original']

    validacoes = {
        'produtos': {'total': 0, 'validos': 0, 'invalidos': 0},
        'clientes': {'total': 0, 'validos': 0, 'invalidos': 0},
        'lojas': {'total': 0, 'validos': 0, 'invalidos': 0}
    }

    cod_prod_validos = set(df_produtos['cod_produto'].dropna().astype(str))
    cod_cli_validos = set(df_clientes['cod_cliente'].dropna().astype(str))
    cod_loja_validos = set(df_lojas['cod_loja'].dropna().astype(str))

    vendas_prod = df_vendas['cod_produto'].dropna().astype(str)
    vendas_cli = df_vendas['cod_cliente'].dropna().astype(str)
    vendas_loja = df_vendas['cod_loja'].dropna().astype(str)

    validacoes['produtos']['total'] = len(vendas_prod)
    validacoes['produtos']['validos'] = vendas_prod.isin(cod_prod_validos).sum()
    validacoes['produtos']['invalidos'] = validacoes['produtos']['total'] - validacoes['produtos']['validos']

    validacoes['clientes']['total'] = len(vendas_cli)
    validacoes['clientes']['validos'] = vendas_cli.isin(cod_cli_validos).sum()
    validacoes['clientes']['invalidos'] = validacoes['clientes']['total'] - validacoes['clientes']['validos']

    validacoes['lojas']['total'] = len(vendas_loja)
    validacoes['lojas']['validos'] = vendas_loja.isin(cod_loja_validos).sum()
    validacoes['lojas']['invalidos'] = validacoes['lojas']['total'] - validacoes['lojas']['validos']

    todos_validos = all(v['invalidos'] == 0 for v in validacoes.values())
    return validacoes, todos_validos