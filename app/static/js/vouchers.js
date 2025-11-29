function selectAllBehavior(selectAllId, vouchersTableId, dropdownId) {
    const selectAllBtn = document.getElementById(selectAllId);
    const checkbox = selectAllBtn.querySelector('input[type="checkbox"]');

    const vouchersTable = document.getElementById(vouchersTableId);
    const tableSelectButtons = vouchersTable.querySelectorAll("button");
    const tableCheckboxes = vouchersTable.querySelectorAll(
        'input[type="checkbox"]',
    );

    const dropdownMenu = document
        .getElementById(dropdownId)
        .querySelector(".dropdown-menu");

    // Toggle select all when clicking the selectAll button
    selectAllBtn.addEventListener("click", (e) => {
        if (e.target !== checkbox) {
            checkbox.checked = !checkbox.checked;
            checkbox.dispatchEvent(new Event("change", { bubbles: true }));
        }
    });

    // Select all / unselect all when the selectAll checkbox changes
    checkbox.addEventListener("change", () => {
        tableCheckboxes.forEach((cb) => (cb.checked = checkbox.checked));
    });

    // Handle dropdown menu actions
    dropdownMenu.addEventListener("click", (event) => {
        const clickedItem = event.target;
        if (clickedItem.classList.contains("dropdown-item")) {
            const action = clickedItem.textContent.trim();

            if (action === "All") {
                tableCheckboxes.forEach((cb) => (cb.checked = true));
                checkbox.checked = true;
            }
            if (action === "None") {
                tableCheckboxes.forEach((cb) => (cb.checked = false));
                checkbox.checked = false;
            }
            if (action === "Read") {
                tableCheckboxes.forEach(
                    (cb) => (cb.checked = cb.dataset.status === "read"),
                );
                checkbox.checked = Array.from(tableCheckboxes).some(
                    (c) => c.checked,
                );
            }
            if (action === "Unread") {
                tableCheckboxes.forEach(
                    (cb) => (cb.checked = cb.dataset.status === "unread"),
                );
                checkbox.checked = Array.from(tableCheckboxes).some(
                    (c) => c.checked,
                );
            }
        }
    });

    // Handle table button clicks and checkbox syncing
    tableSelectButtons.forEach((btn) => {
        const cb = btn.querySelector('input[type="checkbox"]');

        // Toggle checkbox when button is clicked
        btn.addEventListener("click", (e) => {
            if (e.target !== cb) {
                cb.checked = !cb.checked;
                cb.dispatchEvent(new Event("change", { bubbles: true }));
            }
        });

        // Update selectAll checkbox if any table checkbox is checked
        cb.addEventListener("change", () => {
            const anyChecked = Array.from(tableCheckboxes).some(
                (c) => c.checked,
            );
            checkbox.checked = anyChecked;
        });
    });
}

function scrollTable(tableSelector, toolbarSelector) {
    const tableContainer = document.querySelector(tableSelector);
    const toolbar = document.querySelector(toolbarSelector);

    tableContainer.addEventListener("scroll", () => {
        // If the table is scrolled down
        if (tableContainer.scrollTop > 0) {
            toolbar.classList.add("table-scrolled");
        } else {
            // Back at the very top
            toolbar.classList.remove("table-scrolled");
        }
    });
}

// Split Layout
function splitLayout() {
    const splitBtn = document.getElementById("splitBtn");
    const splitWrapper = document.querySelector(".table-split-wrapper");
    const rows = document.querySelectorAll("#vouchersTable tr");

    splitBtn.addEventListener("click", () => {
        console.log("Split layout button clicked");

        const active = splitWrapper.classList.toggle("split-active");
        splitBtn.classList.toggle("active", active);
        console.log(`Split layout is now ${active ? "active" : "inactive"}`);

        rows.forEach((row) => {
            if (active) {
                console.log("Setting target to splitPane");
                row.setAttribute("hx-target", "#splitPane");
                row.setAttribute("hx-headers", '{"HX-Layout":"split"}');
            } else {
                console.log("Setting target to content");
                row.setAttribute("hx-target", "#content");
                row.removeAttribute("hx-headers");
            }
        });

        localStorage.setItem("vouchersSplitLayout", active ? "true" : "false");
    });

    const splitSetting = localStorage.getItem("vouchersSplitLayout");
    if (splitSetting === "true") {
        // Disable animation temporarily
        splitWrapper
            .querySelector(".table-container")
            .classList.add("no-transition");
        splitWrapper
            .querySelector(".detail-panel")
            .classList.add("no-transition");

        console.log("Applying saved split layout setting: active");
        splitWrapper.classList.add("split-active");
        splitBtn.classList.add("active");
        rows.forEach((row) => {
            row.setAttribute("hx-target", "#splitPane");
            row.setAttribute("hx-headers", '{"HX-Layout":"split"}');
        });
    } else {
        console.log("Applying saved split layout setting: inactive");
        splitWrapper.classList.remove("split-active");
        splitBtn.classList.remove("active");
        rows.forEach((row) => {
            row.setAttribute("hx-target", "#content");
            row.removeAttribute("hx-headers");
        });

        // Force reflow, then remove no-transition so future toggles animate
        void splitWrapper.offsetHeight;
        splitWrapper
            .querySelector(".table-container")
            .classList.remove("no-transition");
        splitWrapper
            .querySelector(".detail-panel")
            .classList.remove("no-transition");
    }
}

document.addEventListener("htmx:afterSwap", (evt) => {
    // Only rebind if the swapped content contains your split button
    if (evt.target.querySelector("#splitBtn")) {
        splitLayout();
    }
    if (evt.target.querySelector("#vouchersTable")) {
        selectAllBehavior("selectAll", "vouchersTable", "selectAllDropdown");
        scrollTable(".table-container", ".toolbar");
    }
});
document.addEventListener("DOMContentLoaded", () => {
    splitLayout();
    selectAllBehavior("selectAll", "vouchersTable", "selectAllDropdown");
    scrollTable(".table-container", ".toolbar");
});
