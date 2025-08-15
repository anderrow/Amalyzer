// Call ensureUID() from uid.js to get or generate the user's UID
const uid = ensureUID();

document.addEventListener("DOMContentLoaded", function () {
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

    // Fetch and inject Graph HTML
    fetch("/vms/Graph")
        .then(res => res.text())
        .then(html => {
            const graphContainer = document.getElementById("VMS_graph_container");
            graphContainer.innerHTML = html;

            graphContainer.querySelectorAll("script").forEach(oldScript => {
                const newScript = document.createElement("script");
                if (oldScript.src) {
                    newScript.src = oldScript.src;
                } else {
                    newScript.textContent = oldScript.textContent;
                }
                document.head.appendChild(newScript);
                oldScript.remove();
            });
        });
    
    fetchSummaryData("/vms/Summary");
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
    const table = document.getElementById("VmsSummaryTable");

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
