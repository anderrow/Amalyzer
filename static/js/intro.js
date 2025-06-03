// ---------------- INTRO ---------------- //
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