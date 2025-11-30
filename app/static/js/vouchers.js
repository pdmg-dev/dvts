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
    // Only rebind if the swapped content contains the vouchers table
    if (evt.target.querySelector("#vouchersTable")) {
        initSelectAllVouchers();
        initTableScroll();
    }
    // Only rebind if the swapped content contains your split button
    if (evt.target.querySelector("#splitBtn")) {
        initSplitLayout();
    }
});

document.addEventListener("DOMContentLoaded", () => {
    initSelectAllVouchers();
    initTableScroll();
    initSplitLayout();
});
