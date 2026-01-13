// Initialize all functionalities on page load
document.addEventListener("DOMContentLoaded", function () {
    // Check if we're on the vouchers page
    const vouchersTable = document.getElementById("vouchersTable");
    if (!vouchersTable) {
        return; // Not on vouchers page, skip
    }

    // Try to restore sort/filter params from localStorage if not in URL
    const urlParams = new URLSearchParams(window.location.search);
    const hasAnyParams = urlParams.toString().length > 0;

    if (!hasAnyParams) {
        // No params in URL, check localStorage
        const savedParams = localStorage.getItem("voucherListParams");
        if (savedParams) {
            // Reload page with saved params
            const newUrl = `${window.location.pathname}?${savedParams}`;
            window.location.href = newUrl;
            return; // Exit - page will reload
        }
    }

    // Save current params for next visit
    const currentParams = window.location.search.substring(1);
    if (currentParams) {
        localStorage.setItem("voucherListParams", currentParams);
    }

    initSelectAllVouchers();
    initTableScroll();
    initSplitLayout();
    initTableArrowNavigation();
    initFilterPanel();
    initExportButton();
    initTableSorting();
});

// Re-initialize functionalities after HTMX content swap
document.addEventListener("htmx:afterSwap", (evt) => {
    // Check if this is the vouchers page content
    const isVouchersSwap =
        !!evt.target.querySelector("#vouchersTable") ||
        !!evt.target.querySelector("#filterBtn");
    if (!isVouchersSwap) return;

    // If navigated back to vouchers without params, restore last saved ones once
    const hasParams =
        new URLSearchParams(window.location.search).toString().length > 0;
    if (!hasParams) {
        const savedParams = localStorage.getItem("voucherListParams");
        const restoredOnce =
            sessionStorage.getItem("voucherListRestored") === "true";
        if (savedParams && !restoredOnce) {
            const url = `${window.location.pathname}?${savedParams}`;
            sessionStorage.setItem("voucherListRestored", "true");
            // Update URL so subsequent swaps see params and avoid loops
            window.history.replaceState({}, "", url);
            // Refresh vouchers content with restored params
            htmx.ajax("GET", url, "#content");
            return;
        }
    }

    // Save current params to localStorage for persistence
    const currentParams = window.location.search.substring(1);
    if (currentParams) {
        localStorage.setItem("voucherListParams", currentParams);
    }

    // Only rebind if the swapped content contains the vouchers table
    if (evt.target.querySelector("#vouchersTable")) {
        initSelectAllVouchers();
        initTableScroll();
        initTableArrowNavigation();
        initTableSorting();
    }
    // Only rebind if the swapped content contains your split button
    if (evt.target.querySelector("#splitBtn")) {
        initSplitLayout();
    }
    // Rebind filter panel after HTMX swaps
    if (evt.target.querySelector("#filterBtn")) {
        initFilterPanel();
    }
    if (evt.target.querySelector("#exportDropdown")) {
        initExportButton();
    }
});

// Select All Vouchers
function initSelectAllVouchers() {
    const selectAllBtn = document.getElementById("selectAllBtn");
    const vouchersTable = document.getElementById("vouchersTable");

    // Guard against missing elements
    if (!selectAllBtn || !vouchersTable) return;

    const selectAllCbx = selectAllBtn.querySelector('input[type="checkbox"]');
    const selectBtns = vouchersTable.querySelectorAll("button");
    const selectCbxs = vouchersTable.querySelectorAll('input[type="checkbox"]');

    const selectAllDropdown = document.getElementById("selectAllDropdown");
    if (!selectAllDropdown) return;

    const dropdownMenu = selectAllDropdown.querySelector(".dropdown-menu");
    if (!dropdownMenu) return;

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

    // Guard against missing elements
    if (!tableContainer || !toolbar) return;

    tableContainer.addEventListener("scroll", () => {
        // Add or remove class based on scroll position
        const isScrolled = tableContainer.scrollTop > 0;
        const toolbar = document.querySelector(".toolbar");
        const thead = document.querySelector(".vouchers-table thead");

        if (isScrolled) {
            toolbar?.classList.add("table-scrolled");
            thead?.classList.add("table-scrolled");
        } else {
            toolbar?.classList.remove("table-scrolled");
            thead?.classList.remove("table-scrolled");
        }
    });
}

// Split Layout Toggle
function initSplitLayout() {
    const splitBtn = document.getElementById("splitBtn");
    const splitWrapper = document.querySelector(".table-split-wrapper");

    // Guard against missing elements
    if (!splitBtn || !splitWrapper) return;

    const tableContainer = splitWrapper.querySelector(".table-container");
    const detailPanel = splitWrapper.querySelector(".detail-panel");
    const vouchersTable = document.getElementById("vouchersTable");

    if (!tableContainer || !detailPanel || !vouchersTable) return;

    const rows = vouchersTable.querySelectorAll("tr");

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
    const vouchersTable = document.getElementById("vouchersTable");

    // Guard against missing table
    if (!vouchersTable) return;

    const rows = vouchersTable.querySelectorAll("tbody tr");
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

// Filter Panel
function initFilterPanel() {
    const filterBtn = document.getElementById("filterBtn");
    const filterPanel = document.getElementById("filterPanel");

    if (!filterBtn || !filterPanel) return;

    const closeFilterBtn = document.getElementById("closeFilterBtn");
    const clearFiltersBtn = document.getElementById("clearFiltersBtn");
    const mainContent = document.querySelector("main");

    // Initialize date pickers if Tempus Dominus is available
    initFilterDatePickers();

    let isAnimating = false;

    function setPanelState(active, animate = true) {
        if (isAnimating) return;
        if (!animate) {
            filterPanel.classList.add("no-transition");
            if (mainContent) mainContent.classList.add("no-transition");
        }

        isAnimating = true;
        filterPanel.classList.toggle("active", active);
        filterBtn.classList.toggle("active", active);
        if (mainContent) {
            mainContent.classList.toggle("filter-open", active);
        }

        localStorage.setItem("filterPanelOpen", active ? "true" : "false");

        setTimeout(
            () => {
                if (!animate) {
                    filterPanel.classList.remove("no-transition");
                    if (mainContent)
                        mainContent.classList.remove("no-transition");
                }
                isAnimating = false;
            },
            animate ? 350 : 0,
        );
    }

    // Check if already bound to prevent duplicate listeners
    if (filterBtn.dataset.bound === "true") return;
    filterBtn.dataset.bound = "true";

    filterBtn.addEventListener("click", (evt) => {
        evt.preventDefault();
        evt.stopPropagation();

        if (isAnimating) return;

        const isOpen = filterPanel.classList.contains("active");
        setPanelState(!isOpen, true);
    });

    const closePanel = () => setPanelState(false, true);

    // Close on X button click
    if (closeFilterBtn) {
        closeFilterBtn.addEventListener("click", (evt) => {
            evt.preventDefault();
            evt.stopPropagation();
            closePanel();
        });
    }

    // Clear filters
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener("click", (evt) => {
            evt.preventDefault();
            const filterForm = document.getElementById("filterForm");
            if (filterForm) {
                filterForm.reset();
                // Trigger apply with cleared filters
                const applyBtn = document.getElementById("applyFiltersBtn");
                if (applyBtn) {
                    htmx.trigger(applyBtn, "click");
                }
            }
        });
    }

    // Restore persisted state (default closed)
    const savedOpen = localStorage.getItem("filterPanelOpen") === "true";
    if (savedOpen) {
        setPanelState(true, false);
    }

    filterPanel.dataset.bound = "true";
}

// Export button
function initExportButton() {
    const exportDropdown = document.getElementById("exportDropdown");
    const exportFiltered = document.getElementById("exportFiltered");
    const exportAll = document.getElementById("exportAll");
    const exportCurrentPage = document.getElementById("exportCurrentPage");

    if (!exportDropdown || exportDropdown.dataset.bound === "true") return;

    const exportUrl = exportDropdown.dataset.exportUrl;

    function collectFilters() {
        const form = document.getElementById("filterForm");
        const params = new URLSearchParams();

        if (form) {
            const fields = [
                "category",
                "resp_center",
                "mode_of_payment",
                "date_from",
                "date_to",
            ];
            fields.forEach((name) => {
                const el = form.elements[name];
                if (el && el.value) {
                    params.append(name, el.value);
                }
            });
        }
        return params;
    }

    function doExport(includeFilters, currentPageOnly) {
        const params = includeFilters
            ? collectFilters()
            : new URLSearchParams();
        if (currentPageOnly) {
            params.append("page_only", "true");
        }
        const url = params.toString()
            ? `${exportUrl}?${params.toString()}`
            : exportUrl;
        window.location.href = url;
    }

    if (exportFiltered) {
        exportFiltered.addEventListener("click", (evt) => {
            evt.preventDefault();
            doExport(true, false);
        });
    }

    if (exportAll) {
        exportAll.addEventListener("click", (evt) => {
            evt.preventDefault();
            doExport(false, false);
        });
    }

    if (exportCurrentPage) {
        exportCurrentPage.addEventListener("click", (evt) => {
            evt.preventDefault();
            doExport(true, true);
        });
    }

    exportDropdown.dataset.bound = "true";
}

// Initialize Tempus Dominus date pickers for filter panel
function initFilterDatePickers() {
    if (typeof tempusDominus === "undefined") {
        console.warn("Tempus Dominus not loaded");
        return;
    }

    const dateFromInput = document.getElementById("filterDateFrom");
    const dateToInput = document.getElementById("filterDateTo");
    const dateFromValue = document.getElementById("dateFromValue");
    const dateToValue = document.getElementById("dateToValue");

    if (!dateFromInput || !dateToInput) return;

    const pickerConfig = {
        localization: {
            locale: "en",
            format: "yyyy-MM-dd",
        },
        display: {
            viewMode: "calendar",
            theme: "light",
            keyboardNavigation: true,
            icons: {
                type: "icons",
                time: "bi bi-clock",
                date: "bi bi-calendar-event",
                up: "bi bi-arrow-up",
                down: "bi bi-arrow-down",
                previous: "bi bi-chevron-left",
                next: "bi bi-chevron-right",
                today: "bi bi-calendar-check",
                clear: "bi bi-trash",
                close: "bi bi-x-lg",
            },
            buttons: {
                today: true,
                clear: true,
                close: true,
            },
            components: {
                calendar: true,
                date: true,
                month: true,
                year: true,
                decades: false,
                clock: false,
                hours: false,
                minutes: false,
                seconds: false,
            },
        },
    };

    // Initialize "From" date picker
    const pickerFrom = new tempusDominus.TempusDominus(
        dateFromInput,
        pickerConfig,
    );
    dateFromInput.addEventListener("change.datetimepicker", (e) => {
        if (e.detail.date) {
            const date = e.detail.date;
            const formattedDate = date.toFormat("yyyy-MM-dd");
            if (dateFromValue) {
                dateFromValue.value = formattedDate;
            }
        } else {
            if (dateFromValue) {
                dateFromValue.value = "";
            }
        }
    });

    // Initialize "To" date picker
    const pickerTo = new tempusDominus.TempusDominus(dateToInput, pickerConfig);
    dateToInput.addEventListener("change.datetimepicker", (e) => {
        if (e.detail.date) {
            const date = e.detail.date;
            const formattedDate = date.toFormat("yyyy-MM-dd");
            if (dateToValue) {
                dateToValue.value = formattedDate;
            }
        } else {
            if (dateToValue) {
                dateToValue.value = "";
            }
        }
    });

    // Set initial values if filters exist
    if (dateFromValue && dateFromValue.value) {
        pickerFrom.viewDate(new tempusDominus.DateTime(dateFromValue.value));
        dateFromInput.value = dateFromValue.value;
    }

    if (dateToValue && dateToValue.value) {
        pickerTo.viewDate(new tempusDominus.DateTime(dateToValue.value));
        dateToInput.value = dateToValue.value;
    }
}

// Table Sorting
function initTableSorting() {
    const sortableHeaders = document.querySelectorAll(
        ".vouchers-table th.sortable",
    );

    sortableHeaders.forEach((header) => {
        header.addEventListener("click", () => {
            const sortColumn = header.getAttribute("data-sort-column");
            const currentSort = new URLSearchParams(window.location.search).get(
                "sort_by",
            );
            const currentDir = new URLSearchParams(window.location.search).get(
                "sort_dir",
            );

            let newDir = "asc"; // Default to ascending

            // Toggle direction if clicking the same column
            if (currentSort === sortColumn && currentDir === "asc") {
                newDir = "desc";
            }

            // Persist to localStorage
            localStorage.setItem("voucherSortBy", sortColumn);
            localStorage.setItem("voucherSortDir", newDir);

            // Build URL with sort parameters, preserving remember_view
            const url = new URL(window.location);
            url.searchParams.set("sort_by", sortColumn);
            url.searchParams.set("sort_dir", newDir);

            // Preserve remember_view checkbox state
            const rememberCheck = document.getElementById("rememberViewCheck");
            if (rememberCheck) {
                url.searchParams.set(
                    "remember_view",
                    rememberCheck.checked ? "true" : "false",
                );
            }

            // Save all current params to localStorage
            localStorage.setItem("voucherListParams", url.search.substring(1));

            // Update browser history with new URL
            window.history.pushState({}, "", url.toString());

            // Trigger HTMX request
            htmx.ajax("GET", url.toString(), "#content");

            // Update UI immediately
            updateSortIndicators(sortColumn, newDir);
        });
    });

    // Set initial sort indicators based on current URL
    const currentSort = new URLSearchParams(window.location.search).get(
        "sort_by",
    );
    const currentDir =
        new URLSearchParams(window.location.search).get("sort_dir") || "asc";

    if (currentSort) {
        updateSortIndicators(currentSort, currentDir);
    }
}

function updateSortIndicators(sortColumn, sortDir) {
    // Remove all active indicators
    document.querySelectorAll(".vouchers-table th.sortable").forEach((th) => {
        th.classList.remove("sorted", "sorted-asc", "sorted-desc");
        const icon = th.querySelector(".sort-icon");
        if (icon) {
            icon.classList.remove("bi-caret-up-fill", "bi-caret-down-fill");
            icon.classList.add("bi-caret-down-fill");
        }
    });

    // Add indicator to current sort column
    const activeHeader = document.querySelector(
        `.vouchers-table th.sortable[data-sort-column="${sortColumn}"]`,
    );
    if (activeHeader) {
        activeHeader.classList.add("sorted");
        activeHeader.classList.add(
            sortDir === "asc" ? "sorted-asc" : "sorted-desc",
        );

        const icon = activeHeader.querySelector(".sort-icon");
        if (icon) {
            icon.classList.remove("bi-caret-up-fill", "bi-caret-down-fill");
            icon.classList.add(
                sortDir === "asc" ? "bi-caret-up-fill" : "bi-caret-down-fill",
            );
        }
    }
}
