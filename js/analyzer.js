
// -------------------- UPDATE ANALYZER DATA -------------------- //
//UPDATE PROPORTIONING ID
window.addEventListener("DOMContentLoaded", () => {
    fetch("http://localhost:5000/analyzer/PropId")
        .then(response => response.text())
        .then(data => {
            console.log("Fetched PropId:", data);
            const inputField = document.getElementById("ProportioningId");
            if (inputField) {
                inputField.value = data;
            }
        })
        .catch(error => console.error("Error fetching current propDbId:", error));
});

//UPDATE SUMMARY
document.addEventListener("DOMContentLoaded", function () {
    fetchSummaryData("http://localhost:5000/analyzer/PropIdSummary"); // Fetch Data as soon as the page is loaded
    
    const summaryButton = document.querySelector("#SummaryButton"); //Listen to Summary Button

    if (summaryButton) { // If Summary exists
        summaryButton.addEventListener("click", function () { // Check if it's clicked
            console.log("Update Summary Data...");
            fetchSummaryData("http://localhost:5000/analyzer/PropIdSummary"); // Reload Data without refreshing page 
        });
    }
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
    const table = document.getElementById("AnalyzerSummaryTable");

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

