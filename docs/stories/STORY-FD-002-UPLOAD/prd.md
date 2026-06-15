# PRD: Suporte a Upload de Arquivos no Painel de Vendas (Cloud-Ready)

## 1. Contexto e Motivação
A FD Consultoria de Dados planeja implantar a aplicação de análise de vendas na nuvem (Streamlit Community Cloud). 
No ambiente de nuvem, o aplicativo não tem acesso à estrutura de pastas locais do usuário (como `D:\AMOSTRAS_TESTES\ENGENHARIA_IA`). Para que a aplicação possa ser utilizada de maneira pública ou compartilhada via link, o usuário deve ser capaz de enviar os arquivos necessários diretamente através do navegador de maneira intuitiva e segura.

---

## 2. Requisitos Funcionais

### RF1: Seleção de Origem dos Dados
* **Descrição**: A barra lateral deve permitir ao usuário escolher de onde carregar os dados.
* **Comportamento**: 
  - Uma opção do tipo Radio Button para alternar entre "📁 Diretório Local" (para desenvolvimento local rápido) e "☁️ Upload de Arquivos" (para produção na nuvem).

### RF2: Upload de Arquivos Múltiplos
* **Descrição**: Apresentar um componente de upload (`st.file_uploader`) quando a opção "☁️ Upload de Arquivos" estiver selecionada.
* **Comportamento**:
  - Aceitar apenas arquivos do tipo `.csv`.
  - Permitir a seleção e envio de múltiplos arquivos de uma só vez.

### RF3: Mapeamento Inteligente
* **Descrição**: O sistema deve associar automaticamente cada arquivo enviado ao seu respectivo papel (Produtos, Clientes, Lojas ou Vendas) com base no nome do arquivo (case-insensitive).
* **Comportamento**:
  - Procurar substrings como `"produto"`, `"cliente"`, `"loja"`, `"venda"`.
  - Exibir avisos e mensagens claras se faltar algum dos 4 arquivos necessários.

---

## 3. Requisitos Não Funcionais
* **Compatibilidade**: A leitura dos arquivos na memória não deve alterar o comportamento dos módulos de limpeza, validação ou modelagem dimensional.
* **Robustez**: Adicionar lógica de segurança (`seek(0)`) para lidar com streams de arquivos na tentativa de detecção de separador e encoding.
