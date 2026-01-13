// Sidebar toggler and active-link helper
sidebarToggler();
setActiveLink();

document.body.addEventListener("htmx:afterOnLoad", function (evt) {
    setActiveLink();
});

// Ensure sidebar links reflect current location. Safe no-op when sidebar missing.
function setActiveLink() {
    try {
        const sidebar = document.getElementById("sidebar");
        if (!sidebar) return;

        // Remove any previous active markers
        sidebar
            .querySelectorAll("a.active")
            .forEach((a) => a.classList.remove("active"));

        const current = window.location.pathname + window.location.search;

        // Prefer exact match then startsWith
        const links = Array.from(sidebar.querySelectorAll("a[href]") || []);
        let matched = null;
        for (const a of links) {
            const href = a.getAttribute("href");
            if (!href) continue;
            // Normalize
            if (href === current || href === window.location.pathname) {
                matched = a;
                break;
            }
        }

        if (!matched) {
            for (const a of links) {
                const href = a.getAttribute("href");
                if (!href) continue;
                if (current.startsWith(href)) {
                    matched = a;
                    break;
                }
            }
        }

        if (matched) matched.classList.add("active");
    } catch (e) {
        // Don't crash the page if something unexpected happens
        console.warn("setActiveLink error:", e);
    }
}

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
