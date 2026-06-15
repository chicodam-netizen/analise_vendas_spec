# PRD: Exibição do Logotipo FD Labs no Painel de Vendas

## 1. Contexto e Motivação
A FD Consultoria de Dados necessita personalizar o painel de análise de vendas com o logotipo institucional (`LOGO_FD.png`).
Essa personalização promove a identidade de marca interna e melhora a experiência visual do usuário final ao interagir com o dashboard.

---

## 2. Requisitos Funcionais

### RF1: Exibição da Logotipo na Barra Lateral
* **Descrição**: A barra lateral (`st.sidebar`) deve exibir a imagem `LOGO_FD.png` no topo.
* **Comportamento**: 
  - Se a imagem `LOGO_FD.png` estiver presente na raiz, ela será exibida com largura ajustada automaticamente ao contêiner da barra lateral.
  - Se o arquivo de imagem não estiver presente, a aplicação deve exibir de forma elegante o título em formato de texto (`📊 FD Consultoria de Dados`) como fallback, evitando falhas ou exceções.

---

## 3. Requisitos Não Funcionais
* **Robustez**: O sistema não deve quebrar caso o arquivo de imagem seja removido ou esteja corrompido (fallback gracioso).
* **Usabilidade**: A imagem deve ter tamanho proporcional e não distorcer o layout da barra lateral.
