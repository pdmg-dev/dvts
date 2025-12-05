function initTempusDominus() {
    const datePicker = document.getElementById("dateReceivedPicker");

    if (!datePicker || datePicker.dataset.initialized === "true") {
        return;
    }

    new tempusDominus.TempusDominus(datePicker, {
        localization: {
            locale: "en",
            format: "yyyy-MM-dd HH:mm",
        },
        display: {
            viewMode: "calendar",
            theme: "light",
            keyboardNavigation: true,
            icons: {
                type: "icons",
                time: "bi bi-clock",
                date: "bi bi-calendar-week",
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
                close: true,
            },
            components: {
                calendar: true,
                date: true,
                month: true,
                year: true,
                decades: false,
                clock: true,
                hours: true,
                minutes: true,
                seconds: false,
            },
        },
    });

    datePicker.dataset.initialized = "true";
}

document.addEventListener("DOMContentLoaded", initTempusDominus);
document.addEventListener("htmx:afterSettle", initTempusDominus);
