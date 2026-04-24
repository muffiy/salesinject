# SalesInject: The Visibility War Game
**Comprehensive Project Overview, Technical Architecture, and MENA Business Strategy**

This document serves as the master blueprint for **SalesInject**. It is designed so that anyone reading it can fully understand the project's goals, its technical architecture, and the business strategy required to scale it—specifically looking through the lens of a Tunisian founder targeting the MENA ecosystem.

---

## 🌟 1. Executive Summary & Vision

**SalesInject** is an AI-powered Telegram Mini App platform that revolutionizes influencer marketing by connecting influencers with brands through a gamified 3D visualization experience. 

**Key Features:**
- **The Map (Visibility War Game):** A 3D city map (powered by DeckGL built on `worldmonitor-datastream-ui` origins) where influencers appear as floating bubbles. Size indicates followers, color represents their niche, and pulse shows recent activity.
- **AI Agents (OpenClaw Powered):** An intelligent backend uses agents (Scout, Matchmaker) to discover influencers, evaluate them, and match them automatically with brands. 
- **Telegram Native:** The entire application runs as a Mini App directly inside Telegram, removing the friction of App Store downloads and allowing for instant user onboarding.
- **Monetization:** The platform generates revenue by taking a commission (e.g., 15%) on facilitated brand-influencer deals.

---

## 🛠️ 2. Technical Architecture & Setup Guide

This section outlines the structure of the `salesinject` repository and how it functions, enabling any developer to understand and build upon it.

### A. Frontend (`/frontend`)
The frontend is a React application optimized for the Telegram Web App environment.

- **Framework:** React 19 + TypeScript, bundled with Vite.
- **Environment:** Integrates `@twa-dev/sdk` to securely authenticate and run natively inside Telegram (`TelegramGuard`).
- **Styling:** Uses Tailwind CSS (`@tailwindcss/postcss`) relying heavily on custom CSS variables (e.g., `--war-black`, `--war-cyan`) to achieve a sleek, cyber-gamified aesthetic.
- **3D Visualization:** The core "Map Page" uses `deck.gl` and `react-map-gl` to render the immersive influencer environment.
- **Routing:** Handled via `react-router-dom` across pages: `/app/dashboard`, `/app/tasks`, `/app/agents`, `/app/profile`, and the background Map.

### B. Backend (`/backend`)
The backend is a high-performance Python application handling AI orchestration, API requests, and Telegram Bot interactions.

- **API Engine:** FastAPI running on `uvicorn`.
- **Database:** PostgreSQL. It utilizes:
  - **SQLAlchemy:** For ORM managing `users`, `agents`, `tasks`, `agent_memories`.
  - **pgvector:** For storing AI embeddings (via `sentence-transformers`), enabling semantic search over memories and scraped ads.
- **AI Pipeline:** Uses robust orchestrators (`run_scout_mission`) that rely on the `exa_py` API for discovering influencers, alongside intelligent ranking algorithms.
- **Asynchronous Tasks:** Celery + Redis handle background tasks like deep internet scraping for the Scout agent.
- **Telegram Bot:** Powered by `aiogram`, seamlessly integrated into the FastAPI lifecycle mapping webhooks to bot actions.

### C. How to Run Locally

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Backend:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
*(Ensure PostgreSQL with `pgvector` and Redis are running locally via Docker, matching credentials in `.env`)*

---

## 🇹🇳 3. Tunisian Market Opportunity Analysis

- **Digital Landscape:** Tunisia has robust internet penetration with ~8.4 million active social media users. Meta platforms (Facebook/Instagram) dominate at nearly 90% penetration, while TikTok is rapidly capturing the Gen-Z demographic.
- **Influencer Ecosystem:** There are generally 15,000–20,000 active creators in Tunisia. Top niches include Tech, Fashion, Food, and Tourism.
- **Pain Points:** Brand-creator collaborations currently happen via chaotic Instagram DMs or WhatsApp texts. There's zero transparent pricing, poor tracking, and no automated matching.
- **Cultural Dynamics:** Creators use *Derja* (Tunisian Arabic mixed with French). Campaigns, especially during high-velocity seasons like Ramadan, require nuanced cultural understanding.

---

## 📊 4. Market Size & Financial Revenue Potential

Calculations tailored for the MENA region with an initial focus on Tunisia:

- **TAM (MENA Influencer Mktg):** ~$1.2 Billion by 2026.
- **SAM (Maghreb Region):** ~$150 Million.
- **SOM (Tunisia Initial Focus):** ~$5 - $8 Million in micro/mid-influencer transactional value.

**12-Month Realistic Revenue Projection (assuming 15% Platform Commission):**
- **Months 1-3:** 100 creators, 30 deals/month (Avg. 500 TND) ➔ ~2,250 TND / Month
- **Months 4-6:** 500 creators, 150 deals/month (Avg. 700 TND) ➔ ~15,750 TND / Month
- **Months 7-9:** 1,500 creators, 500 deals/month (Avg. 1,000 TND) ➔ ~75,000 TND / Month
- **Months 10-12:** 3,000+ creators, 1,200 deals/month (Avg. 1,500 TND) ➔ ~270,000 TND / Month

---

## 🏗️ 5. Tunisia-Specific Advantages & Resources

Tunisian founders have strategic systemic advantages heading into 2026:

- **Funding Ecosystem:** Startups are eligible for the World Bank *"Startups and PMEs Innovantes"* (up to 150k TND), and programs like the ITC Digital Trade.
- **Startup Act:** Becoming "Startup Label" certified grants tax exemptions, foreign currency accounts, and covers founder's state-backed salaries.
- **Talent Pool:** Access to a highly skilled, multilingual (Arabic, French, English) engineering workforce at competitive rates compared to EU/US markets.
- **Strategic Gateway:** Tunisia serves as the ideal sandbox to validate product-market-fit before expanding horizontally across the Maghreb and vertically down into Francophone Africa.

---

## 🚀 6. MENA Regional Expansion Strategy

- **Phase 1: Tunisia (Months 1-6)** - Attain product-market fit. Manually concierging the first 50 brand deals to polish the UI and validate the Telegram mini-app flow.
- **Phase 2: Maghreb / Algeria & Morocco (Months 7-12)** - Linguistic and cultural similarities allow scaling using the exact same Deep Learning/NLP models trained on Derja/French.
- **Phase 3: GCC / Egypt, Saudi Arabia, UAE (Months 13-24)** - Enter the high-ticket market. Re-train AI Matchmaker NLP on Gulf/Egyptian Arabic dialects. Tap into massive macro-influencer budgets.
- **Phase 4: Francophone Africa (Year 3+)** - Leverage TABC-Novation City partnerships to scale out into Ivory Coast, Senegal, etc.

---

## 💡 7. Product Adaptations for Tunisia & MENA

- **Payment Processing:** Integrating local gateways (Flouci, D17) for early traction. Using a Delaware LLC/Stripe combination to hold and route funds when scaling into the EU/GCC.
- **Language Models:** Customizing OpenClaw/Agent Zero to inherently understand Derja text inside Instagram captions and TikTok videos.
- **Cultural Platform Modes:** Adding a "Ramadan Mode" to the visual map UI, prioritizing food, family-oriented, and modest-fashion creators.
- **WhatsApp Integration:** Eventually pushing Agent Matchmaker notifications via WhatsApp (in addition to Telegram) to capture older, traditional brand managers.

---

## ⚖️ 8. Competitive Landscape Analysis

- **Global SaaS (Upfluence, Grin, AspireIQ):**
  *Weaknesses:* Ignorant of local MENA micro-cultures, highly expensive SaaS subscriptions, and clunky UI that looks like Excel sheets.
- **Regional Agencies (ArabyAds iConnect, Vamp):**
  *Weaknesses:* Act more like traditional gatekept talent agencies rather than scalable tech.
- **The SalesInject Advantage:**
  *Strengths:* 100% self-serve. Beautiful gamified 3D map format. Zero-installation via Telegram. AI-agent automation reduces manual matching hours to zero.

---

## 📈 9. Growth Strategy: The $50 Launch Plan

A realistic pivot-and-launch timeline for a bootstrapped Tunisian founder:
- **Weeks 1-2 ($15):** Setup backend on affordable cloud (Hetzner free-tier or Render). Purchase `.tn` or `.com` domain ($15). Establish Telegram webhook.
- **Weeks 3-4 ($10):** Run an AdsGram mini-campaign on Telegram targeted at Tunisian students/creators ($10). Manually DM top 50 local TikTokers. 
- **Weeks 5-8 ($15):** Concierge match the first 3 brand campaigns. Facilitate deals entirely manually if needed behind the scenes. Collect ~100 TND in commissions to reinvest into PostgreSQL node upgrades.
- **Weeks 9-12 ($10):** Officially submit for the Startup Act Label using the live prototype. Implement in-app referral ("Invite a friend, your map bubble gets larger").

---

## ⚠️ 10. Risk Assessment & Mitigation

- **API Rate Limits (Meta/Instagram):** Heavy reliance on scraping can get IPs banned. *Mitigation:* Diversify with the `exa_py` API and decentralized scraping queues via Celery.
- **Payment & Currency Friction:** Getting locked out of cross-border USD flows. *Mitigation:* Target local economy first with Flouci, secure Startup Act label for a foreign currency account.
- **Creator Novelty Attrition:** Gamified apps can lose their charm. *Mitigation:* Tie the visual "bubble" directly to real-world earnings. If they don't produce, they shrink.

---

## 🚀 11. Final Recommendation & Go-Forward

**Recommendation: STRONG GO.**

The combination of the Telegram Web App ecosystem (zero-friction), a gamified map aesthetic (highly engaging for Gen Z), and an AI-automated backend (highly capital-efficient) is a formidable wedge into the MENA influencer market.

**Top 3 Actions for Next 30 Days:**
1. **Polish the Build:** Fix missing python dependencies (e.g., `uvicorn`), ensure the `deck.gl` components fetch real mocked data from FastAPI. 
2. **Onboard the "Seed" Map Nodes:** Find 20 highly recognizable Tunisian influencers, manually add their data to the database so the 3D map looks populated and active on Day 1.
3. **Legalize & Shield:** Apply for an official patente or the Startup Label to open enterprise bank accounts necessary to process brand ad budgets.
