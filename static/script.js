const logoLight = "/static/images/logo_black.png";
const logoDark = "/static/images/logo_white.png";

const iconDark = "/static/images/dark_mode_inv.png";
const iconLight = "/static/images/light_mode.png";


function initTheme() {
    const storedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDark = storedTheme === "dark" || (!storedTheme && prefersDark);

    document.documentElement.classList.toggle("dark", isDark);

    const themeIcon = document.getElementById("theme-icon");
    const logo = document.getElementById("logo");
    const logoFooter = document.getElementById("logo-footer");

    if (themeIcon) themeIcon.src = isDark ? iconLight : iconDark;
    if (logo) logo.src = isDark ? logoDark  : logoLight;
    if (logoFooter) logoFooter.src = isDark ? logoDark  : logoLight;
}

function setupToggle() {
    const toggleDarkMode = document.getElementById("darkmode-toggle");

    if (!toggleDarkMode) return;

    toggleDarkMode.addEventListener("click", () => {
        const isDark = document.documentElement.classList.toggle("dark");

        localStorage.setItem("theme", isDark ? "dark" : "light");

        const themeIcon = document.getElementById("theme-icon");
        const logo = document.getElementById("logo");
        const logoFooter = document.getElementById("logo-footer");

        if (themeIcon) themeIcon.src = isDark ? iconLight : iconDark;
        if (logo) logo.src = isDark ? logoDark : logoLight;
        if (logoFooter)logoFooter.src = isDark ? logoDark : logoLight;
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    setupToggle();
});