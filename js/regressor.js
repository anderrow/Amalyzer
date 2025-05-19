
window.addEventListener("DOMContentLoaded", () => {
    // Fetch current Proportioning ID
    fetch("http://localhost:5000/common/PropId")
    .then(response => response.text())
    .then(data => {
        console.log("Fetched PropId:", data);
        const inputField = document.getElementById("ProportioningId");
        if (inputField) {
            inputField.value = data;
        }
    })
    .catch(error => console.error("Error fetching current propDbId:", error));

    // Fetch and inject Graph HTML
    fetch("http://localhost:5000/regressor/Graph", { })
    .then(res => res.text())
    .then(html => {
        const graphContainer = document.getElementById("regressor_graph_container");
        graphContainer.innerHTML = html;  // 1) insert raw HTML

        // 2) now find all <script> tags inside the graphContainer
        graphContainer.querySelectorAll("script").forEach(oldScript => {
            // Create a new identical <script>
            const newScript = document.createElement("script");
            if (oldScript.src) {
                newScript.src = oldScript.src;
            } else {
                newScript.textContent = oldScript.textContent;
            }
            // Add it to <head> (or body)
            document.head.appendChild(newScript);
            // Optionally remove the old one
            oldScript.remove();
        });
    })
    fetchSummaryData("http://localhost:5000/regressor/SummaryTable"); 
});

// Function to fetch proportioning data
function fetchSummaryData(link) {
    fetch(link) // Adjust the URL
        .then(response => response.json())
        .then(data => populateTable(data)) // Populate table with the fetched data
        .catch(error => console.error("Error fetching data:", error));
}

//Fuction to fill the table
function populateTable(data) {
    const table = document.getElementById("RegressorTable");

    // Clear any existing content
    table.innerHTML = "";

    // Handle empty or invalid data
    if (!Array.isArray(data) || data.length === 0) {
        table.innerHTML = "<tr><td>No data available</td></tr>";
        return;
    }

    // Get the keys from the first object (assumes all objects have the same keys)
    const keys = Object.keys(data[0]);

    // Create one row per key
    keys.forEach(key => {
        const row = document.createElement("tr");

        // First cell: key name (field label)
        const keyCell = document.createElement("th");
        keyCell.textContent = key;
        row.appendChild(keyCell);

        // Next cells: values for this key across all entries
        data.forEach(entry => {
            const valueCell = document.createElement("td");
            valueCell.textContent = entry[key];
            row.appendChild(valueCell);
        });

        table.appendChild(row);
    });
}