function cancelSearch(searchInputId, cancelBtnId) {
    const cancelButton = document.getElementById(cancelBtnId);
    const searchInput = document.getElementById(searchInputId);

    cancelButton.style.display = "none";

    searchInput.addEventListener("input", (event) => {
        const inputValue = event.target.value;

        if (inputValue.length > 0) {
            console.log("There is at least one character typed!");
            cancelButton.style.display = "block";
        } else {
            cancelButton.style.display = "none";
        }
    });

    cancelButton.addEventListener("mousedown", (event) => {
        event.preventDefault(); // Prevent button from stealing focus
        console.log("Cancel button is clicked");
        cancelButton.style.display = "none";
        searchInput.value = "";
        searchInput.focus();
    });
}

cancelSearch("searchInput", "cancelBtn");
