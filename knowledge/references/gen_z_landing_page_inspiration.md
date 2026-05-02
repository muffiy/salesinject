# 🎨 Gen-Z High-End App Landing Page References

**Curated:** 2026-04-25
**Purpose:** Design inspiration sources for the SalesInject Telegram Mini App landing page and internal UI, emphasizing bold typography, neon accents, dopamine palettes, 3D visualization, and Gen-Z/creator-economy aesthetics.

---

## 📋 The 10 Reference Sites

### 1. Palette.site — Gen-Z Fintech Bold Color Systems
**URL:** https://palette.site/blog/2026-03-15-01-why-financial-literacy-apps-for-gen-z-should-swap-serious-blue-for-electric-magenta-and-high-energy-yellow/
**Why it matters for SalesInject:**
- Five curated high-voltage palettes: *Cybernetic Sunburst*, *Pixels & Punk*, *Dopamine Loop*, *Glitch Garden*, *Sorbet Interface*
- Direct translation guide from institutional blues → electric magenta / acid green / infrared orange / midnight anchors
- Ready-to-use hex swatches for our Tailwind config

**Steal for SalesInject:** The *Glitch Garden* palette (High-Vis Yellow + Terminal Green + Void Black) closely matches the existing design reference in `designs/363a…jpg` — codify as Tailwind tokens.

---

### 2. Spark — Gen Z Mobile Banking (Behance, Pragmatic Coders)
**URL:** https://www.behance.net/gallery/199003113/Spark-Gen-Z-mobile-app-design
**Why it matters:**
- Full case study on gamification, AI companion, ESG investing for young users
- "Entertaining to interact with" visual language — exactly the vibe SalesInject needs for influencer discovery
- Demonstrates onboarding flows that convert young audiences

**Steal:** The gamified progress rings and AI-companion chat bubble pattern — reuse for Scout mission feedback loops.

---

### 3. Bridge Money — Confederation Studio
**URL:** https://www.confederationstudio.com/work/bridge-money-mobile-app
**Why it matters:**
- "Street-smart money chasers" branding — raw, unapologetic, urban-American tone
- Black/white + gold accents, grit photography, brash typography
- Shows how to merge high-end luxury with streetwear edge

**Steal:** Typography pairing (heavy display serif + sharp mono) — perfect for Tunisian-founder brand voice that bridges MENA street culture with global influencer economy.

---

### 4. Glow — Framer Template (Production-Ready Gen-Z Fintech)
**URL:** http://glow.framer.media/
**Why it matters:**
- Landing page anatomy: hero with app mockups, BNPL modules, cashback carousels, card tiers (Glow / Gold / Black)
- Stats section, pricing grid, testimonials — full structural blueprint
- Can be forked as a starting scaffold if client wants a marketing page pre-launch

**Steal:** The tiered card showcase pattern → reuse for SalesInject pricing/agent tiers (Scout / Spy Satellite / AI General).

---

### 5. Flow Bank — Warm Human Gen-Z Banking (Behance, Nov 2025)
**URL:** https://www.behance.net/gallery/238679481/Flow-Bank-A-Gen-Z-Special-Based-Banking-Website
**Why it matters:**
- Counterpoint to loud neon — warm, human, approachable
- Proves "bold but calm" is viable for Gen-Z
- CTA-driven structure with strong hierarchy

**Steal:** The soft-gradient hero + single-focus CTA — useful for the Telegram Mini App landing screen where we need instant clarity (the "MANAGE YOUR LEADS IN ONE PLACE" screen in our reference image).

---

### 6. Dopamine UX Landing Page — Petras Baukys (Dribbble)
**URL:** https://dribbble.com/shots/25864740-Dopamine-UX-landing-page-design
**Why it matters:**
- Textbook dopamine design: `#E60521` `#A60317` `#E63C5C` `#E9708B` over `#131313` and white
- Demonstrates high-contrast pattern without feeling cheap
- Tight type system with a single accent family

**Steal:** Single-accent-family discipline — pick one neon (magenta or acid yellow), anchor everything to black, use sparingly.

---

### 7. Creatorland — Gen Z Influencer App (Phenomenon Studio, Dribbble)
**URL:** https://dribbble.com/tags/app-landing-page (search "Creatorland")
**Why it matters:**
- **74.4k views** — validated Gen-Z influencer aesthetic
- Most direct competitor-adjacent reference: influencer discovery + creator economy
- Bold typography + vivid color + interactive 3D elements

**Steal:** Creator profile card layout — adapt for our influencer search results in the Paperclip sidebar.

---

### 8. Awwwards Mobile & Apps Collection (Live-Curated)
**URL:** https://www.awwwards.com/websites/mobile-apps/
**Why it matters:**
- Always-current showcase of top mobile app marketing sites
- Featured: Synnect (social), Reeltrip (video/travel), reelmuse.ai (creator AI), AskNova Astrology (Gen-Z vertical)
- Filter by "Social Network" tag for our exact niche

**Steal:** Check weekly; specifically study **reelmuse.ai** and **Reeltrip** for creator-economy landing page structure.

---

### 9. Lapa Ninja — 3D Websites Gallery
**URL:** https://www.lapa.ninja/category/3d-websites/
**Why it matters:**
- 156 curated 3D landing pages (WebGL / Three.js / R3F / Spline)
- Direct references for the "gamified 3D visualization" promised in SalesInject's pitch
- Standouts: **Chipsa**, **Vibe-X**, **World Labs**

**Steal:** Spline-based hero interactions — lightweight enough for Telegram Mini App webview if we optimize assets.

---

### 10. Zenly-Inspired Map UI (local reference: `designs/5415…jpg`)
**URL:** https://www.zenly.com/ (app shut down but screenshots circulate via Mobbin, Dribbble)
**Why it matters:**
- Our second design-folder reference **is** a Zenly-style geosocial layout
- Proves our DeckGL map + influencer pins direction is genre-correct
- Zenly-class animation density is the north star for map interactions

**Steal:**
- Avatar-pins with speech bubbles for influencer cards on the map
- Bottom-sheet location list with "X more places" truncation pattern
- Profile screen with memory strip (horizontal image carousel) — reuse for influencer portfolio previews

**Find more:** https://mobbin.com/apps/zenly-ios

---

## 🎨 Patterns to Codify in Tailwind Config

Based on `designs/363a86e8385b3173ab19957d97610273.jpg`:

```js
// tailwind.config.js (additions)
colors: {
  brand: {
    bg: '#0A0A0A',        // near-black canvas
    card: '#141414',       // card surface
    yellow: '#E5FF45',     // acid highlight (primary CTA)
    green: '#5FF08A',      // terminal green (activity/positive)
    pink: '#FF3D9A',       // hot pink (alerts/new)
    lime: '#C9FF4D',       // lime accent
    white: '#FAFAFA',
  }
}
```

## 🧩 Component Patterns from `designs/363a…jpg` (Linear Creator CRM Mock)

This reference is a mobile lead/campaign management app — **directly reusable** for SalesInject. Components to port:

| Component | Found in screen | SalesInject use case |
|---|---|---|
| **Hero card w/ oversized number** (`75%` progress) | "Hi, Tomas" dashboard | Scout mission progress / credits remaining |
| **Color-block tile grid** (yellow/pink/green cards) | Dashboard | Agent cards (Scout, Spy Satellite, AI General) |
| **Sparkline-in-card** | Marketing screen | Influencer performance mini-chart |
| **Donut chart tile** | Marketing | Source breakdown (TikTok / IG / YT) |
| **Calendar strip + time-blocked events** | Planned Calls | Scheduled mission timeline |
| **Contact card with expandable detail** | Contact | Influencer profile quick-view |
| **Chat/source channel list** | Chats | Connected platform list |
| **Projects grid w/ image thumbnails** | Profile | Past campaigns portfolio |
| **Campaign progress slider** | Profile | Active mission status bar |
| **Notification cards, color-coded** | Notifications | Paperclip activity feed |
| **Avatar-led chat list** | Instagram Chats | Influencer DM thread placeholder |
| **Pill-shaped primary CTA at bottom** | All screens | Fixed-action-button pattern (already partial in current UI) |

## 🧩 Component Patterns from `designs/5415…jpg` (Zenly-style Geo-Social)

This reference is closest to our **MapPage** direction. Components to port:

| Component | Screen | SalesInject use case |
|---|---|---|
| **Handwritten-style city headline** | Map view | Scout mission location header |
| **Circular avatar-pins on map** | Map view | Influencer pins (already planned) |
| **Speech-bubble tail under pins** | Map view | "Last posted X ago" indicator |
| **Landmark glyph-pins** (shop/park/food) | Map view | Brand/venue markers |
| **Bottom-sheet with place list + "X more"** | Search | Results drawer for scout output |
| **Horizontal memory carousel** | Profile | Influencer content preview strip |
| **Friends list with "+ ADD" chips** | Profile | Saved influencers / shortlist |
| **Large rounded floating bottom nav** | All screens | Primary nav (already in codebase) |
| **Gradient-tinted status bar matched to content** | All screens | Themed top-bar per agent/mission |

---

## 🛠 How to Use This Document

1. **When designing a new component**, open this file + cross-reference the source URL
2. **When picking colors**, use the Tailwind tokens codified above (don't invent new ones)
3. **When in doubt about density**, err toward the Zenly reference — SalesInject is a map-first app
4. **When pitching to stakeholders**, send the Glow Framer template link as "structural direction"

**Session follow-up:** Each UI/UX implementation session must log which reference(s) were used in `knowledge/sessions/ui-ux/session_YYYY-MM-DD.md` under a new "References consulted" heading.

---

Sources:
- [Palette.site — Gen-Z Fintech Bold Color Systems](https://palette.site/blog/2026-03-15-01-why-financial-literacy-apps-for-gen-z-should-swap-serious-blue-for-electric-magenta-and-high-energy-yellow/)
- [Spark — Gen Z Mobile App Design (Behance)](https://www.behance.net/gallery/199003113/Spark-Gen-Z-mobile-app-design)
- [Bridge Money — Confederation Studio](https://www.confederationstudio.com/work/bridge-money-mobile-app)
- [Glow — Framer Template](http://glow.framer.media/)
- [Flow Bank — Gen-Z Banking (Behance)](https://www.behance.net/gallery/238679481/Flow-Bank-A-Gen-Z-Special-Based-Banking-Website)
- [Dopamine UX Landing — Petras Baukys (Dribbble)](https://dribbble.com/shots/25864740-Dopamine-UX-landing-page-design)
- [Creatorland — Phenomenon Studio (Dribbble)](https://dribbble.com/tags/app-landing-page)
- [Awwwards Mobile & Apps](https://www.awwwards.com/websites/mobile-apps/)
- [Lapa Ninja 3D Websites](https://www.lapa.ninja/category/3d-websites/)
- [Zenly via Mobbin](https://mobbin.com/apps/zenly-ios)
