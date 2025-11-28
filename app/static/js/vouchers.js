// Select All
function selectAllBehavior(seletAllId, vouchersTableId) {
    const selectAllBtn = document.getElementById(seletAllId);
    const checkbox = selectAllBtn.querySelector('input[type="checkbox"]');

    const tableSelectButtons = document
        .getElementById(vouchersTableId)
        .querySelectorAll("button");
    const tableCheckboxes = document
        .getElementById(vouchersTableId)
        .querySelectorAll('input[type="checkbox"]');

    // Toggle select all
    selectAllBtn.addEventListener("click", (e) => {
        if (e.target !== checkbox) {
            checkbox.checked = !checkbox.checked;
            checkbox.dispatchEvent(new Event("change", { bubbles: true }));
        }
    });

    // Select all / unselect all
    checkbox.addEventListener("change", () => {
        if (checkbox.checked) {
            tableCheckboxes.forEach((cb) => {
                cb.checked = true;
            });
        } else {
            tableCheckboxes.forEach((cb) => {
                cb.checked = false;
            });
        }
    });

    tableSelectButtons.forEach((btn) => {
        const cb = btn.querySelector('input[type="checkbox"]');
        // Mark a table checkbox if its button is clicked
        btn.addEventListener("click", (e) => {
            if (e.target !== cb) {
                cb.checked = !cb.checked;
                cb.dispatchEvent(new Event("change", { bubbles: true }));
            }
        });
        // Mark the select all checkbox if at least one table checkbox is checked
        cb.addEventListener("change", () => {
            const anyChecked = Array.from(tableCheckboxes).some(
                (c) => c.checked,
            );
            checkbox.checked = anyChecked;
        });
    });
}
selectAllBehavior("selectAll", "vouchersTable");

// Split Layout
function splitLayout(split, splitWrapperSelector, detailPanelSelector) {
    const splitBtn = document.querySelector(split);
    const splitWrapper = document.querySelector(splitWrapperSelector);
    const detailPanel = document.querySelector(detailPanelSelector);
    const tableBody = document.querySelector("#vouchersTable tbody");

    splitBtn.addEventListener("click", () => {
        const active = splitWrapper.classList.toggle("split-active");
        splitBtn.classList.toggle("active", active);

        if (!active) {
            // Clear immediately when toggling back
            detailPanel.innerHTML = "";
        }
    });

    // Listen for the end of the transition/animation
    splitWrapper.addEventListener("transitionend", () => {
        if (splitWrapper.classList.contains("split-active")) {
            detailPanel.innerHTML = `
        <div class="text-center mt-5">
          <span>Select a row to view details</span>
        </div>
      `;
        }
    });

    // Event delegation: listen once on tbody
    tableBody.addEventListener("click", (e) => {
        const row = e.target.closest("tr");
        if (!row) return;

        // Only respond if split layout is active
        if (splitWrapper.classList.contains("split-active")) {
            const col1 = row.children[0].innerText.trim();
            const col2 = row.children[1].innerText.trim();
            const col3 = row.children[2].innerText.trim();

            detailPanel.innerHTML = `
        <h4 class="mb-3">Row Details</h4>
        <p><strong>Column 1:</strong> ${col1}</p>
        <p><strong>Column 2:</strong> ${col2}</p>
        <p><strong>Column 3:</strong> ${col3}</p>
      `;
        }
    });
}

splitLayout(".split", ".table-split-wrapper", ".detail-panel");

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

document.body.addEventListener("htmx:afterSwap", function (evt) {
    selectAllBehavior("selectAll", "vouchersTable");
    splitLayout(".split", ".table-split-wrapper", ".detail-panel");
    scrollTable(".table-container", ".toolbar");
});
