// Intro
setTimeout(() => {
    const intro = document.getElementById("intro");

    // Aplica el efecto de desvanecimiento
    intro.style.opacity = "0";
    intro.style.visibility = "hidden"; // Esto lo oculta completamente después de la transición

    // Espera la duración de la animación antes de redirigir
    setTimeout(() => {
        window.location.href = "./pages/proportionings.html"; // Redirección
    }, 1000); // Espera 1s para la animación antes de redirigir
}, 3000); // Duración de la intro (3s antes de iniciar el fade-out)


// End of Intro
