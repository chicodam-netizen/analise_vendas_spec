import pytest
import pandas as pd
import os
import io
from data_loader import carregar_csv_com_separador, carregar_todos_arquivos, carregar_arquivos_upload

def test_carregar_csv_com_separador_valid(tmp_path):
    # Test loading a valid CSV with semi-colon and latin1 encoding
    file_path = tmp_path / "test.csv"
    data = "cod_produto;nome\n1;Produto Ação\n2;Produto B"
    file_path.write_bytes(data.encode('latin1'))

    df, sep, enc, msg = carregar_csv_com_separador(str(file_path))
    assert df is not None
    assert sep == ';'
    assert enc == 'latin1'
    assert len(df) == 2
    assert list(df.columns) == ['cod_produto', 'nome']

def test_carregar_csv_com_separador_comma(tmp_path):
    # Test loading a valid CSV with comma separator and utf-8 encoding
    file_path = tmp_path / "test_comma.csv"
    data = "cod_produto,nome\n1,Produto A\n2,Produto B"
    file_path.write_bytes(data.encode('utf-8'))

    df, sep, enc, msg = carregar_csv_com_separador(str(file_path))
    assert df is not None
    assert sep == ','
    assert enc == 'utf-8'

def test_carregar_csv_com_separador_invalid():
    # Test loading a non-existent file
    df, sep, enc, msg = carregar_csv_com_separador("non_existent_file.csv")
    assert df is None
    assert sep is None
    assert enc is None
    assert "Erro ao ler arquivo" in msg

def test_carregar_csv_com_separador_file_like():
    # Test loading with an in-memory file object (StringIO)
    data = "cod_produto,nome\n1,Produto A\n2,Produto B"
    file_like = io.StringIO(data)
    df, sep, enc, msg = carregar_csv_com_separador(file_like)
    assert df is not None
    assert sep == ','
    assert len(df) == 2

def test_carregar_todos_arquivos(tmp_path):
    # Setup temporary directory with the 4 required CSV files
    data_prod = "cod_produto;nome\n1;Produto A\n2;Produto B"
    data_cli = "cod_cliente;nome\n101;Cliente A\n102;Cliente B"
    data_loja = "cod_loja;nome\n10;Loja A"
    data_venda = "cod_venda;cod_produto;cod_cliente;cod_loja;quantidade;Valor_Final;Data\n1;1;101;10;2;100.0;2026-06-22"

    (tmp_path / "Produtos.csv").write_bytes(data_prod.encode('utf-8'))
    (tmp_path / "clientes.csv").write_bytes(data_cli.encode('utf-8'))
    (tmp_path / "Loja.csv").write_bytes(data_loja.encode('utf-8'))
    (tmp_path / "Vendas.csv").write_bytes(data_venda.encode('utf-8'))

    arquivos, msg = carregar_todos_arquivos(str(tmp_path))
    assert arquivos is not None
    assert len(arquivos) == 4
    assert 'produtos' in arquivos
    assert 'clientes' in arquivos
    assert 'lojas' in arquivos
    assert 'vendas' in arquivos
    assert "✅" in msg

def test_carregar_todos_arquivos_missing_directory():
    arquivos, msg = carregar_todos_arquivos("non_existent_directory_12345")
    assert arquivos is None
    assert "Diretório não encontrado" in msg

def test_carregar_todos_arquivos_missing_file(tmp_path):
    # Setup only 3 of the 4 required files
    (tmp_path / "Produtos.csv").write_bytes(b"cod_produto;nome\n1;Produto A")
    (tmp_path / "clientes.csv").write_bytes(b"cod_cliente;nome\n101;Cliente A")
    (tmp_path / "Loja.csv").write_bytes(b"cod_loja;nome\n10;Loja A")
    # Vendas.csv is missing

    arquivos, msg = carregar_todos_arquivos(str(tmp_path))
    assert arquivos is None
    assert "❌ Arquivo não encontrado: Vendas.csv" in msg

def test_carregar_arquivos_upload():
    # Setup mock file-like upload objects
    class MockUploadedFile(io.StringIO):
        def __init__(self, name, content):
            super().__init__(content)
            self.name = name

    mapeamento = {
        'produtos': MockUploadedFile("Produtos.csv", "cod_produto;nome\n1;Produto A"),
        'clientes': MockUploadedFile("clientes.csv", "cod_cliente;nome\n101;Cliente A"),
        'lojas': MockUploadedFile("Loja.csv", "cod_loja;nome\n10;Loja A"),
        'vendas': MockUploadedFile("Vendas.csv", "cod_venda;cod_produto;cod_cliente;cod_loja;quantidade;Valor_Final;Data\n1;1;101;10;2;100.0;2026-06-22")
    }

    arquivos, msg = carregar_arquivos_upload(mapeamento)
    assert arquivos is not None
    assert len(arquivos) == 4
    assert "✅" in msg
