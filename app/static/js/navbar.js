function cancelSearch(searchInputId, cancelBtnId) {
    const cancelButton = document.getElementById(cancelBtnId);
    const searchInput = document.getElementById(searchInputId);

    // If either element is missing, do nothing silently
    if (!cancelButton || !searchInput) return;

    cancelButton.style.display = "none";

    searchInput.addEventListener("input", (event) => {
        const inputValue = event.target.value;

        if (inputValue.length > 0) {
            cancelButton.style.display = "block";
        } else {
            cancelButton.style.display = "none";
        }
    });

    cancelButton.addEventListener("mousedown", (event) => {
        event.preventDefault(); // Prevent button from stealing focus
        cancelButton.style.display = "none";
        searchInput.value = "";
        searchInput.focus();
    });
}

cancelSearch("searchInput", "cancelBtn");
