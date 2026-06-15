import pandas as pd
import re
from config import FORMATOS_DATA

def limpar_valor_numerico(valor):
    """Converte string com formato brasileiro para float."""
    if pd.isna(valor) or valor is None or valor == '':
        return None
    try:
        if isinstance(valor, (int, float)):
            return float(valor)
        str_valor = str(valor).strip()
        if not str_valor:
            return None
        # Remove caracteres não numéricos exceto vírgula, ponto e sinal
        str_valor = re.sub(r'[^\d,\-\.]', '', str_valor)
        str_valor = str_valor.replace(',', '.')
        # Corrige múltiplos pontos
        partes = str_valor.split('.')
        if len(partes) > 2:
            str_valor = ''.join(partes[:-1]) + '.' + partes[-1]
        return float(str_valor) if str_valor and str_valor != '.' else None
    except:
        return None

def converter_para_datetime(serie):
    """Tenta converter uma série para datetime usando múltiplos formatos."""
    if serie.empty:
        return serie
    for formato in FORMATOS_DATA:
        try:
            return pd.to_datetime(serie, format=formato, errors='raise')
        except:
            continue
    try:
        return pd.to_datetime(serie, dayfirst=True, errors='coerce')
    except:
        return serie

def identificar_tipos_colunas(df):
    """Identifica automaticamente colunas numéricas, datas, ids, texto e categorias."""
    colunas_numericas = []
    colunas_datas = []
    colunas_texto = []
    colunas_id = []
    colunas_categoria = []

    for coluna in df.columns:
        nome_lower = str(coluna).lower()
        # IDs
        if any(p in nome_lower for p in ['cod_', 'id_', 'codigo']):
            colunas_id.append(coluna)
            continue
        # Datas pelo nome
        if any(p in nome_lower for p in ['data', 'date', 'dia']):
            amostra = df[coluna].dropna().head(10)
            if not amostra.empty:
                teste = converter_para_datetime(amostra)
                if teste.notna().any():
                    colunas_datas.append(coluna)
                    continue
        # Tipagem pandas
        if df[coluna].dtype in ['int64', 'float64']:
            colunas_numericas.append(coluna)
        elif df[coluna].dtype == 'datetime64[ns]':
            colunas_datas.append(coluna)
        elif df[coluna].dtype == 'object':
            amostra = df[coluna].dropna().head(100)
            if not amostra.empty:
                # Testa se é numérico
                conv = amostra.apply(limpar_valor_numerico)
                if conv.notna().sum() > len(amostra) * 0.8:
                    colunas_numericas.append(coluna)
                else:
                    # Testa se é data
                    teste_data = converter_para_datetime(amostra)
                    if teste_data.notna().sum() > len(amostra) * 0.8:
                        colunas_datas.append(coluna)
                    else:
                        if df[coluna].nunique() / len(df) < 0.1:
                            colunas_categoria.append(coluna)
                        else:
                            colunas_texto.append(coluna)
        else:
            colunas_texto.append(coluna)

    return {
        'numericas': list(set(colunas_numericas)),
        'datas': list(set(colunas_datas)),
        'texto': list(set(colunas_texto)),
        'ids': list(set(colunas_id)),
        'categorias': list(set(colunas_categoria))
    }

def limpar_dataframe(df, tipos_esperados=None):
    """Aplica limpeza com base nos tipos identificados."""
    df_limpo = df.copy()
    if tipos_esperados is None:
        tipos = identificar_tipos_colunas(df_limpo)
    else:
        tipos = tipos_esperados

    for col in tipos.get('numericas', []):
        if col in df_limpo.columns:
            df_limpo[col] = df_limpo[col].apply(limpar_valor_numerico)

    for col in tipos.get('datas', []):
        if col in df_limpo.columns:
            df_limpo[col] = converter_para_datetime(df_limpo[col])

    for col in tipos.get('texto', []) + tipos.get('categorias', []):
        if col in df_limpo.columns:
            df_limpo[col] = df_limpo[col].astype(str).str.strip()
            df_limpo[col] = df_limpo[col].replace(['nan', 'None', 'null', ''], None)

    for col in tipos.get('ids', []):
        if col in df_limpo.columns:
            df_limpo[col] = df_limpo[col].astype(str).str.strip()
            df_limpo[col] = df_limpo[col].replace(['nan', 'None', 'null', ''], None)

    return df_limpo, tipos