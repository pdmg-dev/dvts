document.addEventListener("DOMContentLoaded", function () {
    closeVoucherCard();
});

document.addEventListener("htmx:afterSwap", function () {
    // Check if the swapped content is the new voucher card
    closeVoucherCard();
});

// For closing the new voucher card
function closeVoucherCard() {
    const closeBtn = document.getElementById("closeVoucherCard");
    if (closeBtn) {
        // Remove existing listeners by cloning and replacing
        const newCloseBtn = closeBtn.cloneNode(true);
        closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);

        newCloseBtn.addEventListener("click", function (e) {
            e.preventDefault();
            const container = document.getElementById("floatingCardContainer");
            container.innerHTML = "";
            history.pushState({}, "", "/vouchers");
        });
    }
}

document.addEventListener("DOMContentLoaded", function () {
    initCategoryDropdown();
});

document.addEventListener("htmx:afterSwap", function (evt) {
    if (evt.detail.target.id === "voucherFormContainer") {
        initCategoryDropdown();
    }
});

function initCategoryDropdown() {
    const input = document.getElementById("categoryInput");
    const menu = document.getElementById("categoryMenu");
    const hidden = document.getElementById("category");

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

    // Handle selecting an option
    document.querySelectorAll(".category-option").forEach((item) => {
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
