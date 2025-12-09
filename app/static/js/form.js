// Initialize dropdowns immediately when script loads
initCategoryDropdown();
initRespCenterDropdown();

// Also initialize after HTMX swaps
document.addEventListener("htmx:afterSwap", function (evt) {
    if (evt.detail.target.id === "voucherFormContainer") {
        initCategoryDropdown();
        initRespCenterDropdown();
    }
});

// Fallback: Also listen for DOM content loaded
document.addEventListener("DOMContentLoaded", function () {
    initCategoryDropdown();
    initRespCenterDropdown();
});

function initCategoryDropdown() {
    const input = document.getElementById("categoryInput");
    const menu = document.getElementById("categoryMenu");
    const hidden = document.getElementById("category");

    // Guard against missing elements
    if (!input || !menu || !hidden) return;

    let dropdown = new bootstrap.Dropdown(input);

    input.addEventListener("click", () => dropdown.show());

    // When typing
    input.addEventListener("input", () => {
        const text = input.value;

        // If only spaces or empty → hide dropdown
        if (text.trim() === "") {
            dropdown.hide();
            showAllOptions(); // restore full list for next time
            return;
        }

        dropdown.show();
        filterOptions(text);
    });

    // Restore all options (used when cleared)
    function showAllOptions() {
        menu.querySelectorAll("li").forEach(
            (li) => (li.style.display = "block"),
        );
    }

    function filterOptions(searchText) {
        const items = menu.querySelectorAll(".category-option");
        const text = searchText.toLowerCase().trim();
        let matchCount = 0;

        items.forEach((item) => {
            const label = item.innerText.toLowerCase();
            const isMatch = label.includes(text);

            item.parentElement.style.display = isMatch ? "block" : "none";

            if (isMatch) matchCount++;
        });

        // No match = hide
        if (matchCount === 0) dropdown.hide();
        else dropdown.show();
    }

    // Handle selecting an option - use event delegation on menu
    menu.querySelectorAll(".category-option").forEach((item) => {
        item.addEventListener("click", function (e) {
            e.preventDefault();

            const value = this.dataset.value;
            const label = this.innerText.trim();

            hidden.value = value;
            input.value = label;

            dropdown.hide();
        });
    });
}

function initRespCenterDropdown() {
    const input = document.getElementById("respCenterInput");
    const menu = document.getElementById("respCenterMenu");
    const hidden = document.getElementById("respCenterId");

    // Guard against missing elements
    if (!input || !menu || !hidden) return;

    let dropdown = new bootstrap.Dropdown(input);

    input.addEventListener("click", () => dropdown.show());

    // When typing
    input.addEventListener("input", () => {
        const text = input.value;

        // If only spaces or empty → hide dropdown
        if (text.trim() === "") {
            dropdown.hide();
            showAllOptions(); // restore full list for next time
            return;
        }

        dropdown.show();
        filterOptions(text);
    });

    // Restore all options (used when cleared)
    function showAllOptions() {
        menu.querySelectorAll("li").forEach(
            (li) => (li.style.display = "block"),
        );
    }

    function filterOptions(searchText) {
        const items = menu.querySelectorAll(".resp-center-option");
        const text = searchText.toLowerCase().trim();
        let matchCount = 0;

        items.forEach((item) => {
            const label = item.innerText.toLowerCase();
            const code = (item.dataset.code || "").toLowerCase();
            const acronym = (item.dataset.acronym || "").toLowerCase();
            const isMatch =
                label.includes(text) ||
                code.includes(text) ||
                acronym.includes(text);

            item.parentElement.style.display = isMatch ? "block" : "none";

            if (isMatch) matchCount++;
        });

        // No match = hide
        if (matchCount === 0) dropdown.hide();
        else dropdown.show();
    }

    // Handle selecting an option - use event delegation on menu
    menu.querySelectorAll(".resp-center-option").forEach((item) => {
        item.addEventListener("click", function (e) {
            e.preventDefault();

            const value = this.dataset.value;
            const label = this.innerText.trim();

            hidden.value = value;
            input.value = label;

            dropdown.hide();
        });
    });
}
