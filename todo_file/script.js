document.addEventListener("DOMContentLoaded", function() {
    const addButton = document.getElementById("add-task");
    const taskInput = document.getElementById("new-task");
    const taskList = document.getElementById("task-list");

    addButton.addEventListener("click", addTask);

    function addTask() {
        const taskValue = taskInput.value.trim();
        if (taskValue) {
            const listItem = document.createElement("li");
            listItem.textContent = taskValue;

            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Delete";
            deleteButton.className = "delete-task";
            deleteButton.addEventListener("click", function() {
                taskList.removeChild(listItem);
            });

            listItem.appendChild(deleteButton);
            taskList.appendChild(listItem);

            taskInput.value = "";
        }
    }
});
