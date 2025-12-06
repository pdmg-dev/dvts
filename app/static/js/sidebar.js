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

function setActiveLink() {
    // Remove active class from all sidebar links
    document
        .querySelectorAll("#sidebar .nav-link.active")
        .forEach((a) => a.classList.remove("active"));

    // Add active to the clicked link
    if (evt.detail.requestConfig.elt.matches(".nav-link")) {
        evt.detail.requestConfig.elt.classList.add("active");
    }
}
