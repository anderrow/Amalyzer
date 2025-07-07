// Call ensureUID() from uid.js to get or generate the user's UID
const uid = ensureUID();

// -------------------- UPDATE ANALYZER DATA -------------------- //
window.addEventListener("DOMContentLoaded", () => {
    // Fetch and inject Graph1 HTML
    fetch("/analyzer/Graph1", { })
    .then(res => res.text())
    .then(html => {
        const graphContainer = document.getElementById("graph-container");
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
    .catch(err => console.error("Error fetching graph:", err));

    // Fetch and inject Graph2 HTML
    fetch("/analyzer/Graph2", { })
    .then(res => res.text())
    .then(html => {
        const graphContainer = document.getElementById("graph-container2");
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
    .catch(err => console.error("Error fetching graph:", err));

    // Fetch and inject Graph2 HTML
    fetch("/analyzer/Graph3", { })
    .then(res => res.text())
    .then(html => {
        const graphContainer = document.getElementById("graph-container3");
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
    .catch(err => console.error("Error fetching graph:", err));

    // Fetch current Proportioning ID
    fetch("/common/PropId")
        .then(response => response.text())
        .then(data => {
            console.log("Fetched PropId:", data);
            const inputField = document.getElementById("ProportioningId");
            if (inputField) {
                inputField.value = data;
            }
        })
        .catch(error => console.error("Error fetching current propDbId:", error));

    // Fetch extra info from  Proportioning ID
    fetch("/common/PropIdExtraInfo")
        .then(response => response.text())
        .then(data => {
            console.log("Fetched PropId extra info:", data);
            const inputField = document.getElementById("InfoPropId");
            if (inputField) {
                inputField.value = data;
            }
        })
        .catch(error => console.error("Error fetching current propDbId:", error));
});


//UPDATE SUMMARY
document.addEventListener("DOMContentLoaded", function () {
    fetchSummaryData("/analyzer/Summary"); // Fetch Data as soon as the page is loaded
    
    const summaryButton = document.querySelector("#SummaryButton"); //Listen to Summary Button
    const propRecordButton = document.querySelector("#PropRecordButton"); //Listen to PropRecord Button
    const logginParamButton = document.querySelector("#LogginParamButton"); //Listen to LoginParam Button
    const lotButton = document.querySelector("#LotButton"); //Listen to Lot Button
    const articleButton = document.querySelector("#ArticleButton"); //Listen to Article Button

    if (summaryButton) { // If Summary exists
        summaryButton.addEventListener("click", function () { // Check if it's clicked
            console.log("Update Summary Data...");
            fetchSummaryData("/analyzer/Summary"); // Reload Data without refreshing page 
        });
    }
    if (propRecordButton) { // If PropRecord exists
        propRecordButton.addEventListener("click", function () { // Check if it's clicked
            console.log("Update PropRecord Data...");
            fetchSummaryData("/analyzer/PropRecord"); // Reload Data without refreshing page 
        });
    }
    if (logginParamButton) { // If LogginParam exists
        logginParamButton.addEventListener("click", function () { // Check if it's clicked
            console.log("Update LogginParam Data...");
            fetchSummaryData("/analyzer/LogginParam"); // Reload Data without refreshing page 
        });
    }
    if (lotButton) { // If Lot Button exists
        lotButton.addEventListener("click", function () { // Check if it's clicked
            console.log("Update Lot Data...");
            fetchSummaryData("/analyzer/Lot"); // Reload Data without refreshing page 
        });
    }
    if (articleButton) { // If Article Button exists
        articleButton.addEventListener("click", function () { // Check if it's clicked
            console.log("Update Article Data...");
            fetchSummaryData("/analyzer/Article"); // Reload Data without refreshing page 
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

