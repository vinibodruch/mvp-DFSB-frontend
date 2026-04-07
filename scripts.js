const BASE_URL = "http://localhost:8080";

const getTasks = async () => {
  let url = BASE_URL + "/tasks/";
  fetch(url, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((data) => {
      data.tasks.forEach((task) => {
        insertList(task);
      });
    })
    .catch((error) => console.error("Error fetching tasks:", error));
};

const insertList = (task) => {
  const tableBody = document.getElementById('tableBody');
  const row = tableBody.insertRow();

  const properties = [
    task.id,
    task.title,
    task.description || "-",
    task.completed ? "Sim" : "Não",
    new Date(task.created_at).toLocaleString("pt-BR"),
    new Date(task.updated_at).toLocaleString("pt-BR")
  ];

  properties.forEach((value, index) => {
    const cell = row.insertCell();
    cell.textContent = value;

    // Color the "Concluída" cell (index 3)
    if (index === 3) {
      cell.style.color = value === "Sim"
        ? "var(--color-success)"
        : "var(--color-text-muted)";
    }
  });

};

document.addEventListener('DOMContentLoaded', getTasks);