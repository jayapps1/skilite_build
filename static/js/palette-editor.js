"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const preview = document.querySelector(
        "#live-business-preview"
    );

    const categorySelect = document.querySelector(
        "#id_business_category"
    );

    const contentElement = document.querySelector(
        "#business-preview-content"
    );

    const roleVariableMap = {
        PRIMARY: "--preview-primary",
        SECONDARY: "--preview-secondary",
        ACCENT: "--preview-accent",
        BACKGROUND: "--preview-background",
        SURFACE: "--preview-surface",
        HEADING: "--preview-heading",
        BODY_TEXT: "--preview-body-text",
        MUTED_TEXT: "--preview-muted-text",
        BORDER: "--preview-border",
        SUCCESS: "--preview-success",
        WARNING: "--preview-warning",
        DANGER: "--preview-danger",
        INFO: "--preview-info",
    };

    const isValidHex = (value) => {
        return /^#[0-9A-F]{6}([0-9A-F]{2})?$/.test(
            value
        );
    };

    const normalizeHex = (value) => {
        let normalized = value.trim().toUpperCase();

        if (
            normalized !== ""
            && !normalized.startsWith("#")
        ) {
            normalized = `#${normalized}`;
        }

        return normalized;
    };

    const applyHexToPreview = (input) => {
        if (!preview) {
            return;
        }

        const role = input.dataset.colorRole;
        const variableName = roleVariableMap[role];
        const value = normalizeHex(input.value);

        input.value = value;

        if (variableName && isValidHex(value)) {
            preview.style.setProperty(
                variableName,
                value
            );

            input.classList.remove("is-invalid");
        } else {
            input.classList.add("is-invalid");
        }
    };

    document.querySelectorAll(".hex-input").forEach(
        (input) => {
            input.addEventListener("input", () => {
                applyHexToPreview(input);

                const picker = document.querySelector(
                    `.visual-colour-picker[data-target="${input.id}"]`
                );

                if (
                    picker
                    && isValidHex(input.value)
                ) {
                    picker.value = input.value.slice(0, 7);
                }
            });

            input.addEventListener("blur", () => {
                applyHexToPreview(input);
            });

            applyHexToPreview(input);
        }
    );

    document.querySelectorAll(
        ".visual-colour-picker"
    ).forEach((picker) => {
        picker.addEventListener("input", () => {
            const target = document.getElementById(
                picker.dataset.target
            );

            if (!target) {
                return;
            }

            target.value = picker.value.toUpperCase();

            applyHexToPreview(target);
        });
    });

    document.querySelectorAll(
        ".copy-hex-button"
    ).forEach((button) => {
        button.addEventListener("click", async () => {
            const target = document.getElementById(
                button.dataset.copyTarget
            );

            if (!target) {
                return;
            }

            try {
                await navigator.clipboard.writeText(
                    target.value
                );

                const icon = button.querySelector("i");

                if (icon) {
                    icon.className = "fa-solid fa-check";

                    window.setTimeout(() => {
                        icon.className =
                            "fa-regular fa-copy";
                    }, 1200);
                }
            } catch (error) {
                target.select();
            }
        });
    });

    let businessContent = {};

    if (contentElement) {
        businessContent = JSON.parse(
            contentElement.textContent
        );
    }

    const applyBusinessContent = () => {
        const selectedCategory = (
            categorySelect
            ? categorySelect.value
            : ""
        );

        const content = (
            businessContent[selectedCategory]
            || businessContent.default
        );

        if (!content) {
            return;
        }

        const brand = document.querySelector(
            "#preview-brand"
        );

        const kicker = document.querySelector(
            "#preview-kicker"
        );

        const headline = document.querySelector(
            "#preview-headline"
        );

        const description = document.querySelector(
            "#preview-description"
        );

        if (brand) {
            brand.textContent = content.brand;
        }

        if (kicker) {
            kicker.textContent = content.kicker;
        }

        if (headline) {
            headline.textContent = content.headline;
        }

        if (description) {
            description.textContent = content.description;
        }

        document.querySelectorAll(
            "[data-preview-service]"
        ).forEach((element) => {
            const index = Number(
                element.dataset.previewService
            );

            if (content.services[index]) {
                element.textContent = (
                    content.services[index]
                );
            }
        });
    };

    if (categorySelect) {
        categorySelect.addEventListener(
            "change",
            applyBusinessContent
        );
    }

    applyBusinessContent();
});