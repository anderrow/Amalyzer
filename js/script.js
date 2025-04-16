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


//----------------UPDATE DATA----------------//
document.addEventListener("DOMContentLoaded", function () {
    fetchProportioningData("http://localhost:5000/api/proportionings"); //Fetch Data as soon as the page is loaded

    const updateButton = document.querySelector("#updateButton"); //Listen to id="updateButton"
    const filterUpdateButton = document.querySelector("#FilterButton"); // Listen to id ='FilterButton'

    if (updateButton) { //If updateButton Exist
        updateButton.addEventListener("click", function () { //Check if it's clicked
            console.log("Update Table Data...");
            fetchProportioningData("http://localhost:5000/api/proportionings"); // Reload Data without refreshing page 
        });
    }
    if (filterUpdateButton){
        filterUpdateButton.addEventListener("click", function () {
            console.log("Update Table (Filter) Data...");
            fetchProportioningData("http://localhost:5000/api/proportioningsfilter"); // Reload Data without refreshing page 
        });
    }
});

function fetchProportioningData(link) {
    fetch(link) // Adjust the URL
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
