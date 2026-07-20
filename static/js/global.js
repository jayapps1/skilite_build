"use strict";

/**
 * Skilite Build global JavaScript.
 *
 * JavaScript used across the whole website belongs here.
 * Feature-specific code should use separate JavaScript files.
 */

document.addEventListener("DOMContentLoaded", () => {
    initializeBootstrapTooltips();
    initializeBootstrapPopovers();
    initializeAutoDismissAlerts();
});


/**
 * Activates all Bootstrap tooltips.
 */
function initializeBootstrapTooltips() {
    if (
        typeof bootstrap === "undefined" ||
        typeof bootstrap.Tooltip === "undefined"
    ) {
        return;
    }

    const tooltipElements = document.querySelectorAll(
        '[data-bs-toggle="tooltip"]'
    );

    tooltipElements.forEach((element) => {
        bootstrap.Tooltip.getOrCreateInstance(element);
    });
}


/**
 * Activates all Bootstrap popovers.
 */
function initializeBootstrapPopovers() {
    if (
        typeof bootstrap === "undefined" ||
        typeof bootstrap.Popover === "undefined"
    ) {
        return;
    }

    const popoverElements = document.querySelectorAll(
        '[data-bs-toggle="popover"]'
    );

    popoverElements.forEach((element) => {
        bootstrap.Popover.getOrCreateInstance(element);
    });
}


/**
 * Automatically dismisses notification messages that
 * contain the data-auto-dismiss attribute.
 */
function initializeAutoDismissAlerts() {
    if (
        typeof bootstrap === "undefined" ||
        typeof bootstrap.Alert === "undefined"
    ) {
        return;
    }

    const alertElements = document.querySelectorAll(
        ".alert[data-auto-dismiss]"
    );

    alertElements.forEach((alertElement) => {
        const delay = Number(
            alertElement.dataset.autoDismiss || 5000
        );

        window.setTimeout(() => {
            const alertInstance =
                bootstrap.Alert.getOrCreateInstance(alertElement);

            alertInstance.close();
        }, delay);
    });
}