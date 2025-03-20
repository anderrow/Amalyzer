// Intro
setTimeout(() => {
    const intro = document.getElementById("intro");

    // Aplica el efecto de desvanecimiento
    intro.style.opacity = "0";
    intro.style.visibility = "hidden"; // Esto lo oculta completamente después de la transición

    // Espera la duración de la animación antes de redirigir
    setTimeout(() => {
        window.location.href = "./pages/proportionings.html"; // Redirección
    }, 1000); // Espera 1s para la animación antes de redirigir
}, 3000); // Duración de la intro (3s antes de iniciar el fade-out)


// End of Intro

document.addEventListener("DOMContentLoaded", function () {
    fetchProportioningData();
});

function fetchProportioningData() {
    fetch("http://localhost:5000/api/proportionings") // Ajusta la URL de tu backend
        .then(response => response.json())
        .then(data => populateTable(data))
        .catch(error => console.error("Error fetching data:", error));
}

function populateTable(data) {
    const tableBody = document.querySelector("#ProportioningTable tbody");
    tableBody.innerHTML = ""; // Limpiar la tabla antes de llenarla

    data.forEach(row => {
        const tr = document.createElement("tr");

        Object.values(row).forEach(value => {
            const td = document.createElement("td");
            td.textContent = value;
            tr.appendChild(td);
        });

        tableBody.appendChild(tr);
    });
}

fetch("http://127.0.0.1:5000/api/proportionings")
