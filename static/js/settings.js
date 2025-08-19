// Call ensureUID() from uid.js to get or generate the user's UID
const uid = ensureUID();

document.addEventListener("DOMContentLoaded", function () {
    const button = document.getElementById("SetEnvironment");
    const select = document.getElementById("ChoosenEnvironment");
    const rowAmount = document.getElementById("RowAmount");

    button.addEventListener("click", async function () {
        const selectedEnvironment = select.value;

        const propDbId = null; 

        try {
            const response = await fetch("/settings/selectedenvironment", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    environment: selectedEnvironment,
                    propDbId: propDbId,
                    uid: uid,
                    rows: rowAmount.value, 
                }),
                credentials: "include",
            });

            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            const result = await response.json();
            console.log("Server response:", result);
            showPopupMessage("✅ Rows to fetch: " + rowAmount.value);
            showPopupMessage("✅ Environment chosen: " + selectedEnvironment); 
            showPopupMessage("PropDbId is now set to Null" , true);


        } catch (error) {
            console.error("Error sending environment:", error);
        }
    });
    loadEnvironments();
});


//Pop Up Message Function//
let popupOffset = 0;

function showPopupMessage(message, isError = false) {
    const popup = document.createElement("div");
    popup.textContent = message;
    popup.style.position = "fixed";
    popup.style.bottom = (20 + popupOffset) + "px";
    popup.style.right = "20px";
    popup.style.padding = "12px 20px";
    popup.style.backgroundColor = isError ? "#dc3545" : "#28a745";
    popup.style.color = "white";
    popup.style.borderRadius = "8px";
    popup.style.boxShadow = "0 2px 8px rgba(0,0,0,0.2)";
    popup.style.zIndex = "1000";
    popup.style.opacity = "0";
    popup.style.transition = "opacity 0.3s ease";

    document.body.appendChild(popup);

    // Aumentar el offset para próximos popups
    popupOffset += 60;

    // Forzar reflow
    void popup.offsetWidth;
    popup.style.opacity = "1";

    setTimeout(() => {
        popup.style.opacity = "0";
        popup.addEventListener("transitionend", () => {
            popup.remove();
            popupOffset -= 60; // Liberar espacio cuando desaparece
        });
    }, 3000);
}

async function loadEnvironments() {
    try {
        const response = await fetch('/settings/availableenvironments');
        const environmentsNames = await response.json();
        const select = document.getElementById('ChoosenEnvironment');

        select.length = 1;

        const fragment = document.createDocumentFragment();
        environmentsNames.forEach(environment => {
            const option = document.createElement('option');
            option.value = environment;
            option.textContent = environment;
            fragment.appendChild(option);
        });
        select.appendChild(fragment);
    } catch (error) {
        console.error('Error loading environment names:', error);
        showError('Failed to load environements names. Please try again.');
    }
}