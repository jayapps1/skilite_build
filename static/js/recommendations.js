"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const preferredSelect = document.querySelector(
        "#id_preferred_color_family"
    );

    const avoidedSelect = document.querySelector(
        "#id_avoided_color_families"
    );

    if (!preferredSelect || !avoidedSelect) {
        return;
    }

    const synchronizeColourOptions = () => {
        const preferredValue = preferredSelect.value;

        Array.from(avoidedSelect.options).forEach((option) => {
            option.disabled = (
                preferredValue !== ""
                && option.value === preferredValue
            );

            if (option.disabled) {
                option.selected = false;
            }
        });
    };

    preferredSelect.addEventListener(
        "change",
        synchronizeColourOptions
    );

    synchronizeColourOptions();
});