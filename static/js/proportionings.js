// ---------------- UPDATE PROPORTIONING DATA ---------------- //
document.addEventListener("DOMContentLoaded", function () {
    fetchProportioningData("/api/proportionings"); // Fetch Data as soon as the page is loaded

    const updateButton = document.querySelector("#updateButton"); // Listen to id="updateButton"
    const filterUpdateButton = document.querySelector("#FilterButton"); // Listen to id ='FilterButton'

    if (updateButton) { // If updateButton exists
        updateButton.addEventListener("click", function () { // Check if it's clicked
            console.log("Update Table Data...");
            fetchProportioningData("/api/proportionings"); // Reload Data without refreshing page 
        });
    }

    if (filterUpdateButton) {
        filterUpdateButton.addEventListener("click", function () {
            console.log("Update Table (Filter) Data...");
            // Get the state of the switch (checked or unchecked) and the input text value from Article Filter
            const switchChecked = document.querySelector("#ArticleFilterSwitch").checked; // Get the state of the switch
            const requestedArticle = document.querySelector("#RequestedArticle").value; // Get the value from the input field

            // Get values from the Age Filter
            const ageSwitchChecked = document.querySelector("#AgeFilterSwitch").checked;  // Get Age Filter switch state
            const timeUnit = document.querySelector("#time-unit").value;  // Get the selected time unit (minutes, hours, days)
            const rangeValue = document.querySelector(".short-slider").value;  // Get the slider value

            const url = `/api/proportioningsfilter?switchChecked=${switchChecked}&requestedArticle=${requestedArticle}&ageSwitchChecked=${ageSwitchChecked}&timeUnit=${timeUnit}&rangeValue=${rangeValue}`;

            // Now fetch the data using the correct dynamic URL
            fetchProportioningData(url); // Pass the correct URL with query parameters
        });
    }
    fetch("/common/PropId")
        .then(response => response.text())
        .then(data => {
            console.log("Fetched PropId:", data);
            const inputField = document.getElementById("PropIdInput");
            if (inputField) {
                inputField.value = data;
            }
        })
        .catch(error => console.error("Error fetching current propDbId:", error));
    // Function to load article names into the dropdown
    async function loadArticleNames() {
        try {
            const response = await fetch('/api/articlenames');
            const articleNames = await response.json();
    
            const select = document.getElementById('RequestedArticle');
    
            // Clear previous options except the first one ("Filter by Article")
            select.length = 1;
    
            // Add a new <option> for each article name
            articleNames.forEach(article => {
                const option = document.createElement('option');
                option.value = article.ArticleName;
                option.textContent = article.ArticleName;
                select.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading article names:', error);
        }
    }
    
    // Just call it directly here:
    loadArticleNames();
});
// Function to fetch proportioning data
function fetchProportioningData(link) {
    fetch(link) // Adjust the URL
        .then(response => response.json())
        .then(data => populateTable(data)) // Populate table with the fetched data
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
            <td>${row.Deviation}</td>
            <td>${row.Tolerance}</td>
            <td>${row.StartTime}</td>
            <td>${row.EndTime}</td>
            <td>${row.MixBoxID}</td>
            <td>${row.IngBoxID}</td>
            <td>${row.DosingLocation}</td>
            <td>${row.TypeOfDosing}</td>
            <td>${row.OrderID}</td>
            `;

            //Adding a Listernet to check when one row is clicked
            tr.addEventListener("click", function () {
                //Obtain propDbID of the row selected
                const propDbId = row.ProportioningDBID;
                console.log("Clicked row with PropDbId:", propDbId);
                
                //Send a Post request to the python backend
                fetch(`/api/rowclicked`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ propDbId: propDbId }),
                })
                //Handle response of the backend 
                .then(response => response.json()) //If a JSON comes convert it on response
                .then(result => {
                    console.log("Backend response:", result);
            
                    fetch("/common/PropId")
                    .then(response => response.text())
                    .then(data => {
                        console.log("Fetched PropId:", data);
                        const inputField = document.getElementById("PropIdInput");
                        if (inputField) {
                            inputField.value = data;
                        }
                    })
                    .catch(error => console.error("Error fetching current propDbId:", error));

                })
                .catch(error => console.error("Error sending data to backend:", error)); //If some error happens print it on console
            });
    
            tableBody.appendChild(tr);
    });
}

