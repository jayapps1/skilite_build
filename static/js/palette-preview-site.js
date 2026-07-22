"use strict";

(function() {
    // ------------------------------------------------------------------
    // Local Photographic Assets Resolver Module
    // ------------------------------------------------------------------
    const SkilitePreviewImages = {
        folderMap: {
            "technology": "technology",
            "finance": "finance",
            "restaurant-food": "restaurant",
            "healthcare": "healthcare",
            "education": "education",
            "beauty-cosmetics": "beauty",
            "construction": "construction",
            "logistics-transport": "logistics",
            "fashion": "fashion",
            "real-estate": "real-estate",
            "hospitality-tourism": "tourism",
            "agriculture": "agriculture",
            "corporate-services": "corporate",
            "nonprofit-ngo": "nonprofit",
            "default": "fallback"
        },

        resolve: function(category, type, index) {
            const folder = this.folderMap[category] || this.folderMap.default;
            const idx = parseInt(index) || 0;

            switch (type) {
                case "hero_desktop":
                    return `/static/images/previews/${folder}/hero_desktop.webp`;
                case "hero_mobile":
                    return `/static/images/previews/${folder}/hero_mobile.webp`;
                case "about":
                    return `/static/images/previews/${folder}/about.webp`;
                case "product":
                    return `/static/images/previews/${folder}/product_${(idx % 6) + 1}.webp`;
                case "gallery":
                    return `/static/images/previews/${folder}/gallery_${(idx % 3) + 1}.webp`;
                case "team":
                    return `/static/images/previews/${folder}/team_${(idx % 3) + 1}.webp`;
                case "testimonial":
                    return `/static/images/previews/${folder}/testimonial_${(idx % 3) + 1}.webp`;
                case "contact":
                case "location":
                    return `/static/images/previews/${folder}/contact.webp`;
                case "cta":
                    return `/static/images/previews/${folder}/cta.webp`;
                case "cover":
                    return `/static/images/previews/${folder}/cover.webp`;
                case "logo":
                    return `/static/images/previews/${folder}/logo.webp`;
                default:
                    return `/static/images/previews/fallback/hero_desktop.webp`;
            }
        },

        // Fast vector backup if local WebP file somehow fails
        fallbackSvg: function(type, category) {
            const colors = this.getColors();
            return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(`
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
                    <rect width="400" height="300" fill="${colors.background}"/>
                    <rect x="10" y="10" width="380" height="280" rx="6" fill="none" stroke="${colors.primary}" stroke-width="2" stroke-dasharray="6,4"/>
                    <circle cx="200" cy="130" r="40" fill="${colors.accent}" opacity="0.8"/>
                    <text x="200" y="210" font-family="sans-serif" font-size="14" fill="${colors.heading}" font-weight="bold" text-anchor="middle">
                        ${category.toUpperCase()} - ${type.toUpperCase()}
                    </text>
                </svg>
            `);
        },

        getColors: function() {
            const previewEl = document.getElementById("live-business-preview");
            const defaults = {
                primary: "#2563eb",
                background: "#f8fafc",
                surface: "#ffffff",
                heading: "#0f172a",
                accent: "#f59e0b"
            };
            if (!previewEl) return defaults;
            const style = getComputedStyle(previewEl);
            return {
                primary: style.getPropertyValue("--preview-primary").trim() || defaults.primary,
                background: style.getPropertyValue("--preview-background").trim() || defaults.background,
                surface: style.getPropertyValue("--preview-surface").trim() || defaults.surface,
                heading: style.getPropertyValue("--preview-heading").trim() || defaults.heading,
                accent: style.getPropertyValue("--preview-accent").trim() || defaults.accent
            };
        }
    };

    // ------------------------------------------------------------------
    // Live Preview Orchestrator Module
    // ------------------------------------------------------------------
    window.SkilitePreview = {
        init: function() {
            // Bind navigation links
            document.querySelectorAll(".preview-nav-link, .footer-link-btn").forEach(btn => {
                btn.addEventListener("click", (e) => {
                    e.preventDefault();
                    const target = btn.dataset.target || "home";
                    this.navigate(target);
                });
            });

            // Mobile Menu Toggle
            const mobileToggle = document.getElementById("preview-mobile-menu-btn");
            const navLinks = document.getElementById("preview-navigation-links");
            if (mobileToggle && navLinks) {
                mobileToggle.addEventListener("click", (e) => {
                    e.preventDefault();
                    navLinks.classList.toggle("mobile-open");
                });
            }

            // Resizer Toolbar buttons
            document.querySelectorAll(".resizer-btn").forEach(btn => {
                btn.addEventListener("click", (e) => {
                    e.preventDefault();
                    const device = btn.dataset.device;
                    this.setDevice(device);
                });
            });

            // Resizer Toolbar Actions
            const fullscreenBtn = document.getElementById("preview-action-fullscreen");
            if (fullscreenBtn) {
                fullscreenBtn.addEventListener("click", (e) => {
                    e.preventDefault();
                    this.toggleFullscreen();
                });
            }

            // Bind Escape key to exit fullscreen mode
            document.addEventListener("keydown", (e) => {
                if (e.key === "Escape") {
                    const shell = document.querySelector(".preview-container-shell");
                    if (shell && shell.classList.contains("fullscreen-active")) {
                        this.toggleFullscreen();
                    }
                }
            });

            const refreshBtn = document.getElementById("preview-action-refresh");
            if (refreshBtn) {
                refreshBtn.addEventListener("click", (e) => {
                    e.preventDefault();
                    this.refresh();
                });
            }

            const resetBtn = document.getElementById("preview-action-reset");
            if (resetBtn) {
                resetBtn.addEventListener("click", (e) => {
                    e.preventDefault();
                    this.navigate("home");
                    const previewMain = document.getElementById("live-business-preview");
                    if (previewMain) previewMain.scrollTop = 0;
                });
            }

            // Scroll Listener to transition transparent navbars to solid backgrounds
            const previewMain = document.getElementById("live-business-preview");
            if (previewMain) {
                previewMain.addEventListener("scroll", () => {
                    const navbarEl = document.getElementById("preview-navbar-element");
                    if (navbarEl) {
                        if (previewMain.scrollTop > 24) {
                            navbarEl.classList.add("navbar-scrolled");
                        } else {
                            navbarEl.classList.remove("navbar-scrolled");
                        }
                    }
                });
            }

            // Bind forms and links to prevent navigation
            document.querySelectorAll("#live-business-preview form").forEach(form => {
                form.addEventListener("submit", (e) => {
                    e.preventDefault();
                });
            });

            document.querySelectorAll("#live-business-preview a").forEach(a => {
                a.addEventListener("click", (e) => {
                    e.preventDefault();
                });
            });

            // Bind dropdowns changes
            const categorySelect = document.querySelector("#id_business_category");
            if (categorySelect) {
                categorySelect.addEventListener("change", () => {
                    this.setCategory(categorySelect.value);
                });
            }

            const themeSelect = document.querySelector("#id_theme_mode");
            if (themeSelect) {
                themeSelect.addEventListener("change", () => {
                    this.setTheme(themeSelect.value);
                });
            }

            // Initialize content
            this.refresh();

            // URL Query parameters overrides (useful for screenshot capturing and deep linking)
            const urlParams = new URLSearchParams(window.location.search);
            const categoryParam = urlParams.get('preview_category');
            const pageParam = urlParams.get('preview_page');
            const themeParam = urlParams.get('preview_theme');
            const deviceParam = urlParams.get('preview_device');

            if (categoryParam) {
                this.setCategory(categoryParam);
            }
            if (themeParam) {
                this.setTheme(themeParam);
            }
            if (deviceParam) {
                this.setDevice(deviceParam);
            }
            if (pageParam) {
                this.navigate(pageParam);
            }
        },

        navigate: function(pageName) {
            // Hide all pages
            document.querySelectorAll(".preview-section").forEach(sec => sec.classList.add("d-none"));
            
            // Show target page
            const targetSec = document.getElementById(`preview-section-${pageName}`);
            if (targetSec) {
                targetSec.classList.remove("d-none");
            }
            
            // Update active state in nav links
            document.querySelectorAll(".preview-nav-link").forEach(link => {
                if (link.dataset.target === pageName) {
                    link.classList.add("active");
                } else {
                    link.classList.remove("active");
                }
            });

            // Close mobile menu
            const navLinks = document.getElementById("preview-navigation-links");
            if (navLinks) {
                navLinks.classList.remove("mobile-open");
            }
        },

        DEVICE_WIDTHS: {
            desktop: 1200,
            tablet: 768,
            mobile: 390
        },

        setDevice: function(deviceName) {
            const previewElement = document.getElementById("live-business-preview");
            if (!previewElement) return;

            previewElement.classList.remove("device-desktop", "device-tablet", "device-mobile");
            previewElement.classList.add(`device-${deviceName}`);
            
            // Set inlineSize style matching DEVICE_WIDTHS source of truth
            if (deviceName === "desktop") {
                previewElement.style.width = "100%";
                previewElement.style.maxWidth = "1200px";
            } else {
                const targetWidth = this.DEVICE_WIDTHS[deviceName] || 390;
                previewElement.style.width = `${targetWidth}px`;
                previewElement.style.maxWidth = "100%";
            }

            // Auto-close open mobile menu links when switching devices
            const navLinks = document.getElementById("preview-navigation-links");
            if (navLinks) {
                navLinks.classList.remove("mobile-open");
            }

            // Update active class on buttons
            document.querySelectorAll(".resizer-btn").forEach(btn => {
                if (btn.dataset.device === deviceName) {
                    btn.classList.add("active");
                } else {
                    btn.classList.remove("active");
                }
            });
        },

        toggleFullscreen: function() {
            const shell = document.querySelector(".preview-container-shell");
            const fullscreenBtn = document.getElementById("preview-action-fullscreen");
            if (!shell) return;

            shell.classList.toggle("fullscreen-active");
            if (shell.classList.contains("fullscreen-active")) {
                if (fullscreenBtn) fullscreenBtn.innerHTML = '<i class="fa-solid fa-compress"></i> Exit';
            } else {
                if (fullscreenBtn) fullscreenBtn.innerHTML = '<i class="fa-solid fa-expand"></i> Fullscreen';
            }
        },

        getActiveCategory: function() {
            const categorySelect = document.querySelector("#id_business_category");
            if (categorySelect) {
                return categorySelect.value;
            }
            const previewEl = document.getElementById("live-business-preview");
            if (previewEl && previewEl.dataset.category) {
                return previewEl.dataset.category;
            }
            return "default";
        },

        updatePreviewImages: function(categorySlug) {
            const previewEl = document.getElementById("live-business-preview");
            if (!previewEl) return;

            const images = previewEl.querySelectorAll("img");
            images.forEach(img => {
                const type = img.dataset.type;
                if (!type) return;

                const index = img.dataset.index || 0;
                const localSrc = SkilitePreviewImages.resolve(categorySlug, type, index);

                // Safe fallback binder
                img.onerror = () => {
                    img.src = SkilitePreviewImages.fallbackSvg(type, categorySlug);
                    img.onerror = null; // prevent infinite loop
                };

                if (img.getAttribute("src") !== localSrc) {
                    img.setAttribute("src", localSrc);
                }
            });
        },

        setCategory: function(categorySlug) {
            const config = window.SkilitePreviewContent[categorySlug] || window.SkilitePreviewContent.default;
            if (!config) return;

            // Brand name updates
            const brandEl = document.getElementById("preview-brand");
            const footerBrandEl = document.getElementById("preview-footer-brand");
            if (brandEl) brandEl.textContent = config.brand;
            if (footerBrandEl) footerBrandEl.textContent = config.brand;

            // Hero section texts
            const kickerEl = document.getElementById("preview-kicker");
            const headlineEl = document.getElementById("preview-headline");
            const descEl = document.getElementById("preview-description");
            const primaryBtnEl = document.getElementById("preview-primary-btn");
            const secondaryBtnEl = document.getElementById("preview-secondary-btn");

            if (kickerEl) kickerEl.textContent = config.kicker;
            if (headlineEl) headlineEl.textContent = config.headline;
            if (descEl) descEl.textContent = config.description;
            if (primaryBtnEl) primaryBtnEl.textContent = config.primaryBtn;
            if (secondaryBtnEl) secondaryBtnEl.textContent = config.secondaryBtn;

            // Trust / Rating indicators
            const ratingEl = document.getElementById("preview-hero-rating");
            if (ratingEl && config.statNumber3) {
                ratingEl.textContent = typeof config.statNumber3 === "string" && config.statNumber3.includes("★") ? config.statNumber3.replace("★", "").trim() : "4.9";
            }

            // Key Statistics
            const statNum1 = document.getElementById("preview-stat-number-1");
            const statLbl1 = document.getElementById("preview-stat-label-1");
            const statNum2 = document.getElementById("preview-stat-number-2");
            const statLbl2 = document.getElementById("preview-stat-label-2");
            const statNum3 = document.getElementById("preview-stat-number-3");
            const statLbl3 = document.getElementById("preview-stat-label-3");

            if (statNum1) statNum1.textContent = config.statNumber1;
            if (statLbl1) statLbl1.textContent = config.statLabel1;
            if (statNum2) statNum2.textContent = config.statNumber2;
            if (statLbl2) statLbl2.textContent = config.statLabel2;
            if (statNum3) statNum3.textContent = config.statNumber3;
            if (statLbl3) statLbl3.textContent = config.statLabel3;

            // Testimonials
            const testTxt1 = document.getElementById("preview-testimonial-text-1");
            const testAut1 = document.getElementById("preview-testimonial-author-1");
            const testRol1 = document.getElementById("preview-testimonial-role-1");
            const testTxt2 = document.getElementById("preview-testimonial-text-2");
            const testAut2 = document.getElementById("preview-testimonial-author-2");
            const testRol2 = document.getElementById("preview-testimonial-role-2");
            const testTxt3 = document.getElementById("preview-testimonial-text-3");
            const testAut3 = document.getElementById("preview-testimonial-author-3");
            const testRol3 = document.getElementById("preview-testimonial-role-3");

            if (testTxt1) testTxt1.textContent = config.testimonialText1;
            if (testAut1) testAut1.textContent = config.testimonialAuthor1;
            if (testRol1) testRol1.textContent = config.testimonialRole1;
            if (testTxt2) testTxt2.textContent = config.testimonialText2;
            if (testAut2) testAut2.textContent = config.testimonialAuthor2;
            if (testRol2) testRol2.textContent = config.testimonialRole2;
            if (testTxt3 && config.testimonialText3) testTxt3.textContent = config.testimonialText3;
            if (testAut3 && config.testimonialAuthor3) testAut3.textContent = config.testimonialAuthor3;
            if (testRol3 && config.testimonialRole3) testRol3.textContent = config.testimonialRole3;

            // CTA Block
            const ctaTitle = document.getElementById("preview-cta-title");
            const ctaSubtitle = document.getElementById("preview-cta-subtitle");
            const ctaBtn = document.getElementById("preview-cta-btn");

            if (ctaTitle) ctaTitle.textContent = config.ctaTitle;
            if (ctaSubtitle) ctaSubtitle.textContent = config.ctaSubtitle;
            if (ctaBtn) ctaBtn.textContent = config.ctaBtn;

            // About Page Elements
            const aboutKicker = document.getElementById("preview-about-kicker");
            const aboutHeadline = document.getElementById("preview-about-headline");
            const aboutSub = document.getElementById("preview-about-sub");
            const aboutDesc = document.getElementById("preview-about-description");
            const aboutVision = document.getElementById("preview-about-vision");
            const aboutMission = document.getElementById("preview-about-mission");
            const valueTitle1 = document.getElementById("preview-value-title-1");
            const valueDesc1 = document.getElementById("preview-value-desc-1");
            const valueTitle2 = document.getElementById("preview-value-title-2");
            const valueDesc2 = document.getElementById("preview-value-desc-2");

            if (aboutKicker) aboutKicker.textContent = config.aboutKicker;
            if (aboutHeadline) aboutHeadline.textContent = config.aboutHeadline;
            if (aboutSub) aboutSub.textContent = config.aboutSub;
            if (aboutDesc) aboutDesc.textContent = config.aboutDescription;
            if (aboutVision) aboutVision.textContent = config.aboutVision;
            if (aboutMission) aboutMission.textContent = config.aboutMission;
            if (valueTitle1) valueTitle1.textContent = config.valueTitle1;
            if (valueDesc1) valueDesc1.textContent = config.valueDesc1;
            if (valueTitle2) valueTitle2.textContent = config.valueTitle2;
            if (valueDesc2) valueDesc2.textContent = config.valueDesc2;

            // Contact page elements
            const contactEmail = document.getElementById("preview-contact-email");
            const contactHours = document.getElementById("preview-contact-hours");
            const contactLoc = document.getElementById("preview-contact-loc");

            if (contactEmail) contactEmail.textContent = config.contactEmail;
            if (contactHours) contactHours.textContent = config.contactHours;
            if (contactLoc) contactLoc.textContent = config.contactLoc;

            // Profile page elements
            const profileName = document.getElementById("preview-profile-name");
            const profileLoc = document.getElementById("preview-profile-loc");
            const certLabel1 = document.getElementById("preview-cert-label-1");
            const certLabel2 = document.getElementById("preview-cert-label-2");
            
            if (profileName) profileName.textContent = config.brand;
            if (profileLoc) profileLoc.textContent = config.contactLoc;
            if (certLabel1) certLabel1.textContent = config.profileCert1;
            if (certLabel2) certLabel2.textContent = config.profileCert2;

            // Profile Avatar Initials
            const profileAvatar = document.getElementById("preview-profile-avatar");
            if (profileAvatar) {
                const words = config.brand.split(" ");
                const initials = words.map(w => w[0]).join("").substring(0, 2).toUpperCase();
                profileAvatar.textContent = initials;
            }

            // Features list template compilation
            const featuresContainers = document.querySelectorAll('[id="preview-features-container"]');
            featuresContainers.forEach(featuresContainer => {
                if (featuresContainer && config.features) {
                    featuresContainer.innerHTML = "";
                    config.features.forEach((feat, index) => {
                        const card = document.createElement("div");
                        card.className = "col-md-6 col-lg-4";
                        card.innerHTML = `
                            <div class="p-3 rounded preview-card-element h-100 text-start d-flex flex-column justify-content-between border shadow-sm" style="border-color: var(--preview-border) !important;">
                                <div>
                                    <div class="preview-product-image-wrapper mb-3 rounded overflow-hidden shadow-sm" style="height: 140px; border: 1px solid var(--preview-border);">
                                        <img class="preview-product-img w-100 h-100" data-type="product" data-index="${index}" alt="${feat.title}" style="object-fit: cover;">
                                    </div>
                                    <div class="d-flex justify-content-between align-items-start mb-2.5">
                                        <div class="preview-icon rounded-circle d-flex align-items-center justify-content-center" style="width: 34px; height: 34px; background: rgba(0,0,0,0.03); color: var(--preview-primary);">
                                            <i class="${feat.icon}"></i>
                                        </div>
                                        <span class="badge ${feat.statusClass} px-2.5 py-1 text-uppercase font-monospace" style="font-size: 0.62rem; letter-spacing: 0.02em;">${feat.status}</span>
                                    </div>
                                    <h4 class="h6 fw-bold mb-1 preview-text-heading">${feat.title}</h4>
                                    <p class="small preview-text-muted mb-3" style="font-size: 0.76rem; line-height: 1.45;">${feat.desc}</p>
                                </div>
                                <div class="d-flex justify-content-between align-items-center pt-2.5 border-top" style="font-size: 0.78rem; border-color: var(--preview-border) !important;">
                                    <span class="badge text-bg-light" style="font-size: 0.65rem; border: 1px solid var(--preview-border);">${feat.badge}</span>
                                    <strong class="preview-text-primary" style="font-size: 0.9rem;">${feat.price}</strong>
                                </div>
                            </div>
                        `;
                        featuresContainer.appendChild(card);
                    });
                }
            });

            // Assign Dynamic Hero Layout Class
            const heroEl = document.getElementById("preview-hero-element");
            if (heroEl) {
                const heroLayouts = {
                    "restaurant-food": "hero-layout-background hero-theme-dark",
                    "technology": "hero-layout-split",
                    "finance": "hero-layout-product",
                    "healthcare": "hero-layout-split",
                    "education": "hero-layout-product",
                    "beauty-cosmetics": "hero-layout-editorial",
                    "construction": "hero-layout-background hero-theme-dark",
                    "logistics-transport": "hero-layout-collage",
                    "fashion": "hero-layout-editorial",
                    "real-estate": "hero-layout-product",
                    "hospitality-tourism": "hero-layout-background hero-theme-dark",
                    "agriculture": "hero-layout-split",
                    "corporate-services": "hero-layout-editorial",
                    "nonprofit-ngo": "hero-layout-background hero-theme-dark",
                    "default": "hero-layout-background"
                };
                heroEl.className = "preview-hero-section " + (heroLayouts[categorySlug] || heroLayouts.default);
            }

            // Toggle Search overlay form fields (for real-estate, tourism, education)
            const searchFormEl = document.getElementById("preview-hero-search-form");
            if (searchFormEl) {
                const showSearch = ["real-estate", "hospitality-tourism", "education"].includes(categorySlug);
                if (showSearch) {
                    searchFormEl.classList.remove("d-none");
                } else {
                    searchFormEl.classList.add("d-none");
                }
            }

            // Transparent Header logic
            const navbarEl = document.getElementById("preview-navbar-element");
            if (navbarEl) {
                const isTransparent = ["restaurant-food", "construction", "hospitality-tourism", "nonprofit-ngo"].includes(categorySlug);
                if (isTransparent) {
                    navbarEl.classList.add("navbar-transparent");
                } else {
                    navbarEl.classList.remove("navbar-transparent");
                }
            }

            // Force scroll reset
            const previewMain = document.getElementById("live-business-preview");
            if (previewMain) {
                previewMain.scrollTop = 0;
                if (navbarEl) navbarEl.classList.remove("navbar-scrolled");
            }

            // Redraw Photographic Visual Assets
            this.updatePreviewImages(categorySlug);
        },

        setColors: function(colorMap) {
            const previewElement = document.getElementById("live-business-preview");
            if (!previewElement) return;

            const variableMap = {
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
                INFO: "--preview-info"
            };

            Object.keys(colorMap).forEach(role => {
                const cssVar = variableMap[role];
                if (cssVar) {
                    previewElement.style.setProperty(cssVar, colorMap[role]);
                }
            });
        },

        setTheme: function(themeMode) {
            const previewElement = document.getElementById("live-business-preview");
            if (!previewElement) return;

            if (themeMode === "DARK") {
                previewElement.classList.add("theme-preview-dark");
            } else {
                previewElement.classList.remove("theme-preview-dark");
            }
        },

        refresh: function() {
            const categorySelect = document.querySelector("#id_business_category");
            let activeCategory = "default";

            if (categorySelect) {
                activeCategory = categorySelect.value;
            } else {
                const previewEl = document.getElementById("live-business-preview");
                if (previewEl && previewEl.dataset.category) {
                    activeCategory = previewEl.dataset.category;
                }
            }

            let colors = {};
            document.querySelectorAll(".hex-input").forEach(input => {
                colors[input.dataset.colorRole] = input.value;
            });
            
            // Read computed properties directly if no color sliders are rendered
            const previewEl = document.getElementById("live-business-preview");
            if (Object.keys(colors).length === 0 && previewEl) {
                const style = getComputedStyle(previewEl);
                const variableMap = {
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
                    INFO: "--preview-info"
                };
                Object.keys(variableMap).forEach(role => {
                    const val = style.getPropertyValue(variableMap[role]).trim();
                    if (val) colors[role] = val;
                });
            }

            this.setColors(colors);

            const themeSelect = document.querySelector("#id_theme_mode");
            if (themeSelect) {
                this.setTheme(themeSelect.value);
            }

            // Complete category rendering
            this.setCategory(activeCategory);
        }
    };

    document.addEventListener("DOMContentLoaded", () => {
        if (document.getElementById("live-business-preview")) {
            window.SkilitePreview.init();
        }
    });
})();
