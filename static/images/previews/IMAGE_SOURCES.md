# Skilite Build Realistic Image Preview Sources

This document describes the design assets, image sources, formatting, and offline-first fallback mechanisms used by the **Skilite Build Realistic Web Preview Engine**.

---

## 1. Local SVG Vector Illustration Engine

To guarantee zero dependencies on external networks, 100% offline uptime, and high performance (no huge image payload downloads during app initialization), the preview engine uses a **Color-Aware Dynamic SVG Generator** built directly inside [palette-preview-site.js](file:///d:/skilite-build/static/js/palette-preview-site.js).

### Why Color-Aware SVGs are Better than Stock Photos
- **Dynamic Adaptability**: Because the SVGs are compiled as XML data-URIs on the fly in JavaScript, they read the active hex choices from the palette (such as primary, secondary, accent, and alert colors). When a user changes a color, the illustration accents (like Jollof chicken, code terminals, graphs, and houses) update immediately to match the brand color scheme!
- **DPI Scaling**: Vector graphics scale cleanly across desktop, tablet, mobile, and fullscreen widths without pixelation or layout shifts.
- **Zero Assets Overhead**: Prevents committing large multi-megabyte binary images into the repository.
- **Offline Integrity**: Continues functioning without internet access.

---

## 2. Image Categories, Types, and Intended Uses

| Category | Type | Description | Primary Colors Used |
| :--- | :--- | :--- | :--- |
| **restaurant-food** | hero | Plate with Jollof rice, plantains, chicken leg, and fresh Sobolo drink | primary, accent, warning, danger |
| **technology** | hero | Cloud server terminal and dashboard dashboard | primary, secondary, accent |
| **real-estate** | hero | Modern residential architectural villa blueprint | primary, accent, info |
| **healthcare** | hero | Doctor medical stethoscope, cross badge, and EKG wave | primary, accent, danger |
| **finance** | hero | Compounds savings vault and upward trending graphs | primary, success, accent |
| **education** | hero | Open academic text book and graduation mortarboard cap | primary, accent |
| **beauty-cosmetics** | hero | Relaxing spa beauty flower outline | primary, accent |
| **construction** | hero | Architectural skyscraper concrete column and heavy crane | primary, accent |
| **logistics-transport**| hero | Commercial cargo container truck and logistics wheels | primary, accent |
| **fashion** | hero | Traditional African Ankara/Kente clothing hanger pattern | primary, danger, warning |
| **hospitality-tourism**| hero | Cape Coast sunset behind green palm tree leaves and wave ripples | primary, success, accent |
| **agriculture** | hero | Organic tractor harvesting wheat crops | success, accent |
| **nonprofit-ngo** | hero | Volunteer community hands holding a love heart outline | primary, danger |
| **default/fallback** | hero | Corporate abstract geometric workspace graphic | primary, accent |

---

## 3. Formatting & Performance Guidelines

- **Format**: All generated vectors are served as clean, base64-equivalent URL-encoded SVG strings: `data:image/svg+xml;charset=utf-8,...`.
- **Preloading**: Fully synchronous on color changes and tab selections. Zero network calls or layout reflow lags.
- **Layout Aspect Ratios**:
  - Hero image: `16:9` panoramic viewport.
  - Product/Menu cards: `4:3` horizontal aspect ratio.
  - Team/Testimonial portraits: `1:1` square circle profiles.
  - Map / Location banner: Widescreen panoramic `8:2` block.
