from groq import Groq

def gerar_resumo_para_llm(indicadores, pergunta_usuario):
    """Constrói um resumo estruturado dos indicadores e da pergunta."""
    resumo = f"""# ANÁLISE DE VENDAS - FD CONSULTORIA

## 1. VISÃO GERAL DOS DADOS
- **Vendas:** {indicadores['visao_geral'].get('total_vendas', 0):,}
- **Produtos vendidos:** {indicadores['visao_geral'].get('total_produtos_vendidos', 0):,} unidades
- **Faturamento total:** R$ {indicadores['visao_geral'].get('faturamento_total', 0):,.2f}
- **Ticket médio:** R$ {indicadores['visao_geral'].get('ticket_medio', 0):,.2f}
- **Quantidade média por venda:** {indicadores['visao_geral'].get('quantidade_media_por_venda', 0):.1f}
"""
    if 'lucro_total' in indicadores['visao_geral']:
        resumo += f"- **Lucro total:** R$ {indicadores['visao_geral']['lucro_total']:,.2f}\n"
        resumo += f"- **Margem média:** {indicadores['visao_geral'].get('margem_media', 0):.1f}%\n"

    # Top 5 produtos
    if indicadores['por_produto']:
        resumo += "\n## 2. TOP 5 PRODUTOS (por faturamento)\n"
        for i, p in enumerate(indicadores['por_produto'][:5], 1):
            nome = f"{p.get('marca', '')} {p.get('tipo', '')}".strip()
            resumo += f"{i}. {nome or p['cod_produto']} - R$ {p.get('faturamento', 0):,.2f} ({p.get('qtd_unidades', 0)} unid.)\n"

    # Top 5 clientes
    if indicadores['por_cliente']:
        resumo += "\n## 3. TOP 5 CLIENTES\n"
        for i, c in enumerate(indicadores['por_cliente'][:5], 1):
            nome = c.get('nome_cliente', f"Cliente {c.get('cod_cliente', '')}")
            resumo += f"{i}. {nome} - R$ {c.get('gasto_total', 0):,.2f} ({c.get('qtd_compras', 0)} compras)\n"

    # Lojas
    if indicadores['por_loja']:
        resumo += "\n## 4. DESEMPENHO POR LOJA\n"
        for l in indicadores['por_loja']:
            desc = l.get('descricao', f"Loja {l.get('cod_loja', '')}")
            resumo += f"- {desc}: R$ {l.get('faturamento', 0):,.2f} ({l.get('qtd_vendas', 0)} vendas)\n"

    # Evolução mensal
    if indicadores['series_temporais'].get('mensal'):
        resumo += "\n## 5. EVOLUÇÃO MENSAL\n"
        for m in indicadores['series_temporais']['mensal']:
            resumo += f"- {m.get('mes_ano', 'N/A')}: R$ {m.get('faturamento', 0):,.2f} ({m.get('vendas', 0)} vendas)\n"

    resumo += f"\n## 6. PERGUNTA DO USUÁRIO\n{pergunta_usuario}\n"
    resumo += """
## 7. INSTRUÇÕES
Responda de forma clara e objetiva, use números exatos dos dados fornecidos, destaque insights relevantes.
"""
    return resumo

def consultar_llm(api_key, pergunta, indicadores):
    """Envia o resumo para a Groq e retorna a resposta."""
    client = Groq(api_key=api_key)
    resumo = gerar_resumo_para_llm(indicadores, pergunta)
    messages = [
        {"role": "system", "content": "Você é a FD Consultoria de Dados, especialista em análise de vendas. Responda apenas com base nos dados fornecidos. CRÍTICO: Se a pergunta do usuário for sobre um assunto fora do contexto das vendas, da empresa ou dos dados fornecidos (como curiosidades gerais, receitas, programação, piadas, etc.), NÃO apresente qualquer conselho, insight ou resposta genérica. Apenas informe ao usuário que a pergunta está fora do contexto dos dados analisados."},
        {"role": "user", "content": resumo}
    ]
    resposta = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=2048,
    )
    return resposta.choices[0].message.content