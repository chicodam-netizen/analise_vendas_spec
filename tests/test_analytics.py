import pytest
import pandas as pd
from analytics import gerar_indicadores

def test_gerar_indicadores_empty():
    res = gerar_indicadores(None)
    assert res['visao_geral'] == {}
    assert res['por_produto'] == []
    assert res['por_cliente'] == []
    assert res['por_loja'] == []
    assert res['series_temporais'] == {}

    res_empty = gerar_indicadores(pd.DataFrame())
    assert res_empty['visao_geral'] == {}

def test_gerar_indicadores_success():
    # Setup a mock df_completo
    df = pd.DataFrame({
        'cod_Venda': ['V1', 'V2', 'V3'],
        'cod_produto': ['P1', 'P2', 'P1'],
        'marca': ['Marca X', 'Marca Y', 'Marca X'],
        'quantidade': [2, 1, 3],
        'Valor_Final': [100.0, 50.0, 150.0],
        'lucro_total': [40.0, 10.0, 60.0],
        'margem_percentual': [40.0, 20.0, 40.0],
        'cod_cliente': ['C1', 'C2', 'C1'],
        'nome_cliente': ['Cliente A', 'Cliente B', 'Cliente A'],
        'cod_loja': ['L1', 'L1', 'L2'],
        'descricao': ['Loja Centro', 'Loja Centro', 'Loja Sul'],
        'Data': pd.to_datetime(['2026-06-22', '2026-06-22', '2026-06-23']),
        'mes_ano': ['2026-06', '2026-06', '2026-06']
    })

    indicadores = gerar_indicadores(df)

    # 1. Visão geral
    v_geral = indicadores['visao_geral']
    assert v_geral['total_vendas'] == 3
    assert v_geral['total_produtos_vendidos'] == 6
    assert v_geral['faturamento_total'] == 300.0
    assert v_geral['ticket_medio'] == 100.0
    assert v_geral['quantidade_media_por_venda'] == 2.0
    assert v_geral['lucro_total'] == 110.0
    assert v_geral['margem_media'] == pytest.approx(33.33, 0.01)

    # 2. Por produto (ordenado por faturamento desc)
    p_prod = indicadores['por_produto']
    # P1 has 2 sales, 5 units, 250 faturamento, 100 profit
    # P2 has 1 sale, 1 unit, 50 faturamento, 10 profit
    assert len(p_prod) == 2
    assert p_prod[0]['cod_produto'] == 'P1'
    assert p_prod[0]['faturamento'] == 250.0
    assert p_prod[0]['qtd_unidades'] == 5
    assert p_prod[0]['qtd_vendas'] == 2
    assert p_prod[0]['margem_media'] == 40.0
    
    assert p_prod[1]['cod_produto'] == 'P2'
    assert p_prod[1]['faturamento'] == 50.0

    # 3. Por cliente (ordenado por gasto total desc)
    p_cli = indicadores['por_cliente']
    # C1 has 2 compras, 5 items, 250 gasto_total
    # C2 has 1 compra, 1 item, 50 gasto_total
    assert len(p_cli) == 2
    assert p_cli[0]['cod_cliente'] == 'C1'
    assert p_cli[0]['gasto_total'] == 250.0
    assert p_cli[0]['ticket_medio_cliente'] == 125.0

    # 4. Por loja (ordenado por faturamento desc)
    p_loja = indicadores['por_loja']
    # L1: V1 + V2 -> faturamento 150.0
    # L2: V3 -> faturamento 150.0
    assert len(p_loja) == 2
    assert p_loja[0]['faturamento'] == 150.0

    # 5. Séries temporais
    series = indicadores['series_temporais']
    assert 'diario' in series
    assert 'mensal' in series
    
    # 2026-06-22 should have faturamento 150.0 (V1=100, V2=50)
    # 2026-06-23 should have faturamento 150.0 (V3=150)
    diario = series['diario']
    assert len(diario) == 2
    assert diario[0]['faturamento'] == 150.0
    assert diario[1]['faturamento'] == 150.0

    mensal = series['mensal']
    assert len(mensal) == 1
    assert mensal[0]['mes_ano'] == '2026-06'
    assert mensal[0]['faturamento'] == 300.0
