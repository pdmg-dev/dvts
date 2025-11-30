// Initialize all functionalities on page load
initSelectAllVouchers();
initTableScroll();
initSplitLayout();
initTableArrowNavigation();

// Re-initialize functionalities after HTMX content swap
document.addEventListener("htmx:afterSwap", (evt) => {
    // Only rebind if the swapped content contains the vouchers table
    if (evt.target.querySelector("#vouchersTable")) {
        initSelectAllVouchers();
        initTableScroll();
        initTableArrowNavigation();
    }
    // Only rebind if the swapped content contains your split button
    if (evt.target.querySelector("#splitBtn")) {
        initSplitLayout();
    }
});

// Select All Vouchers
function initSelectAllVouchers() {
    const selectAllBtn = document.getElementById("selectAllBtn");
    const selectAllCbx = selectAllBtn.querySelector('input[type="checkbox"]');

    const vouchersTable = document.getElementById("vouchersTable");
    const selectBtns = vouchersTable.querySelectorAll("button");
    const selectCbxs = vouchersTable.querySelectorAll('input[type="checkbox"]');

    const dropdownMenu = document
        .getElementById("selectAllDropdown")
        .querySelector(".dropdown-menu");

    // Select All button
    selectAllBtn.addEventListener("click", (e) => {
        if (e.target !== selectAllCbx) {
            selectAllCbx.click(); // Toggle checkbox
        }
    });

    // Select All checkbox
    selectAllCbx.addEventListener("change", () => {
        selectCbxs.forEach((cb) => (cb.checked = selectAllCbx.checked));
    });

    // Individual voucher select buttons
    selectBtns.forEach((btn) => {
        const cb = btn.querySelector('input[type="checkbox"]');

        // Button click toggles checkbox
        btn.addEventListener("click", (e) => {
            if (e.target !== cb) {
                cb.click();
            }
        });

        // Checkbox change updates Select All state
        cb.addEventListener("change", () => {
            const anyChecked = Array.from(selectCbxs).some((c) => c.checked);
            selectAllCbx.checked = anyChecked;
        });
    });

    // Dropdown menu actions
    dropdownMenu.addEventListener("click", (event) => {
        const clickedItem = event.target;
        if (!clickedItem.classList.contains("dropdown-item")) return;

        const action = clickedItem.textContent.trim();

        // Perform action based on clicked item
        switch (action) {
            case "All":
                selectCbxs.forEach((cb) => (cb.checked = true)); // Check all
                selectAllCbx.checked = true;
                break;

            case "None":
                selectCbxs.forEach((cb) => (cb.checked = false)); // Uncheck all
                selectAllCbx.checked = false;
                break;
        }
    });
}

// Table Scroll Behavior
function initTableScroll() {
    const tableContainer = document.querySelector(".table-container");
    const toolbar = document.querySelector(".toolbar");

    tableContainer.addEventListener("scroll", () => {
        // Add or remove class based on scroll position
        if (tableContainer.scrollTop > 0) {
            toolbar.classList.add("table-scrolled");
        } else {
            toolbar.classList.remove("table-scrolled");
        }
    });
}

// Split Layout Toggle
function initSplitLayout() {
    const splitBtn = document.getElementById("splitBtn");
    const splitWrapper = document.querySelector(".table-split-wrapper");
    const rows = document.querySelectorAll("#vouchersTable tr");
    const tableContainer = splitWrapper.querySelector(".table-container");
    const detailPanel = splitWrapper.querySelector(".detail-panel");

    // Apply layout state to wrapper, button, and rows
    function applyLayout(active) {
        splitWrapper.classList.toggle("split-active", active);
        splitBtn.classList.toggle("active", active);

        // Update each row's htmx attributes
        rows.forEach((row) => {
            row.setAttribute("hx-target", active ? "#splitPane" : "#content");
            row.setAttribute("hx-push-url", active ? "false" : "true");
            active
                ? row.setAttribute("hx-headers", '{"HX-Layout":"split"}')
                : row.removeAttribute("hx-headers");
        });
    }

    // Button click toggles layout
    splitBtn.addEventListener("click", () => {
        const active = splitWrapper.classList.toggle("split-active");
        applyLayout(active);
        localStorage.setItem("vouchersSplitLayout", active ? "true" : "false"); // Save setting
    });

    // Apply saved state immediately
    const saved = localStorage.getItem("vouchersSplitLayout") === "true";
    if (saved) {
        // Disable transitions temporarily so it "just appears" split
        tableContainer.classList.add("no-transition");
        detailPanel.classList.add("no-transition");
        applyLayout(true);

        // Force reflow, then remove no-transition so future toggles animate
        void splitWrapper.offsetHeight;
        tableContainer.classList.remove("no-transition");
        detailPanel.classList.remove("no-transition");
    } else {
        applyLayout(false);
    }
}

function initTableArrowNavigation() {
    const rows = document.querySelectorAll("#vouchersTable tbody tr");
    if (!rows.length) return;

    // Ensure rows are focusable
    rows.forEach((row) => row.setAttribute("tabindex", "0"));

    document.addEventListener("keydown", function (event) {
        const active = document.activeElement;
        let currentIndex = Array.from(rows).indexOf(active);

        // Find the split wrapper
        const splitWrapper = document.querySelector(".table-split-wrapper");
        const splitActive =
            splitWrapper && splitWrapper.classList.contains("split-active");

        // Arrow navigation
        if (event.key === "ArrowUp" || event.key === "ArrowDown") {
            if (currentIndex === -1) {
                rows[0].focus();
                if (splitActive) {
                    rows[0].click();
                }
            } else {
                if (event.key === "ArrowUp" && currentIndex > 0) {
                    rows[currentIndex - 1].focus();
                    if (splitActive) {
                        rows[currentIndex - 1].click();
                    }
                } else if (
                    event.key === "ArrowDown" &&
                    currentIndex < rows.length - 1
                ) {
                    rows[currentIndex + 1].focus();
                    if (splitActive) {
                        rows[currentIndex + 1].click();
                    }
                }
            }
            event.preventDefault(); // Prevent default scrolling
        }

        // Enter key handling
        if (event.key === "Enter" && currentIndex !== -1) {
            rows[currentIndex].click(); // Trigger row click
            event.preventDefault();
        }
    });
}
