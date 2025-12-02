initRemoveFile();

// For closing the new voucher card
document
    .getElementById("closeVoucherCard")
    .addEventListener("click", function () {
        document.getElementById("newVoucherCard").remove();
        history.pushState({}, "", "/vouchers");
    });

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
