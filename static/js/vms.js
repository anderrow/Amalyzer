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
});
