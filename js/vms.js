document.addEventListener("DOMContentLoaded", function () {
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
        
    // Fetch extra info from  Proportioning ID
    fetch("http://localhost:5000/common/PropIdExtraInfo")
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
