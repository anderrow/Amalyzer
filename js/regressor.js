
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
});