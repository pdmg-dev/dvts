document.addEventListener("DOMContentLoaded", function () {
    initRemoveFile();
    closeVoucherCard();
});

document.addEventListener("htmx:afterSwap", function () {
    // Check if the swapped content is the new voucher card
    initRemoveFile();
    closeVoucherCard();
});

// For closing the new voucher card
function closeVoucherCard() {
    document
        .getElementById("closeVoucherCard")
        .addEventListener("click", function () {
            document.getElementById("newVoucherCard").remove();
            history.pushState({}, "", "/vouchers");
        });
}

function initRemoveFile() {
    const attachment = document.getElementById("attachment");
    const inputGroup = attachment.parentElement; // assuming it's inside .input-group

    attachment.addEventListener("input", (event) => {
        const inputValue = event.target.value;

        // If a file is chosen and button doesn't exist yet
        if (inputValue.length > 0 && !document.getElementById("removeFile")) {
            attachment.classList.add("has-file");
            const removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.id = "removeFile";
            removeBtn.className = "btn btn-outline-secondary btn-sm";
            removeBtn.innerHTML = '<i class="bi bi-x"></i>';

            // Insert after the file input
            inputGroup.appendChild(removeBtn);

            // Add click handler
            removeBtn.addEventListener("click", (event) => {
                event.preventDefault();
                attachment.classList.remove("has-file");
                attachment.value = ""; // clears the chosen file
                removeBtn.remove(); // remove the button itself
            });
        }
    });
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
