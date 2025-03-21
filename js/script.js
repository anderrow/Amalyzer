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

        // Insertar las celdas en el orden correcto
        tr.innerHTML = `
            <td>${row.ProportioningDBID}</td>
            <td>${row.ArticleDBID}</td>
            <td>${row.LotDBID}</td>
            <td>${row.VMSscan}</td>
            <td>${row.ArticleID}</td>
            <td>${row.ArticleName}</td>
            <td>${row.LotID}</td>
            <td>${row.Requested}</td>
            <td>${row.Actual}</td>
            <td>${row.StartTime}</td>
            <td>${row.EndTime}</td>
            <td>${row.MixBoxID}</td>
            <td>${row.IngBoxID}</td>
            <td>${row.DosingLocation}</td>
            <td>${row.TypeOfDosing}</td>
        `;

        tableBody.appendChild(tr);
    });
}


fetch("http://127.0.0.1:5000/api/proportionings")
