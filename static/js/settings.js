// Call ensureUID() from uid.js to get or generate the user's UID
const uid = ensureUID();

document.addEventListener("DOMContentLoaded", function () {
    const button = document.getElementById("SetEnvironment");
    const select = document.getElementById("ChoosenEnvironment");

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
                    uid: uid
                }),
                credentials: "include",
            });

            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            const result = await response.json();
            console.log("Server response:", result);
        } catch (error) {
            console.error("Error sending environment:", error);
        }
    });
});
