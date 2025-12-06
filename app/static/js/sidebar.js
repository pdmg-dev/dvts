sidebarToggler();
setActiveLink();

document.body.addEventListener("htmx:afterOnLoad", function (evt) {
    setActiveLink();
});

function sidebarToggler() {
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    sidebarToggle.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
    });
}
