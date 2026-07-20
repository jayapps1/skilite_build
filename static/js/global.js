"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const navbar = document.querySelector(
        "#skilite-navbar"
    );

    const updateNavbarState = () => {
        if (!navbar) {
            return;
        }

        navbar.classList.toggle(
            "navbar-scrolled",
            window.scrollY > 20
        );
    };

    window.addEventListener(
        "scroll",
        updateNavbarState,
        {
            passive: true,
        }
    );

    updateNavbarState();

    const navigationCollapse = document.querySelector(
        "#main-navigation"
    );

    if (navigationCollapse) {
        navigationCollapse
            .querySelectorAll("a.nav-link")
            .forEach((link) => {
                link.addEventListener("click", () => {
                    if (
                        window.innerWidth >= 992
                        || !navigationCollapse.classList.contains(
                            "show"
                        )
                    ) {
                        return;
                    }

                    const collapseInstance =
                        bootstrap.Collapse.getOrCreateInstance(
                            navigationCollapse
                        );

                    collapseInstance.hide();
                });
            });
    }

    window.setTimeout(() => {
        document
            .querySelectorAll(
                ".skilite-message-container .alert"
            )
            .forEach((alertElement) => {
                const alertInstance =
                    bootstrap.Alert.getOrCreateInstance(
                        alertElement
                    );

                alertInstance.close();
            });
    }, 6000);
});