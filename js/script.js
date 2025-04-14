// Intro
setTimeout(() => {
    const intro = document.getElementById("intro");

    if (intro) { // Only execute if Intro exits
        intro.style.opacity = "0";
        intro.style.visibility = "hidden";

        setTimeout(() => {
            window.location.href = "./pages/proportionings.html"; // Redirect
        }, 1000);
    } else {
        console.warn("No animation found, Intro not found ot doesn't exist");
    }
}, 3000);



// End of Intro

document.addEventListener("DOMContentLoaded", function () {
    fetchProportioningData();

    const updateButton = document.querySelector("#updateButton");
    if (updateButton) {
        updateButton.addEventListener("click", function () {
            console.log("Update Table Data...");
            fetchProportioningData(); // Reload Data without refreshing page 
        });
    }
});

function fetchProportioningData() {
    fetch("http://localhost:5000/api/proportionings") // Adjust the URL
        .then(response => response.json())
        .then(data => populateTable(data))
        .catch(error => console.error("Error fetching data:", error));
}

function populateTable(data) {
    const tableBody = document.querySelector("#ProportioningTable tbody"); //Where to fill the data (tbody with ID ProportioningTable)
    tableBody.innerHTML = ""; // Clean the table before Filling

    data.forEach(row => {
        const tr = document.createElement("tr");

        // Insert in the correct order
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

