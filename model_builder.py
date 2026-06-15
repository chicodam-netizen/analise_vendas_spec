import pandas as pd
from data_cleaner import converter_para_datetime

def construir_modelo_dimensional(arquivos):
    """
    Realiza os merges entre vendas e dimensões, adiciona colunas calculadas.
    Retorna (df_completo, mensagem_erro).
    """
    try:
        df_vendas = arquivos['vendas']['df_original'].copy()
        df_produtos = arquivos['produtos']['df_original'].copy()
        df_clientes = arquivos['clientes']['df_original'].copy()
        df_lojas = arquivos['lojas']['df_original'].copy()

        # Converte chaves para string
        df_vendas['cod_produto'] = df_vendas['cod_produto'].astype(str)
        df_vendas['cod_cliente'] = df_vendas['cod_cliente'].astype(str)
        df_vendas['cod_loja'] = df_vendas['cod_loja'].astype(str)
        df_produtos['cod_produto'] = df_produtos['cod_produto'].astype(str)
        df_clientes['cod_cliente'] = df_clientes['cod_cliente'].astype(str)
        df_lojas['cod_loja'] = df_lojas['cod_loja'].astype(str)

        df_completo = df_vendas.merge(df_produtos, on='cod_produto', how='left')
        df_completo = df_completo.merge(df_clientes, on='cod_cliente', how='left')
        df_completo = df_completo.merge(df_lojas, on='cod_loja', how='left')

        # Colunas de lucro e margem
        if 'custo' in df_completo.columns and 'Valor_Unitario' in df_completo.columns:
            df_completo['lucro_unitario'] = df_completo['Valor_Unitario'] - df_completo['custo']
            df_completo['lucro_total'] = df_completo['lucro_unitario'] * df_completo['quantidade']
            mask = df_completo['Valor_Unitario'] > 0
            df_completo.loc[mask, 'margem_percentual'] = (df_completo.loc[mask, 'lucro_unitario'] / df_completo.loc[mask, 'Valor_Unitario'] * 100).round(2)

        # Extração de datas
        if 'Data' in df_completo.columns:
            if not pd.api.types.is_datetime64_any_dtype(df_completo['Data']):
                df_completo['Data'] = converter_para_datetime(df_completo['Data'])
            if pd.api.types.is_datetime64_any_dtype(df_completo['Data']):
                df_completo['ano'] = df_completo['Data'].dt.year
                df_completo['mes'] = df_completo['Data'].dt.month
                df_completo['dia'] = df_completo['Data'].dt.day
                df_completo['dia_semana'] = df_completo['Data'].dt.day_name()
                df_completo['mes_ano'] = df_completo['Data'].dt.to_period('M').astype(str)

        return df_completo, None
    except Exception as e:
        return None, str(e)