"use strict";

(function() {
    window.SkilitePreviewImages = {
        // Active color values to inject into SVGs
        getColors: function() {
            const previewEl = document.getElementById("live-business-preview");
            const defaults = {
                primary: "#2563eb",
                secondary: "#64748b",
                accent: "#f59e0b",
                background: "#f8fafc",
                surface: "#ffffff",
                heading: "#0f172a",
                bodyText: "#334155",
                mutedText: "#64748b",
                border: "#e2e8f0",
                success: "#16a34a",
                warning: "#d97706",
                danger: "#dc2626",
                info: "#0284c7"
            };

            if (!previewEl) return defaults;

            const style = getComputedStyle(previewEl);
            return {
                primary: style.getPropertyValue("--preview-primary").trim() || defaults.primary,
                secondary: style.getPropertyValue("--preview-secondary").trim() || defaults.secondary,
                accent: style.getPropertyValue("--preview-accent").trim() || defaults.accent,
                background: style.getPropertyValue("--preview-background").trim() || defaults.background,
                surface: style.getPropertyValue("--preview-surface").trim() || defaults.surface,
                heading: style.getPropertyValue("--preview-heading").trim() || defaults.heading,
                bodyText: style.getPropertyValue("--preview-body-text").trim() || defaults.bodyText,
                mutedText: style.getPropertyValue("--preview-muted-text").trim() || defaults.mutedText,
                border: style.getPropertyValue("--preview-border").trim() || defaults.border,
                success: style.getPropertyValue("--preview-success").trim() || defaults.success,
                warning: style.getPropertyValue("--preview-warning").trim() || defaults.warning,
                danger: style.getPropertyValue("--preview-danger").trim() || defaults.danger,
                info: style.getPropertyValue("--preview-info").trim() || defaults.info
            };
        },

        // Helper to encode SVG into compliant Data URI
        encodeSvg: function(svgString) {
            return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svgString);
        },

        // Generator for realistic category SVGs
        generate: function(category, type, index) {
            const colors = this.getColors();
            const idx = parseInt(index) || 0;

            switch (type) {
                case "hero":
                    return this.encodeSvg(this.templates.hero(category, colors));
                case "about":
                    return this.encodeSvg(this.templates.about(category, colors));
                case "cta":
                    return this.encodeSvg(this.templates.cta(category, colors));
                case "product":
                    return this.encodeSvg(this.templates.product(category, idx, colors));
                case "team":
                case "testimonial":
                    return this.encodeSvg(this.templates.avatar(category, type, idx, colors));
                case "cover":
                    return this.encodeSvg(this.templates.cover(category, colors));
                case "location":
                    return this.encodeSvg(this.templates.location(colors));
                case "gallery":
                    return this.encodeSvg(this.templates.gallery(category, idx, colors));
                default:
                    return this.encodeSvg(this.templates.generic(colors));
            }
        },

        // Templates repository
        templates: {
            hero: function(cat, c) {
                let illustration = "";

                // Render beautiful vector illustrations based on category
                if (cat === "restaurant-food") {
                    illustration = `
                        <!-- Plate with Jollof rice, plantain, chicken -->
                        <circle cx="580" cy="225" r="140" fill="${c.surface}" stroke="${c.border}" stroke-width="4"/>
                        <circle cx="580" cy="225" r="100" fill="${c.accent}" opacity="0.85"/>
                        <!-- Rice grains texture -->
                        <circle cx="550" cy="210" r="4" fill="${c.primary}"/>
                        <circle cx="560" cy="200" r="4" fill="${c.primary}"/>
                        <circle cx="570" cy="220" r="4" fill="${c.primary}"/>
                        <circle cx="540" cy="230" r="4" fill="${c.primary}"/>
                        <!-- Grilled Chicken representation -->
                        <path d="M600,180 Q650,180 640,220 Q610,240 600,180 Z" fill="${c.primary}" opacity="0.9"/>
                        <!-- Plantain slices -->
                        <ellipse cx="530" cy="250" rx="20" ry="10" fill="${c.warning}" transform="rotate(-15, 530, 250)"/>
                        <ellipse cx="550" cy="265" rx="20" ry="10" fill="${c.warning}" transform="rotate(-10, 550, 265)"/>
                        <!-- Drink Glass (Sobolo) -->
                        <rect x="440" y="120" width="40" height="90" rx="5" fill="${c.danger}" opacity="0.8"/>
                        <line x1="435" y1="120" x2="485" y2="120" stroke="${c.border}" stroke-width="4"/>
                        <line x1="450" y1="130" x2="420" y2="90" stroke="${c.accent}" stroke-width="4"/> <!-- Straw -->
                    `;
                } else if (cat === "technology") {
                    illustration = `
                        <!-- Cloud servers & dashboard dashboard -->
                        <rect x="460" y="100" width="260" height="150" rx="10" fill="${c.surface}" stroke="${c.primary}" stroke-width="4" filter="drop-shadow(0 4px 8px rgba(0,0,0,0.1))"/>
                        <rect x="475" y="115" width="230" height="25" rx="5" fill="${c.primary}" opacity="0.15"/>
                        <rect x="475" y="150" width="70" height="85" rx="5" fill="${c.accent}" opacity="0.2"/>
                        <rect x="555" y="150" width="150" height="40" rx="5" fill="${c.primary}" opacity="0.2"/>
                        <rect x="555" y="200" width="150" height="35" rx="5" fill="${c.secondary}" opacity="0.2"/>
                        <!-- Tech connections lines -->
                        <path d="M460,200 L400,200 L370,160 M400,200 L370,240" stroke="${c.accent}" stroke-width="3" stroke-dasharray="6,4" fill="none"/>
                        <circle cx="370" cy="160" r="10" fill="${c.accent}"/>
                        <circle cx="370" cy="240" r="10" fill="${c.primary}"/>
                    `;
                } else if (cat === "real-estate") {
                    illustration = `
                        <!-- Modern Villa blueprint / illustration -->
                        <rect x="450" y="150" width="280" height="180" fill="${c.surface}" stroke="${c.border}" stroke-width="2" rx="8"/>
                        <path d="M450,150 L590,70 L730,150 Z" fill="url(#hero-grad)"/>
                        <rect x="490" y="200" width="60" height="130" fill="${c.primary}" opacity="0.9"/>
                        <circle cx="535" cy="265" r="5" fill="${c.accent}"/>
                        <!-- Big Windows -->
                        <rect x="590" y="180" width="100" height="80" fill="${c.info}" opacity="0.4" rx="4"/>
                        <line x1="640" y1="180" x2="640" y2="260" stroke="${c.surface}" stroke-width="2"/>
                        <line x1="590" y1="220" x2="690" y2="220" stroke="${c.surface}" stroke-width="2"/>
                    `;
                } else if (cat === "healthcare") {
                    illustration = `
                        <!-- Stethoscope & clinic elements -->
                        <circle cx="580" cy="225" r="130" fill="${c.primary}" opacity="0.08"/>
                        <!-- Heart Beat Wave -->
                        <path d="M420,225 L490,225 L505,180 L520,270 L535,210 L545,235 L555,225 L720,225" stroke="${c.danger}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                        <!-- Doctor symbol -->
                        <circle cx="580" cy="160" r="35" fill="${c.primary}"/>
                        <path d="M530,240 C530,200 630,200 630,240 Z" fill="${c.primary}"/>
                        <circle cx="580" cy="225" r="20" fill="${c.surface}" stroke="${c.accent}" stroke-width="4"/>
                        <path d="M573,225 L587,225 M580,218 L580,232" stroke="${c.accent}" stroke-width="4"/>
                    `;
                } else if (cat === "finance") {
                    illustration = `
                        <!-- Upward investment trending graph -->
                        <rect x="440" y="80" width="280" height="280" rx="10" fill="${c.surface}" stroke="${c.border}" stroke-width="2"/>
                        <path d="M460,320 L520,270 L580,220 L640,140 L700,90" fill="none" stroke="${c.success}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="700" cy="90" r="10" fill="${c.accent}"/>
                        <!-- Bar chart columns -->
                        <rect x="470" y="280" width="25" height="40" fill="${c.primary}" opacity="0.3"/>
                        <rect x="530" y="230" width="25" height="90" fill="${c.primary}" opacity="0.5"/>
                        <rect x="590" y="180" width="25" height="140" fill="${c.primary}" opacity="0.7"/>
                        <rect x="650" y="110" width="25" height="210" fill="${c.primary}"/>
                    `;
                } else if (cat === "education") {
                    illustration = `
                        <!-- Open book & graduation cap -->
                        <path d="M460,260 Q570,220 680,260 L680,160 Q570,120 460,160 Z" fill="${c.surface}" stroke="${c.primary}" stroke-width="4"/>
                        <line x1="570" y1="140" x2="570" y2="245" stroke="${c.primary}" stroke-width="4"/>
                        <!-- Mortarboard cap -->
                        <polygon points="570,60 670,100 570,140 470,100" fill="${c.accent}"/>
                        <rect x="560" y="100" width="20" height="45" fill="${c.primary}"/>
                        <path d="M670,100 L670,150" stroke="${c.accent}" stroke-width="3" fill="none"/>
                    `;
                } else if (cat === "beauty-cosmetics") {
                    illustration = `
                        <!-- Flower & Spa vector -->
                        <circle cx="580" cy="225" r="110" fill="${c.accent}" opacity="0.1"/>
                        <path d="M580,120 C560,180 520,180 520,225 C520,270 580,270 580,225 Z" fill="${c.primary}" opacity="0.8"/>
                        <path d="M580,120 C600,180 640,180 640,225 C640,270 580,270 580,225 Z" fill="${c.primary}" opacity="0.8"/>
                        <path d="M480,225 C540,205 540,165 580,165 C620,165 620,205 680,225 Z" fill="${c.accent}" opacity="0.6"/>
                        <circle cx="580" cy="225" r="20" fill="${c.surface}"/>
                    `;
                } else if (cat === "construction") {
                    illustration = `
                        <!-- Heavy Crane building a skyscraper -->
                        <rect x="480" y="160" width="80" height="200" fill="${c.surface}" stroke="${c.border}" stroke-width="3"/>
                        <line x1="480" y1="200" x2="560" y2="200" stroke="${c.border}"/>
                        <line x1="480" y1="260" x2="560" y2="260" stroke="${c.border}"/>
                        <!-- Crane Arm -->
                        <line x1="620" y1="60" x2="620" y2="360" stroke="${c.accent}" stroke-width="8"/>
                        <line x1="620" y1="100" x2="450" y2="100" stroke="${c.accent}" stroke-width="6"/>
                        <line x1="470" y1="100" x2="470" y2="160" stroke="${c.primary}" stroke-width="3"/> <!-- Hook -->
                    `;
                } else if (cat === "logistics-transport") {
                    illustration = `
                        <!-- Delivery truck & globe -->
                        <rect x="460" y="170" width="180" height="100" rx="5" fill="${c.primary}"/>
                        <rect x="640" y="190" width="60" height="80" rx="5" fill="${c.primary}"/>
                        <circle cx="510" cy="285" r="25" fill="${c.accent}"/>
                        <circle cx="630" cy="285" r="25" fill="${c.accent}"/>
                        <rect x="660" y="200" width="30" height="30" fill="${c.surface}"/>
                    `;
                } else if (cat === "fashion") {
                    illustration = `
                        <!-- Sewing hanger and Kente dress blueprint -->
                        <path d="M500,120 L580,60 L660,120" stroke="${c.primary}" stroke-width="5" fill="none"/>
                        <path d="M580,60 L580,90" stroke="${c.primary}" stroke-width="5" fill="none"/>
                        <!-- Gown shape with Kente colors -->
                        <path d="M510,130 L650,130 L680,360 L480,360 Z" fill="${c.accent}" opacity="0.2"/>
                        <rect x="520" y="160" width="120" height="30" fill="${c.primary}"/>
                        <rect x="530" y="210" width="100" height="30" fill="${c.danger}"/>
                        <rect x="510" y="260" width="140" height="30" fill="${c.warning}"/>
                    `;
                } else if (cat === "hospitality-tourism") {
                    illustration = `
                        <!-- Sunset behind palm tree coconut -->
                        <circle cx="580" cy="225" r="120" fill="${c.accent}" opacity="0.9"/>
                        <!-- Waves -->
                        <path d="M420,320 Q500,280 580,320 T740,320 L740,360 L420,360 Z" fill="${c.primary}"/>
                        <!-- Palm tree trunk -->
                        <path d="M480,330 Q510,220 540,140" stroke="${c.secondary}" stroke-width="8" fill="none"/>
                        <!-- Palm leaves -->
                        <path d="M540,140 Q470,120 450,150 M540,140 Q580,100 610,120 M540,140 Q520,80 500,100" stroke="${c.success}" stroke-width="5" fill="none"/>
                    `;
                } else if (cat === "agriculture") {
                    illustration = `
                        <!-- Tractor and wheat crops -->
                        <circle cx="580" cy="225" r="120" fill="${c.success}" opacity="0.08"/>
                        <!-- Crops lines -->
                        <path d="M420,340 L740,340 M450,300 L450,340 M500,290 L500,340 M550,300 L550,340 M600,280 L600,340" stroke="${c.success}" stroke-width="4"/>
                        <circle cx="450" cy="290" r="6" fill="${c.accent}"/>
                        <circle cx="500" cy="280" r="6" fill="${c.accent}"/>
                        <circle cx="550" cy="290" r="6" fill="${c.accent}"/>
                    `;
                } else if (cat === "nonprofit-ngo") {
                    illustration = `
                        <!-- Heart in hands outline -->
                        <path d="M580,260 C530,200 480,150 530,110 C580,70 580,130 580,130 C580,130 580,70 630,110 C680,150 630,200 580,260 Z" fill="${c.danger}" opacity="0.85"/>
                        <!-- Holding Hands vectors -->
                        <path d="M460,300 Q540,260 580,310" stroke="${c.primary}" stroke-width="8" fill="none" stroke-linecap="round"/>
                        <path d="M700,300 Q620,260 580,310" stroke="${c.primary}" stroke-width="8" fill="none" stroke-linecap="round"/>
                    `;
                } else {
                    // Default Fallback - Abstract professional business layout
                    illustration = `
                        <rect x="460" y="100" width="240" height="240" rx="12" fill="${c.surface}" stroke="${c.border}" stroke-width="4"/>
                        <circle cx="580" cy="220" r="70" fill="url(#hero-grad)"/>
                        <line x1="500" y1="160" x2="660" y2="160" stroke="${c.accent}" stroke-width="5" stroke-linecap="round"/>
                        <line x1="500" y1="280" x2="600" y2="280" stroke="${c.primary}" stroke-width="5" stroke-linecap="round"/>
                    `;
                }

                return `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" width="100%" height="100%">
                        <defs>
                            <linearGradient id="hero-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="${c.primary}" />
                                <stop offset="100%" stop-color="${c.accent}" />
                            </linearGradient>
                        </defs>
                        <rect width="800" height="450" fill="${c.background}"/>
                        <!-- Background Grid pattern -->
                        <g opacity="0.05">
                            <line x1="0" y1="50" x2="800" y2="50" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="0" y1="100" x2="800" y2="100" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="0" y1="150" x2="800" y2="150" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="0" y1="200" x2="800" y2="200" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="0" y1="250" x2="800" y2="250" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="0" y1="300" x2="800" y2="300" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="0" y1="350" x2="800" y2="350" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="0" y1="400" x2="800" y2="400" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="100" y1="0" x2="100" y2="450" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="200" y1="0" x2="200" y2="450" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="300" y1="0" x2="300" y2="450" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="400" y1="0" x2="400" y2="450" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="500" y1="0" x2="500" y2="450" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="600" y1="0" x2="600" y2="450" stroke="${c.bodyText}" stroke-width="1"/>
                            <line x1="700" y1="0" x2="700" y2="450" stroke="${c.bodyText}" stroke-width="1"/>
                        </g>
                        <!-- Geometric decor -->
                        <circle cx="70" cy="380" r="120" fill="${c.primary}" opacity="0.03"/>
                        <circle cx="730" cy="80" r="160" fill="${c.accent}" opacity="0.03"/>
                        
                        <!-- Illustration content -->
                        ${illustration}
                    </svg>
                `;
            },

            about: function(cat, c) {
                return `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300" width="100%" height="100%">
                        <rect width="800" height="300" fill="${c.surface}"/>
                        <rect x="20" y="20" width="760" height="260" rx="8" fill="${c.background}" stroke="${c.border}" stroke-width="2"/>
                        <!-- Decorative banner lines -->
                        <path d="M20,150 Q200,80 400,150 T780,150" fill="none" stroke="${c.primary}" stroke-width="4" opacity="0.2"/>
                        <path d="M20,180 Q200,110 400,180 T780,180" fill="none" stroke="${c.accent}" stroke-width="2" opacity="0.15"/>
                        <!-- Abstract Team/Office illustration outline -->
                        <circle cx="280" cy="150" r="30" fill="${c.primary}"/>
                        <circle cx="400" cy="130" r="35" fill="${c.accent}"/>
                        <circle cx="520" cy="150" r="30" fill="${c.secondary}"/>
                        <path d="M240,220 C240,190 320,190 320,220 Z" fill="${c.primary}"/>
                        <path d="M350,210 C350,175 450,175 450,210 Z" fill="${c.accent}"/>
                        <path d="M480,220 C480,190 560,190 560,220 Z" fill="${c.secondary}"/>
                    </svg>
                `;
            },

            cta: function(cat, c) {
                return `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 150" width="100%" height="100%">
                        <rect width="150" height="150" fill="${c.accent}" rx="8"/>
                        <!-- Megaphone / Mail alert icon -->
                        <path d="M40,90 L60,90 L85,115 L85,35 L60,60 L40,60 Z" fill="${c.surface}"/>
                        <path d="M95,60 Q110,75 95,90" stroke="${c.surface}" stroke-width="4" fill="none" stroke-linecap="round"/>
                        <path d="M105,50 Q125,75 105,100" stroke="${c.surface}" stroke-width="4" fill="none" stroke-linecap="round"/>
                    </svg>
                `;
            },

            product: function(cat, idx, c) {
                const icons = {
                    "restaurant-food": [
                        `<circle cx="100" cy="60" r="45" fill="${c.accent}" opacity="0.8"/><circle cx="100" cy="60" r="30" fill="${c.surface}"/><path d="M80,60 L120,60" stroke="${c.primary}" stroke-width="4"/>`, // Jollof bowl
                        `<path d="M60,65 Q100,30 140,65 L140,75 L60,75 Z" fill="${c.primary}"/><rect x="70" y="75" width="60" height="10" fill="${c.accent}"/>`, // Banku fish
                        `<ellipse cx="100" cy="60" rx="40" ry="25" fill="${c.accent}"/><circle cx="100" cy="50" r="15" fill="${c.primary}"/>`, // Fufu bowl
                        `<rect x="85" y="30" width="30" height="60" fill="${c.danger}"/><line x1="80" y1="30" x2="120" y2="30" stroke="${c.border}" stroke-width="3"/>` // Sobolo glass
                    ],
                    "technology": [
                        `<rect x="60" y="35" width="80" height="50" rx="5" fill="${c.primary}"/><rect x="70" y="45" width="60" height="30" fill="${c.surface}"/><rect x="90" y="85" width="20" height="10" fill="${c.primary}"/>`, // Monitor
                        `<path d="M100,30 L135,50 L135,90 L100,110 L65,90 L65,50 Z" fill="${c.info}" opacity="0.8"/>`, // API Gateway
                        `<rect x="70" y="35" width="60" height="50" rx="5" fill="${c.primary}"/><path d="M85,35 L85,25 Q100,15 115,25 L115,35" stroke="${c.accent}" stroke-width="4" fill="none"/>`, // Security Shield
                        `<circle cx="100" cy="60" r="30" fill="${c.danger}" opacity="0.8"/><path d="M85,60 L115,60 M100,45 L100,75" stroke="${c.surface}" stroke-width="4"/>` // AI Engine
                    ]
                };

                const catIcons = icons[cat] || icons["technology"];
                const itemIcon = catIcons[idx % catIcons.length] || catIcons[0];

                return `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 120" width="100%" height="100%">
                        <rect width="200" height="120" fill="${c.background}"/>
                        <!-- Dynamic vector center -->
                        <g transform="translate(0, 0)">
                            ${itemIcon}
                        </g>
                    </svg>
                `;
            },

            avatar: function(cat, type, idx, c) {
                // Different fill colors for portraits
                const fills = [c.primary, c.accent, c.secondary, c.success];
                const activeFill = fills[idx % fills.length];

                return `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100%" height="100%">
                        <circle cx="50" cy="50" r="50" fill="${activeFill}" opacity="0.15"/>
                        <circle cx="50" cy="50" r="46" fill="none" stroke="${activeFill}" stroke-width="2"/>
                        <!-- Head -->
                        <circle cx="50" cy="40" r="18" fill="${activeFill}"/>
                        <!-- Shoulders -->
                        <path d="M22,78 C22,60 78,60 78,78 Z" fill="${activeFill}"/>
                    </svg>
                `;
            },

            cover: function(cat, c) {
                return `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 200" width="100%" height="100%">
                        <defs>
                            <linearGradient id="cover-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stop-color="${c.primary}" />
                                <stop offset="50%" stop-color="${c.secondary}" />
                                <stop offset="100%" stop-color="${c.accent}" />
                            </linearGradient>
                        </defs>
                        <rect width="800" height="200" fill="url(#cover-grad)"/>
                        <!-- Widescreen abstract geometric lines -->
                        <polygon points="600,0 800,0 800,200 500,200" fill="${c.surface}" opacity="0.1"/>
                        <polygon points="0,200 300,200 200,0 0,0" fill="${c.background}" opacity="0.1"/>
                    </svg>
                `;
            },

            location: function(c) {
                return `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 200" width="100%" height="100%">
                        <rect width="800" height="200" fill="${c.background}"/>
                        <!-- Map grid lines -->
                        <g stroke="${c.border}" stroke-width="2" opacity="0.5">
                            <!-- Horizontal roads -->
                            <line x1="0" y1="50" x2="800" y2="50"/>
                            <line x1="0" y1="120" x2="800" y2="120"/>
                            <line x1="0" y1="170" x2="800" y2="170"/>
                            <!-- Vertical roads -->
                            <line x1="150" y1="0" x2="150" y2="200"/>
                            <line x1="300" y1="0" x2="300" y2="200"/>
                            <line x1="450" y1="0" x2="450" y2="200"/>
                            <line x1="650" y1="0" x2="650" y2="200"/>
                        </g>
                        <!-- Green parks area -->
                        <rect x="320" y="10" width="110" height="90" rx="5" fill="${c.success}" opacity="0.15"/>
                        <rect x="470" y="130" width="160" height="30" rx="5" fill="${c.success}" opacity="0.15"/>
                        <!-- Location Pin -->
                        <g transform="translate(300, 120)">
                            <path d="M0,-24 C-10,-24 -18,-16 -18,-6 C-18,6 0,24 0,24 C0,24 18,6 18,-6 C18,-16 10,-24 0,-24 Z" fill="${c.accent}"/>
                            <circle cx="0" cy="-6" r="6" fill="${c.surface}"/>
                        </g>
                    </svg>
                `;
            },

            gallery: function(cat, idx, c) {
                const colors = [c.primary, c.accent, c.info, c.secondary];
                const activeColor = colors[idx % colors.length];

                return `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 150" width="100%" height="100%">
                        <rect width="200" height="150" fill="${c.surface}"/>
                        <rect x="10" y="10" width="180" height="130" rx="5" fill="${activeColor}" opacity="0.1" stroke="${c.border}" stroke-width="2"/>
                        <!-- Abstract picture framing -->
                        <circle cx="100" cy="65" r="25" fill="${activeColor}" opacity="0.6"/>
                        <!-- Mountain sketch -->
                        <polygon points="40,110 80,60 120,110" fill="${c.secondary}" opacity="0.4"/>
                        <polygon points="90,110 130,70 170,110" fill="${c.secondary}" opacity="0.6"/>
                    </svg>
                `;
            },

            generic: function(c) {
                return `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 150" width="100%" height="100%">
                        <rect width="200" height="150" fill="${c.background}"/>
                        <circle cx="100" cy="75" r="30" fill="${c.primary}" opacity="0.2"/>
                        <path d="M70,85 L100,55 L130,85" fill="none" stroke="${c.primary}" stroke-width="4"/>
                    </svg>
                `;
            }
        }
    };
})();
