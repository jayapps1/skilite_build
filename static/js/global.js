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

    // Night Mode (Dark/Light Theme) Toggler
    const themeToggleBtn = document.querySelector("#theme-toggle-btn");
    const themeToggleIcon = document.querySelector("#theme-toggle-icon");

    if (themeToggleBtn && themeToggleIcon) {
        const updateToggleIcon = (theme) => {
            if (theme === "dark") {
                themeToggleIcon.classList.remove("fa-moon");
                themeToggleIcon.classList.add("fa-sun");
            } else {
                themeToggleIcon.classList.remove("fa-sun");
                themeToggleIcon.classList.add("fa-moon");
            }
        };

        const currentTheme = document.documentElement.getAttribute("data-bs-theme") || "light";
        updateToggleIcon(currentTheme);

        themeToggleBtn.addEventListener("click", () => {
            const activeTheme = document.documentElement.getAttribute("data-bs-theme") || "light";
            const newTheme = activeTheme === "dark" ? "light" : "dark";

            document.documentElement.setAttribute("data-bs-theme", newTheme);
            localStorage.setItem("theme", newTheme);
            updateToggleIcon(newTheme);
        });
    }
});