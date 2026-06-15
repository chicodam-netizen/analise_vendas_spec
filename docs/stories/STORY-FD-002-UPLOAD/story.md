# STORY-FD-002-UPLOAD: Upload de Arquivos via Interface Web

## Descrição
Adicionar suporte ao upload de múltiplos arquivos CSV diretamente pela barra lateral do Streamlit, permitindo a execução segura do aplicativo em servidores de nuvem.

---

## Critérios de Aceitação (AC)

- **AC1: Seleção de Entrada**: A barra lateral deve conter um seletor para alternar entre "Diretório Local" e "Upload de Arquivos".
- **AC2: Upload Múltiplo e Validação**: O componente de upload deve aceitar os arquivos `.csv` e o sistema deve avisar quais arquivos estão pendentes antes do processamento.
- **AC3: Mapeamento Automático**: O mapeamento dos arquivos enviados deve ser feito pelo nome (ex: `Vendas.csv` mapeado para a tabela de vendas), independentemente de maiúsculas/minúsculas.
- **AC4: Semântica de Leitura de Streams**: O leitor de dados deve conseguir tentar ler com múltiplos separadores e encodings sem corromper o buffer de arquivo na memória.

---

## File List
- [MODIFY] [SPEC.md](file:///d:/FD_CONSULTORIA/DESENVOLVIMENTO/analise_vendas_spec/SPEC.md)
- [MODIFY] [data_loader.py](file:///d:/FD_CONSULTORIA/DESENVOLVIMENTO/analise_vendas_spec/data_loader.py)
- [MODIFY] [ui.py](file:///d:/FD_CONSULTORIA/DESENVOLVIMENTO/analise_vendas_spec/ui.py)
- [MODIFY] [app.py](file:///d:/FD_CONSULTORIA/DESENVOLVIMENTO/analise_vendas_spec/app.py)
