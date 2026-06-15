# STORY-FD-001-LOGO: Logotipo Corporativo na Interface do Usuário

## Descrição
Adicionar o logotipo institucional da FD Labs (`LOGO_FD.png`) à barra lateral do painel de Análise de Vendas.
Se a imagem não estiver disponível na pasta, a interface deve exibir um fallback elegante baseado em texto.

---

## Critérios de Aceitação (AC)

- **AC1: Renderização de Imagem**: Carregar e renderizar `LOGO_FD.png` no topo da barra lateral (`st.sidebar`).
- **AC2: Fallback Elegante**: Caso o arquivo `LOGO_FD.png` não exista no caminho esperado, a barra lateral deve continuar exibindo o título em texto "📊 FD Consultoria de Dados" sem gerar erros.
- **AC3: Responsividade**: O logotipo deve ajustar sua largura dinamicamente à largura da barra lateral.

---

## File List
- [MODIFY] [ui.py](file:///d:/FD_CONSULTORIA/DESENVOLVIMENTO/analise_vendas_spec/ui.py)
- [MODIFY] [SPEC.md](file:///d:/FD_CONSULTORIA/DESENVOLVIMENTO/analise_vendas_spec/SPEC.md)
