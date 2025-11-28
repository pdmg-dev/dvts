function sidebarToggler(toggleId, sidebarId) {
    const sidebarToggle = document.getElementById(toggleId);
    const sidebar = document.getElementById(sidebarId);

    sidebarToggle.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
    });
}

sidebarToggler("sidebarToggle", "sidebar");

function navlinkActive() {
    document.addEventListener("htmx:afterOnLoad", function (event) {
        document
            .querySelectorAll("#voucherMenu .nav-link")
            .forEach((link) => link.classList.remove("active"));
        if (event.detail.element.closest("#voucherMenu")) {
            event.detail.element.classList.add("active");
        }
    });
}

navlinkActive();
