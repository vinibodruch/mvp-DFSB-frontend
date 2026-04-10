const BASE_URL = "http://127.0.0.1:8080";

document.getElementById("apiDocsLink").href = `${BASE_URL}/openapi/swagger`;

// ================================
// Verificação de saúde da API
// ================================

const checkHealth = async () => {
  const badge = document.getElementById("statusIndicator");
  try {
    const response = await fetch(`${BASE_URL}/health`);
    if (response.ok) {
      badge.textContent = "API online";
      badge.className = "status-badge status-online";
    } else {
      throw new Error("status não ok");
    }
  } catch {
    badge.textContent = "API offline";
    badge.className = "status-badge status-offline";
    alert("Backend não está rodando. Inicie o servidor em http://127.0.0.1:8080 e recarregue a página.");
  }
};

// ================================
// Buscar e exibir tarefas
// ================================

const loadTasks = async () => {
  try {
    const response = await fetch(`${BASE_URL}/tasks/`);
    const data = await response.json();
    renderTasks(data.tasks);
  } catch (error) {
    console.error("Erro ao buscar tarefas:", error);
  }
};

const renderTasks = (tasks) => {
  const list = document.getElementById("taskList");
  const emptyMessage = document.getElementById("emptyMessage");

  list.innerHTML = "";

  if (tasks.length === 0) {
    emptyMessage.hidden = false;
    return;
  }

  emptyMessage.hidden = true;

  tasks.forEach((task) => {
    list.appendChild(createTaskItem(task));
  });
};

const createTaskItem = (task) => {
  const li = document.createElement("li");
  li.className = `task-item${task.completed ? " completed" : ""}`;
  li.dataset.id = task.id;

  // Conteúdo textual
  const content = document.createElement("div");
  content.className = "task-content";

  const title = document.createElement("span");
  title.className = "task-title";
  title.textContent = task.title;

  content.appendChild(title);

  if (task.description) {
    const desc = document.createElement("span");
    desc.className = "task-description";
    desc.textContent = task.description;
    content.appendChild(desc);
  }

  // Ações (checkbox de conclusão + botão excluir)
  const actions = document.createElement("div");
  actions.className = "task-actions";

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = task.completed;
  checkbox.title = task.completed ? "Marcar como pendente" : "Marcar como concluída";
  checkbox.addEventListener("change", () => toggleComplete(task.id, checkbox.checked));

  const deleteBtn = document.createElement("button");
  deleteBtn.className = "btn-icon";
  deleteBtn.title = "Excluir tarefa";
  deleteBtn.textContent = "✕";
  deleteBtn.addEventListener("click", () => openDeleteModal(task.id));

  const editBtn = document.createElement("button");
  editBtn.className = "btn-icon";
  editBtn.title = "Editar tarefa";
  editBtn.textContent = "✎";
  editBtn.addEventListener("click", () => openEditModal(task));

  const infoBtn = document.createElement("button");
  infoBtn.className = "btn-icon btn-info";
  infoBtn.textContent = "ℹ";
  infoBtn.setAttribute("aria-label", "Informações da tarefa");

  const tooltip = document.createElement("div");
  tooltip.className = "info-tooltip";
  const fmt = (iso) => new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
  tooltip.innerHTML = `<span>Criado: ${fmt(task.created_at)}</span><span>Atualizado: ${fmt(task.updated_at)}</span>`;
  infoBtn.appendChild(tooltip);

  actions.appendChild(checkbox);
  actions.appendChild(infoBtn);
  actions.appendChild(editBtn);
  actions.appendChild(deleteBtn);

  li.appendChild(content);
  li.appendChild(actions);

  return li;
};

// ================================
// Criar tarefa
// ================================

const createTask = async (title, description) => {
  const body = { title };
  if (description) body.description = description;

  const response = await fetch(`${BASE_URL}/tasks/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error("Falha ao criar tarefa");
  }

  return response.json();
};

// ================================
// Alternar conclusão da tarefa
// ================================

const toggleComplete = async (taskId, completed) => {
  try {
    const response = await fetch(`${BASE_URL}/tasks/${taskId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed }),
    });

    if (!response.ok) throw new Error("Falha ao atualizar tarefa");

    // Atualiza o estilo do item sem recarregar toda a lista
    const item = document.querySelector(`.task-item[data-id="${taskId}"]`);
    if (item) {
      item.classList.toggle("completed", completed);
      const checkbox = item.querySelector("input[type=checkbox]");
      if (checkbox) {
        checkbox.title = completed ? "Marcar como pendente" : "Marcar como concluída";
      }
    }
  } catch (error) {
    console.error("Erro ao atualizar tarefa:", error);
    // Reverte o checkbox em caso de erro
    await loadTasks();
  }
};

// ================================
// Editar tarefa (com modal)
// ================================

let pendingEditId = null;

const openEditModal = async (task) => {
  pendingEditId = task.id;

  // Busca os dados mais recentes da tarefa antes de abrir o modal
  try {
    const response = await fetch(`${BASE_URL}/tasks/${task.id}`);
    if (response.ok) {
      const fresh = await response.json();
      document.getElementById("editTitle").value = fresh.title;
      document.getElementById("editDescription").value = fresh.description || "";
    } else {
      document.getElementById("editTitle").value = task.title;
      document.getElementById("editDescription").value = task.description || "";
    }
  } catch {
    document.getElementById("editTitle").value = task.title;
    document.getElementById("editDescription").value = task.description || "";
  }

  document.getElementById("editModal").hidden = false;
};

const closeEditModal = () => {
  pendingEditId = null;
  document.getElementById("editModal").hidden = true;
};

const updateTask = async (taskId, title, description) => {
  const body = { title };
  body.description = description || null;

  const response = await fetch(`${BASE_URL}/tasks/${taskId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) throw new Error("Falha ao atualizar tarefa");
  return response.json();
};

// ================================
// Excluir tarefa (com modal)
// ================================

let pendingDeleteId = null;

const openDeleteModal = (taskId) => {
  pendingDeleteId = taskId;
  document.getElementById("deleteModal").hidden = false;
};

const closeDeleteModal = () => {
  pendingDeleteId = null;
  document.getElementById("deleteModal").hidden = true;
};

const confirmDeleteTask = async () => {
  if (pendingDeleteId === null) return;

  try {
    const response = await fetch(`${BASE_URL}/tasks/${pendingDeleteId}`, {
      method: "DELETE",
    });

    if (!response.ok && response.status !== 204) {
      throw new Error("Falha ao excluir tarefa");
    }

    // Remove o item da lista sem recarregar tudo
    const item = document.querySelector(`.task-item[data-id="${pendingDeleteId}"]`);
    if (item) item.remove();

    // Mostra mensagem vazia se não sobrar nenhuma tarefa
    const list = document.getElementById("taskList");
    if (list.children.length === 0) {
      document.getElementById("emptyMessage").hidden = false;
    }
  } catch (error) {
    console.error("Erro ao excluir tarefa:", error);
  } finally {
    closeDeleteModal();
  }
};

// ================================
// Inicialização e eventos
// ================================

document.addEventListener("DOMContentLoaded", () => {
  // Verifica a API e carrega as tarefas ao abrir a página
  checkHealth();
  loadTasks();

  // Envio do formulário de criação
  const form = document.getElementById("createForm");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const titleInput = document.getElementById("inputTitle");
    const descriptionInput = document.getElementById("inputDescription");
    const submitBtn = form.querySelector("button[type=submit]");

    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();

    if (!title) return;

    submitBtn.disabled = true;

    try {
      const task = await createTask(title, description);

      // Adiciona a nova tarefa ao topo da lista
      const list = document.getElementById("taskList");
      document.getElementById("emptyMessage").hidden = true;
      list.prepend(createTaskItem(task));

      // Limpa o formulário
      titleInput.value = "";
      descriptionInput.value = "";
    } catch (error) {
      console.error("Erro ao criar tarefa:", error);
    } finally {
      submitBtn.disabled = false;
    }
  });

  // Botões do modal de exclusão
  document.getElementById("confirmDelete").addEventListener("click", confirmDeleteTask);
  document.getElementById("cancelDelete").addEventListener("click", closeDeleteModal);

  // Fecha o modal de exclusão ao clicar fora dele
  document.getElementById("deleteModal").addEventListener("click", (event) => {
    if (event.target === event.currentTarget) closeDeleteModal();
  });

  // Formulário do modal de edição
  document.getElementById("editForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (pendingEditId === null) return;

    const title = document.getElementById("editTitle").value.trim();
    const description = document.getElementById("editDescription").value.trim();
    const submitBtn = event.target.querySelector("button[type=submit]");

    if (!title) return;

    submitBtn.disabled = true;
    try {
      const updated = await updateTask(pendingEditId, title, description);
      const item = document.querySelector(`.task-item[data-id="${pendingEditId}"]`);
      if (item) {
        item.querySelector(".task-title").textContent = updated.title;
        const descEl = item.querySelector(".task-description");
        if (updated.description) {
          if (descEl) {
            descEl.textContent = updated.description;
          } else {
            const newDesc = document.createElement("span");
            newDesc.className = "task-description";
            newDesc.textContent = updated.description;
            item.querySelector(".task-content").appendChild(newDesc);
          }
        } else if (descEl) {
          descEl.remove();
        }
      }
      closeEditModal();
    } catch (error) {
      console.error("Erro ao editar tarefa:", error);
    } finally {
      submitBtn.disabled = false;
    }
  });

  document.getElementById("cancelEdit").addEventListener("click", closeEditModal);

  // Fecha o modal de edição ao clicar fora dele
  document.getElementById("editModal").addEventListener("click", (event) => {
    if (event.target === event.currentTarget) closeEditModal();
  });
});
