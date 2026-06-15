import os

# Constantes
ARQUIVOS_NECESSARIOS = {
    'produtos': 'Produtos.csv',
    'clientes': 'clientes.csv',
    'lojas': 'Loja.csv',
    'vendas': 'Vendas.csv'
}

COLUNAS_CHAVE = {
    'produtos': 'cod_produto',
    'clientes': 'cod_cliente',
    'lojas': 'cod_loja',
    'vendas': ['cod_produto', 'cod_cliente', 'cod_loja']
}

PATH_PADRAO = r"D:\AMOSTRAS_TESTES\ENGENHARIA_IA"

SEPARADORES = [';', ',', '\t']
ENCODINGS = ['utf-8', 'latin1', 'cp1252']

FORMATOS_DATA = [
    '%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y',
    '%Y%m%d', '%d-%m-%Y', '%d.%m.%Y'
]

MODELO_LLM = "llama-3.3-70b-versatile"
TEMPERATURA_LLM = 0.2
MAX_TOKENS_LLM = 2048