
// -------------------- UPDATE ANALYZER DATA -------------------- //
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
