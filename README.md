# Do It — Frontend

Uma **Single Page Application** de lista de tarefas feita com HTML, CSS e JavaScript puro (sem frameworks). Consome a [API do backend](../mvp-DFSB-backend/README.md).

---

## Descrição

O **Do It** permite criar, visualizar, concluir e excluir tarefas por meio de uma interface simples com tema escuro. Toda a comunicação com o servidor é feita via HTTP usando a Fetch API, sem nenhuma dependência externa ou etapa de build.

---

## Funcionalidades

- Verificação automática de saúde da API ao carregar a página
- Listagem de todas as tarefas cadastradas
- Criação de tarefa com título e descrição opcional
- Marcar tarefa como concluída (exibe em verde com tachado)
- Excluir tarefa com modal de confirmação
- Layout responsivo com tema escuro

---

## Estrutura do projeto

```text
mvp-DFSB-frontend/
├── index.html    # Estrutura da página
├── styles.css    # Estilos com tema escuro (sem dependências externas)
└── scripts.js    # Toda a lógica de comunicação com a API e manipulação do DOM
```

---

## Requisitos

- Navegador moderno (Chrome, Firefox, Edge, Safari — versões a partir de 2022)
- O **backend** rodando em `http://127.0.0.1:8080`
- Nenhuma ferramenta de build, servidor local ou extensão necessária

---

## Rodando o backend

```bash
# A partir da pasta mvp-DFSB-backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

A API estará disponível em `http://127.0.0.1:8080`.  
Documentação Swagger: `http://127.0.0.1:8080/openapi`

OBS.: Executando na porta **8080** pois a porta **5000** local pode estar em uso.

---

## Abrindo o frontend

Basta abrir o arquivo `index.html` no navegador:

```bash
# macOS
open index.html

# Linux
xdg-open index.html

# Windows
start index.html
```

Ou arraste o arquivo para qualquer janela do navegador — **sem necessidade de servidor**.

---

## Rotas da API utilizadas

| Método   | Rota          | Finalidade                          |
| -------- | ------------- | ----------------------------------- |
| `GET`    | `/health`     | Verificar se a API está no ar       |
| `GET`    | `/tasks/`     | Carregar todas as tarefas           |
| `POST`   | `/tasks/`     | Criar uma nova tarefa               |
| `PATCH`  | `/tasks/:id`  | Atualizar o status de conclusão     |
| `DELETE` | `/tasks/:id`  | Excluir uma tarefa                  |

---

## Tecnologias

- **HTML5** — marcação semântica
- **CSS3** — variáveis CSS, Flexbox, tema escuro
- **JavaScript** — Fetch API, manipulação de DOM, eventos
