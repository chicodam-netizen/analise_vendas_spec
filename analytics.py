import pandas as pd

def gerar_indicadores(df_completo):
    """Calcula métricas e agregações principais."""
    indicadores = {
        'visao_geral': {},
        'por_produto': [],
        'por_cliente': [],
        'por_loja': [],
        'series_temporais': {}
    }

    if df_completo is None or df_completo.empty:
        return indicadores

    # Visão geral
    indicadores['visao_geral'] = {
        'total_vendas': len(df_completo),
        'total_produtos_vendidos': int(df_completo['quantidade'].sum()) if 'quantidade' in df_completo.columns else 0,
        'faturamento_total': float(df_completo['Valor_Final'].sum()) if 'Valor_Final' in df_completo.columns else 0,
        'ticket_medio': float(df_completo['Valor_Final'].mean()) if 'Valor_Final' in df_completo.columns else 0,
        'quantidade_media_por_venda': float(df_completo['quantidade'].mean()) if 'quantidade' in df_completo.columns else 0
    }
    if 'lucro_total' in df_completo.columns:
        indicadores['visao_geral']['lucro_total'] = float(df_completo['lucro_total'].sum())
        indicadores['visao_geral']['margem_media'] = float(df_completo['margem_percentual'].mean()) if 'margem_percentual' in df_completo.columns else 0

    # Top produtos
    if 'cod_produto' in df_completo.columns:
        grupo = ['cod_produto']
        for col in ['marca', 'tipo', 'categoria']:
            if col in df_completo.columns:
                grupo.append(col)
        agg = {}
        if 'cod_Venda' in df_completo.columns:
            agg['cod_Venda'] = 'count'
        if 'quantidade' in df_completo.columns:
            agg['quantidade'] = 'sum'
        if 'Valor_Final' in df_completo.columns:
            agg['Valor_Final'] = 'sum'
        if agg:
            df_prod = df_completo.groupby(grupo).agg(agg).reset_index()
            rename = {}
            if 'cod_Venda' in agg:
                rename['cod_Venda'] = 'qtd_vendas'
            if 'quantidade' in agg:
                rename['quantidade'] = 'qtd_unidades'
            if 'Valor_Final' in agg:
                rename['Valor_Final'] = 'faturamento'
            df_prod.rename(columns=rename, inplace=True)
            if 'lucro_total' in df_completo.columns:
                lucro = df_completo.groupby(grupo)['lucro_total'].sum().reset_index()
                df_prod = df_prod.merge(lucro, on=grupo)
                if 'faturamento' in df_prod.columns:
                    df_prod['margem_media'] = (df_prod['lucro_total'] / df_prod['faturamento'] * 100).round(2)
            indicadores['por_produto'] = df_prod.sort_values('faturamento', ascending=False).head(20).to_dict('records')

    # Top clientes (análogo)
    if 'cod_cliente' in df_completo.columns:
        grupo = ['cod_cliente']
        for col in ['nome_cliente', 'cidade', 'uf']:
            if col in df_completo.columns:
                grupo.append(col)
        agg = {}
        if 'cod_Venda' in df_completo.columns:
            agg['cod_Venda'] = 'count'
        if 'quantidade' in df_completo.columns:
            agg['quantidade'] = 'sum'
        if 'Valor_Final' in df_completo.columns:
            agg['Valor_Final'] = 'sum'
        if agg:
            df_cli = df_completo.groupby(grupo).agg(agg).reset_index()
            rename = {}
            if 'cod_Venda' in agg:
                rename['cod_Venda'] = 'qtd_compras'
            if 'quantidade' in agg:
                rename['quantidade'] = 'qtd_itens'
            if 'Valor_Final' in agg:
                rename['Valor_Final'] = 'gasto_total'
            df_cli.rename(columns=rename, inplace=True)
            if 'gasto_total' in df_cli and 'qtd_compras' in df_cli:
                df_cli['ticket_medio_cliente'] = (df_cli['gasto_total'] / df_cli['qtd_compras']).round(2)
            indicadores['por_cliente'] = df_cli.sort_values('gasto_total', ascending=False).head(20).to_dict('records')

    # Lojas
    if 'cod_loja' in df_completo.columns:
        grupo = ['cod_loja']
        if 'descricao' in df_completo.columns:
            grupo.append('descricao')
        agg = {}
        if 'cod_Venda' in df_completo.columns:
            agg['cod_Venda'] = 'count'
        if 'quantidade' in df_completo.columns:
            agg['quantidade'] = 'sum'
        if 'Valor_Final' in df_completo.columns:
            agg['Valor_Final'] = 'sum'
        if agg:
            df_loja = df_completo.groupby(grupo).agg(agg).reset_index()
            rename = {}
            if 'cod_Venda' in agg:
                rename['cod_Venda'] = 'qtd_vendas'
            if 'quantidade' in agg:
                rename['quantidade'] = 'qtd_produtos'
            if 'Valor_Final' in agg:
                rename['Valor_Final'] = 'faturamento'
            df_loja.rename(columns=rename, inplace=True)
            indicadores['por_loja'] = df_loja.sort_values('faturamento', ascending=False).to_dict('records')

    # Séries temporais
    if 'Data' in df_completo.columns and pd.api.types.is_datetime64_any_dtype(df_completo['Data']):
        diario = df_completo.groupby(df_completo['Data'].dt.date).agg(
            vendas=('cod_Venda', 'count'),
            faturamento=('Valor_Final', 'sum')
        ).reset_index()
        diario['Data'] = pd.to_datetime(diario['Data'])
        indicadores['series_temporais']['diario'] = diario.to_dict('records')

        if 'mes_ano' in df_completo.columns:
            mensal = df_completo.groupby('mes_ano').agg(
                vendas=('cod_Venda', 'count'),
                faturamento=('Valor_Final', 'sum')
            ).reset_index()
            indicadores['series_temporais']['mensal'] = mensal.to_dict('records')

    return indicadores