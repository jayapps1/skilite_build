"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const preview = document.querySelector("#live-business-preview");
    const categorySelect = document.querySelector("#id_business_category");
    const contentElement = document.querySelector("#business-preview-content");
    const autoGenCheckbox = document.querySelector("#auto-generate-colors");

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
        return /^#[0-9A-F]{6}([0-9A-F]{2})?$/.test(value);
    };

    const normalizeHex = (value) => {
        let normalized = value.trim().toUpperCase();
        if (normalized !== "" && !normalized.startsWith("#")) {
            normalized = `#${normalized}`;
        }
        return normalized;
    };

    // Calculate background luminance
    const getLuminance = (hex) => {
        hex = hex.replace("#", "");
        if (hex.length === 3) {
            hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
        }
        if (hex.length !== 6) return 1.0;
        const r = parseInt(hex.substring(0, 2), 16) / 255;
        const g = parseInt(hex.substring(2, 4), 16) / 255;
        const b = parseInt(hex.substring(4, 6), 16) / 255;

        const a = [r, g, b].map(v => {
            return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
        });
        return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
    };

    // Auto generate remaining colors if checked
    const runAutoGeneration = (triggerInput) => {
        if (!autoGenCheckbox || !autoGenCheckbox.checked) {
            return;
        }

        const bgInput = document.querySelector('input.hex-input[data-color-role="BACKGROUND"]');
        if (!bgInput) return;

        const bgHex = bgInput.value;
        if (!isValidHex(bgHex)) return;

        const lum = getLuminance(bgHex);
        let updates = {};

        if (lum > 0.5) {
            // Light Background
            updates = {
                SURFACE: "#FFFFFF",
                HEADING: "#0F172A",
                BODY_TEXT: "#334155",
                MUTED_TEXT: "#64748B",
                BORDER: "#E2E8F0",
            };
        } else {
            // Dark Background
            updates = {
                SURFACE: "#1E293B",
                HEADING: "#F8FAFC",
                BODY_TEXT: "#CBD5E1",
                MUTED_TEXT: "#94A3B8",
                BORDER: "#334155",
            };
        }

        // Standard helpers
        updates["SUCCESS"] = "#16A34A";
        updates["WARNING"] = "#EA580C";
        updates["DANGER"] = "#DC2626";
        updates["INFO"] = "#0284C7";

        // Apply generated values to non-active inputs to avoid cursor fighting
        Object.keys(updates).forEach(role => {
            const input = document.querySelector(`input.hex-input[data-color-role="${role}"]`);
            if (input && input !== document.activeElement) {
                const hexVal = updates[role];
                input.value = hexVal;
                
                // Update color picker
                const picker = document.querySelector(`.visual-colour-picker[data-target="${input.id}"]`);
                if (picker) {
                    picker.value = hexVal;
                }
                
                // Apply value to preview styles
                const cssVar = roleVariableMap[role];
                if (preview && cssVar) {
                    preview.style.setProperty(cssVar, hexVal);
                }
            }
        });
    };

    // Recalculate and apply UI Style mappings
    const applyStyleMappings = () => {
        if (!preview) return;

        document.querySelectorAll(".ui-color-mapper").forEach(select => {
            const cssVar = select.dataset.cssVar;
            const targetRole = select.value;
            const targetInput = document.querySelector(`input.hex-input[data-color-role="${targetRole}"]`);
            
            if (targetInput && isValidHex(targetInput.value)) {
                preview.style.setProperty(cssVar, targetInput.value);
            }
        });
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
            preview.style.setProperty(variableName, value);
            input.classList.remove("is-invalid");
            
            // Recalculate mappings in case this color is mapped to a UI component
            applyStyleMappings();
        } else {
            input.classList.add("is-invalid");
        }
    };

    // Initialize/Bind inputs
    document.querySelectorAll(".hex-input").forEach((input) => {
        input.addEventListener("input", () => {
            applyHexToPreview(input);

            // Handle auto generation triggers
            if (["BACKGROUND", "PRIMARY", "SECONDARY", "ACCENT"].includes(input.dataset.colorRole)) {
                runAutoGeneration(input);
            }

            const picker = document.querySelector(`.visual-colour-picker[data-target="${input.id}"]`);
            if (picker && isValidHex(input.value)) {
                picker.value = input.value.slice(0, 7);
            }
        });

        input.addEventListener("blur", () => {
            applyHexToPreview(input);
        });

        applyHexToPreview(input);
    });

    document.querySelectorAll(".visual-colour-picker").forEach((picker) => {
        picker.addEventListener("input", () => {
            const target = document.getElementById(picker.dataset.target);
            if (!target) return;

            target.value = picker.value.toUpperCase();
            applyHexToPreview(target);

            // Handle auto generation triggers
            if (["BACKGROUND", "PRIMARY", "SECONDARY", "ACCENT"].includes(target.dataset.colorRole)) {
                runAutoGeneration(target);
            }
        });
    });

    // Mappers change listeners
    document.querySelectorAll(".ui-color-mapper").forEach(select => {
        select.addEventListener("change", applyStyleMappings);
    });

    // Clipboard copy buttons
    document.querySelectorAll(".copy-hex-button").forEach((button) => {
        button.addEventListener("click", async () => {
            const target = document.getElementById(button.dataset.copyTarget);
            if (!target) return;

            try {
                await navigator.clipboard.writeText(target.value);
                const icon = button.querySelector("i");
                if (icon) {
                    icon.className = "fa-solid fa-check";
                    window.setTimeout(() => {
                        icon.className = "fa-regular fa-copy";
                    }, 1200);
                }
            } catch (error) {
                target.select();
            }
        });
    });

    let businessContent = {};
    if (contentElement) {
        businessContent = JSON.parse(contentElement.textContent);
    }

    const applyBusinessContent = () => {
        const selectedCategory = categorySelect ? categorySelect.value : "";
        const content = businessContent[selectedCategory] || businessContent.default;

        if (!content) return;

        const brand = document.querySelector("#preview-brand");
        const kicker = document.querySelector("#preview-kicker");
        const headline = document.querySelector("#preview-headline");
        const description = document.querySelector("#preview-description");

        if (brand) brand.textContent = content.brand;
        if (kicker) kicker.textContent = content.kicker;
        if (headline) headline.textContent = content.headline;
        if (description) description.textContent = content.description;

        document.querySelectorAll("[data-preview-service]").forEach((element) => {
            const index = Number(element.dataset.previewService);
            if (content.services[index]) {
                element.textContent = content.services[index];
            }
        });

        const categoryDetails = {
            technology: {
                aboutKicker: "Innovating the future",
                aboutHeadline: "About NovaTech Solutions",
                aboutDescription: "We provide custom software, cloud architectures, and robust cybersecurity designed to scale and optimize your operation.",
                contactEmail: "info@novatech.com",
                primaryBtn: "Start Free Trial",
                secondaryBtn: "Book a Demo",
                serviceIcons: ["fa-solid fa-cloud", "fa-solid fa-code", "fa-solid fa-shield-halved"],
                serviceDescs: [
                    "Highly scalable cloud database and compute infrastructure.",
                    "Developer friendly REST and GraphQL APIs with full docs.",
                    "Advanced threat prevention and end-to-end encryption."
                ]
            },
            finance: {
                aboutKicker: "Securing wealth since 2012",
                aboutHeadline: "About TrustCapital",
                aboutDescription: "We offer expert investment strategies, trust planning, and business banking to secure your assets and scale your wealth.",
                contactEmail: "advisors@trustcapital.com",
                primaryBtn: "Open Account",
                secondaryBtn: "Contact Advisor",
                serviceIcons: ["fa-solid fa-vault", "fa-solid fa-chart-pie", "fa-solid fa-shield-heart"],
                serviceDescs: [
                    "High-yield savings plans and secure corporate vaults.",
                    "Intelligent, automated portfolio optimization services.",
                    "Comprehensive risk mitigation and liability insurance."
                ]
            },
            "restaurant-food": {
                aboutKicker: "Taste the tradition",
                aboutHeadline: "About Savory Kitchen",
                aboutDescription: "Our culinary team prepares authentic dishes using farm-fresh organic ingredients, offering full-service dining and prompt home deliveries.",
                contactEmail: "chef@savorykitchen.com",
                primaryBtn: "Book a Table",
                secondaryBtn: "View Menu",
                serviceIcons: ["fa-solid fa-utensils", "fa-solid fa-truck-fast", "fa-solid fa-champagne-glasses"],
                serviceDescs: [
                    "Gourmet dining created by world class chefs.",
                    "Lightning fast delivery bringing hot fresh food to your door.",
                    "High end catering services for private events."
                ]
            },
            healthcare: {
                aboutKicker: "Putting patients first",
                aboutHeadline: "About CarePoint Health",
                aboutDescription: "We are a medical network providing preventive care, specialist consultations, and wellness support for patients and families.",
                contactEmail: "care@carepoint.com",
                primaryBtn: "Find a Doctor",
                secondaryBtn: "Schedule Appointment",
                serviceIcons: ["fa-solid fa-stethoscope", "fa-solid fa-heart-pulse", "fa-solid fa-user-doctor"],
                serviceDescs: [
                    "Comprehensive health screening and diagnoses.",
                    "24/7 telehealth consultations from the comfort of home.",
                    "Leading clinic specialists across oncology, pediatrics, and more."
                ]
            },
            education: {
                aboutKicker: "Shaping bright futures",
                aboutHeadline: "About BrightPath Academy",
                aboutDescription: "We offer custom online classes, professional certificate pathways, and student counseling designed for career advancement.",
                contactEmail: "admissions@brightpath.edu",
                primaryBtn: "Enroll Now",
                secondaryBtn: "Explore Courses",
                serviceIcons: ["fa-solid fa-graduation-cap", "fa-solid fa-book-open", "fa-solid fa-school"],
                serviceDescs: [
                    "Personal tutoring by experienced university lecturers.",
                    "Accredited professional certifications in tech and business.",
                    "Modern hybrid classrooms for flexible remote learning."
                ]
            },
            default: {
                aboutKicker: "Who we are",
                aboutHeadline: "About Our Business",
                aboutDescription: "We are a dedicated team of professionals committed to delivering outstanding solutions tailored to your unique business needs.",
                contactEmail: "info@business.com",
                primaryBtn: "Get started",
                secondaryBtn: "Learn more",
                serviceIcons: ["fa-solid fa-briefcase", "fa-solid fa-headset", "fa-solid fa-chart-line"],
                serviceDescs: [
                    "Reliable services designed around your requirements.",
                    "Helpful support for customers and business partners.",
                    "Practical solutions for growth and long-term success."
                ]
            }
        };

        const details = categoryDetails[selectedCategory] || categoryDetails.default;
        
        const aboutKicker = document.querySelector("#preview-about-kicker");
        const aboutHeadline = document.querySelector("#preview-about-headline");
        const aboutDescription = document.querySelector("#preview-about-description");
        const contactEmail = document.querySelector("#preview-contact-email");
        const primaryBtn = document.querySelector("#preview-primary-btn");
        const secondaryBtn = document.querySelector("#preview-secondary-btn");

        if (aboutKicker) aboutKicker.textContent = details.aboutKicker;
        if (aboutHeadline) aboutHeadline.textContent = details.aboutHeadline;
        if (aboutDescription) aboutDescription.textContent = details.aboutDescription;
        if (contactEmail) contactEmail.textContent = details.contactEmail;
        if (primaryBtn) primaryBtn.textContent = details.primaryBtn;
        if (secondaryBtn) secondaryBtn.textContent = details.secondaryBtn;

        for (let i = 0; i < 3; i++) {
            const iconEl = document.querySelector(`#preview-service-icon-${i}`);
            const descEl = document.querySelector(`#preview-service-desc-${i}`);
            
            if (iconEl && details.serviceIcons[i]) {
                iconEl.className = details.serviceIcons[i];
            }
            if (descEl && details.serviceDescs[i]) {
                descEl.textContent = details.serviceDescs[i];
            }
        }
    };

    if (categorySelect) {
        categorySelect.addEventListener("change", applyBusinessContent);
    }

    applyBusinessContent();

    // Tab switching for live preview
    const navLinks = document.querySelectorAll(".preview-nav-link, .footer-link-btn");
    const sections = document.querySelectorAll(".preview-section");

    navLinks.forEach(link => {
        link.addEventListener("click", () => {
            // Find target slug
            const target = link.dataset.target;

            // Update navbar active state
            document.querySelectorAll(".preview-nav-link").forEach(l => {
                if (l.dataset.target === target) {
                    l.classList.add("active");
                } else {
                    l.classList.remove("active");
                }
            });

            // Hide all sections
            sections.forEach(s => s.classList.add("d-none"));
            
            // Show target section
            const targetId = `preview-section-${target}`;
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.remove("d-none");
            }
        });
    });

    // Run initial auto generation and style mappings
    runAutoGeneration();
    applyStyleMappings();
});