document.addEventListener("DOMContentLoaded", () => {
    const flashes = document.querySelectorAll(".flash");
    flashes.forEach((flash) => {
        setTimeout(() => {
            flash.style.transition = "opacity .4s";
            flash.style.opacity = "0";
        }, 3500);
    });
});
