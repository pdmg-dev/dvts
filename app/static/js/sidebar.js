sidebarToggler();
setActiveLink();

document.body.addEventListener("htmx:afterOnLoad", function (evt) {
    setActiveLink();
});

function sidebarToggler() {
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");
    const mainContent = document.querySelector("main");

    if (!sidebarToggle || !sidebar) return;

    let isAnimating = false;

    function setPanelState(active, animate = true) {
        if (isAnimating) return;

        if (!animate) {
            sidebar.classList.add("no-transition");
            if (mainContent) mainContent.classList.add("no-transition");
        }

        isAnimating = true;

        // Toggle active class on sidebar
        sidebar.classList.toggle("active", active);

        // Toggle sidebar-open class on main content
        if (mainContent) {
            mainContent.classList.toggle("sidebar-open", active);
        }

        localStorage.setItem("sidebarOpen", active ? "true" : "false");

        setTimeout(
            () => {
                if (!animate) {
                    sidebar.classList.remove("no-transition");
                    if (mainContent)
                        mainContent.classList.remove("no-transition");
                }
                isAnimating = false;
            },
            animate ? 350 : 0,
        );
    }

    // Prevent duplicate listeners by removing old ones first
    sidebarToggle.replaceWith(sidebarToggle.cloneNode(true));
    const newSidebarToggle = document.getElementById("sidebarToggle");

    newSidebarToggle.addEventListener("click", (evt) => {
        evt.preventDefault();
        evt.stopPropagation();

        if (isAnimating) return;

        const isActive = sidebar.classList.contains("active");
        setPanelState(!isActive, true);
    });

    // Restore persisted state (default open)
    const savedOpen = localStorage.getItem("sidebarOpen") === "true";
    if (savedOpen) {
        setPanelState(true, false);
    }
}
