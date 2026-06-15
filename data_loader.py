import pandas as pd
import os
from config import SEPARADORES, ENCODINGS, ARQUIVOS_NECESSARIOS  # <-- adicionado

def carregar_csv_com_separador(caminho_arquivo):
    """
    Tenta carregar um CSV usando diferentes separadores e encodings.
    Retorna (DataFrame, separador, encoding, mensagem).
    """
    for sep in SEPARADORES:
        for encoding in ENCODINGS:
            try:
                # Testa com 5 linhas para verificar se o separador é válido
                df_teste = pd.read_csv(caminho_arquivo, sep=sep, encoding=encoding, nrows=5)
                if len(df_teste.columns) > 1:
                    df = pd.read_csv(caminho_arquivo, sep=sep, encoding=encoding)
                    return df, sep, encoding, f"Sucesso: separador '{sep}', encoding {encoding}"
            except:
                continue
    # Última tentativa: deixa o pandas inferir
    try:
        df = pd.read_csv(caminho_arquivo, sep=None, engine='python', encoding='utf-8')
        return df, 'auto', 'utf-8', "Sucesso: separador auto-detectado"
    except Exception as e:
        return None, None, None, f"Erro ao ler arquivo: {str(e)}"

def carregar_todos_arquivos(caminho_base):
    """
    Carrega os quatro arquivos necessários a partir do diretório base.
    Retorna (dicionario_com_dfs, mensagem_consolidada).
    """
    arquivos = {}
    mensagens = []

    if not os.path.exists(caminho_base):
        return None, f"Diretório não encontrado: {caminho_base}"

    for tipo, nome_arquivo in ARQUIVOS_NECESSARIOS.items():
        caminho_completo = os.path.join(caminho_base, nome_arquivo)
        if not os.path.exists(caminho_completo):
            mensagens.append(f"❌ Arquivo não encontrado: {nome_arquivo}")
            continue

        df, sep, enc, msg = carregar_csv_com_separador(caminho_completo)
        if df is not None:
            arquivos[tipo] = {
                'df_original': df,
                'caminho': caminho_completo
            }
            mensagens.append(f"✅ {nome_arquivo}: {len(df)} linhas")
        else:
            mensagens.append(f"❌ {nome_arquivo}: {msg}")

    return arquivos if arquivos else None, "\n".join(mensagens)