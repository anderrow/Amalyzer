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
    fetch("/regressor/Graph")
        .then(res => res.text())
        .then(html => {
            const graphContainer = document.getElementById("regressor_graph_container");
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

    fetchSummaryData("/regressor/SummaryTable");

    const updateButton = document.querySelector("#UpdateRegressor");
    if (updateButton) {
        updateButton.addEventListener("click", function () {
            console.log("Updating Regressor Graph...");

            const intermediatesInput = document.querySelector("#IntermediatesBin");
            const regressionsInput = document.querySelector("#PolynomialRegressionsSlider");

            if (intermediatesInput && regressionsInput) {
                const intermediates = intermediatesInput.value;
                const amountOfRegressions = regressionsInput.value;

                const url = `/regressor/Graph?intermediates=${intermediates}&amountOfRegressions=${amountOfRegressions}`;

                fetch(url)
                    .then(res => res.text())
                    .then(html => {
                        const graphContainer = document.getElementById("regressor_graph_container");
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
                    })
                    .catch(err => console.error("Error updating regressor graph:", err));
            } else {
                console.warn("One or both sliders are missing.");
            }
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

function populateTable(data) {
    const table = document.getElementById("RegressorTable");
    table.innerHTML = "";

    if (!Array.isArray(data) || data.length === 0) {
        table.innerHTML = "<tr><td>No data available</td></tr>";
        return;
    }

    // Mapping keys to human-readable labels
    const labels = {
        lot_id: "LotID",
        lot_dbid: "Lot(DB)ID",
        c2_in_flowtablequality: "Quality(FlowTable)",
        c2_in_measureddensity: "Measured Density",
        c2_in_angleofrepose: "Measured AOR",
        c2_in_oscillationfactor: "Oscilation Factor",
        c2_in_oscillationmin: "Oscilation Min",
        c2_in_oscillationspeed: "Oscilation Speed",
        c1_in_minflow: "Min Flow",
        c1_in_maxflow: "Max Flow",
        IntermediateCount: "Intermediate Count"
    };

    const rowData = data[0]; // single dictionary object

    // For each key-value, create a row
    Object.keys(rowData).forEach(key => {
        const row = document.createElement("tr");

        // Key cell (th)
        const keyCell = document.createElement("th");
        keyCell.textContent = labels[key] || key; // use label if exists or fallback to key
        row.appendChild(keyCell);

        // Value cell (td)
        const valueCell = document.createElement("td");
        valueCell.textContent = rowData[key];
        row.appendChild(valueCell);

        table.appendChild(row);
    });
}
