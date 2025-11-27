function sidebarToggler(toggleId, sidebarId) {
    const sidebarToggle = document.getElementById(toggleId);
    const sidebar = document.getElementById(sidebarId);

    sidebarToggle.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
    });
}

sidebarToggler("sidebarToggle", "sidebar");
