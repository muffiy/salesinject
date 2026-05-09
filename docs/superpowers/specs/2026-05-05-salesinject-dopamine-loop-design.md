---
name: SalesInject Dopamine Loop & Start Page Design
description: Hyper-local influencer marketing platform with territory conquest gamification and 45-second mission dopamine loops
type: design
---

# SalesInject Dopamine Loop & Start Page Design

## Overview
Transform SalesInject into the "Uber of local influencer marketing" through hyper-local territory conquest gamification. Users (local influencers/citizens) complete location-based missions (café visits, store promotions) to claim neighborhoods and earn instant payments.

## Target Audience
- **Local Influencers**: Micro-influencers, students, content creators in specific cities
- **Citizen Ambassadors**: Everyday people willing to promote local businesses
- **Goal**: Complete missions in under 45 seconds, claim territory, earn immediate payments

## Core Dopamine Loop
1. **Profile Setup** → Get free scout credits (immediate reward)
2. **Map Entry** → See local territory with avatar at center
3. **Mission Claim** → 45-second target creates urgency
4. **Mission Complete** → Territory expansion + instant payment
5. **Progress Tracking** → Control % increases, local rank improves
6. **Repeat** with escalating stakes and larger territories

## Design Sections

### 1. Start Page (Landing.tsx)
**Military Command Aesthetic**
- **Hero Title**: "SALESINJECT" with glitch effect
- **Subtitle**: "Le 'Uber' du marketing d'influence local"
- **Primary CTA**: "DÉPLOYER VOS AGENTS" (leads to profile setup)
- **Secondary CTA**: "VOIR LE CHAMP DE BATAILLE" (blurred map preview)
- **Live Stats Ticker**: 
  - "24 Missions Actives" 
  - "125 Agents Déployés"
  - "58% Contrôle" (platform-wide average)

**Visual Elements**
- Grid overlay with moving scan lines
- Pulsing "EN DIRECT" indicator
- Micro-interactions on hover (particle effects)
- Sound effect on button click (optional military "beep")

### 2. Profile Setup & Dopamine Hook (Onboarding.tsx)
**Enhanced 3-Step Wizard**

**Step 1: Commander Alias**
- Character counter with "ALIAS DE COMMANDANT" placeholder
- Live avatar preview with sigil generation (first 2 letters)
- Subtle pulse animation on valid input

**Step 2: Target Directive (Niche)**
- French niche labels: "Restauration", "Mode", "Événements", "Services"
- Glow effect updates background with niche color
- Haptic feedback on selection (if supported)

**Step 3: Confirmation - DOPAMINE PEAK**
- **Reward Text**: "ACQUISITION D'UN SCOUT INITIAL"
- **Visual**: `DopaminePulse` centered on screen (cyan ring explosion)
- **Value Animation**: "50 CRÉDITS" → **"GRATUIT"** with strikethrough + green glow
- **Sound Effect**: Digital unlock "cha-ching"
- **Overlay**: `EmotionalFeedbackOverlay` with "PREMIER DÉPLOIEMENT ACCORDÉ"
- **Balance Display**: "SOLDE: 100 CRÉDITS" appears below

**Post-Completion Sequence**
- 2-second delay to savor reward
- Auto-navigate to 3D map centered on user's location
- `RewardDrop` animation showing "+100 CRÉDITS" from top
- `ActionStreakCounter` initialized to 1 (French label: "SÉRIE")

### 3. 3D Map Entry (MapPage.tsx)
**Hyper-Local Avatar-Centered Design**

**Initial Map State**
- Geolocation capture during profile setup (request permission, fallback to city selection if denied)
- Map zooms to user's neighborhood (500m radius) or selected city center
- User avatar appears at center with pulsing glow
- "VOTRE ZONE" highlighted with subtle boundary
- Fog of war covers 80% of map

**Avatar Interaction**
- **Tap/Click Avatar**: Opens `ProfileCard` overlay (new component in `frontend/src/components/territory/ProfileCard.tsx`) with:
  - "% de Contrôle de la ville" (starts at 0%, calculated as: (missions completed in city / total missions in city) × 100)
  - "Missions Terminées" (0)
  - "Gains" ($0)
  - "Classement Local" (#1,234 dans [Ville])
  - "ÉTENDRE LE TERRITOIRE" button (navigates to mission list)
- **Avatar States**:
  - **Idle**: Gentle pulse animation
  - **Mission Active**: Badge showing current mission type
  - **Level Up**: Explosive particle effect

**Local Mission Visualization**
- **Mission Pins**: Color-coded by type (Food, Retail, Events, Services)
- **Distance Labels**: "150m", "450m" from avatar
- **Urgency Indicators**:
  - "EXPIRE DANS [temps]" on each pin
  - "X AUTRES EN TRAIN DE RÉCLAMER" counter
  - `ThreatSignal` on missions about to expire
- **First Mission Guidance**:
  - Pulsing arrow to nearest mission (<200m)
  - Tooltip: "RÉCLAMEZ VOTRE PREMIÈRE MISSION LOCALE - < 45 SECONDES"
  - Visible countdown showing target completion time (45 seconds max)
  - Auto-zoom to mission location on selection

**Territory Progression**
- **Control % Meter**: Updates after each completed mission
- **Neighborhood Unlocks**: 3 missions in area → claims neighborhood
- **Visual Feedback**: Claimed areas show user's color/branding
- **Leaderboard**: "TOP 10 DANS [QUARTIER]" in profile card

**Dopamine Elements on Mission Complete**
- `DopaminePulse` + territory expansion animation
- `RewardDrop` showing "+2.5% CONTRÔLE"
- `EmotionalFeedbackOverlay` "TERRITOIRE SÉCURISÉ"
- `RankShiftTicker` "#1,234 → #892 DANS [VILLE]"

### 4. Behavioral Components Integration

**Existing Components to Use**
- `DopaminePulse`: Mission completion celebrations
- `EmotionalFeedbackOverlay`: Status messages ("DOMINATION", "CRITIQUE")
- `RewardDrop`: Credit/control % increases
- `ActionStreakCounter`: "SÉRIE LOCALE" (consecutive days with local mission)
- `GhostAgentsLayer`: Faint outlines of other users in same city
- `ThreatSignal`: Urgency on expiring missions
- `UncertaintyBar`: Intel accumulation during scouting
- `RankShiftTicker`: Local ranking improvements
- `MissionHeatMeter`: Tracks "CHALEUR" in local area (mission density)
- `BudgetAlert`: Becomes "BUDGET QUOTIDIEN DE TERRITOIRE"

**New Components Needed**
- `TerritoryControlMeter`: Visual % control of city
- `LocalLeaderboard`: Top influencers in user's city/neighborhood
- `45SecondTimer`: Countdown display for mission claiming
- `NeighborhoodClaimAnimation`: Visual territory expansion effect

## Success Metrics
1. **Time to First Mission**: <90 seconds from landing page
2. **Mission Completion Rate**: >70% of claimed missions completed
3. **45-Second Target**: Average mission claim-to-proof time
4. **Territory Expansion**: Users complete ≥3 missions to claim first neighborhood
5. **Return Rate**: ≥40% of users return within 24 hours

## Technical Implementation Notes

**File Modifications**
1. `frontend/src/pages/Landing.tsx`: Update hero section with French text, live stats
2. `frontend/src/pages/Onboarding.tsx`: Enhance with dopamine reward sequence
3. `frontend/src/pages/MapPage.tsx`: Add avatar-centered logic, territory visuals
4. `frontend/src/components/behavioral/`: Utilize existing components
5. New components in `frontend/src/components/territory/`

**Data Requirements**
- User geolocation (with fallback to city selection)
- Neighborhood boundary definitions
- Mission density heat maps
- Local leaderboard rankings

**Localization**
- French as primary language (as per UX document)
- Key phrases: "Contrôle", "Territoire", "Mission", "Classement", "Gains"

## Next Steps
1. **User reviews this spec** → Approve or request changes
2. **Invoke writing-plans skill** → Create detailed implementation plan
3. **Implementation** → Start with highest-impact dopamine elements
4. **Testing** → Validate 45-second mission flow and reward sequences