# 🧩 Design Folder — Component Extraction

**Source images:** `designs/363a86e8385b3173ab19957d97610273.jpg`, `designs/5415db5513dac976dd40c6c38b07dec8.jpg`

This document catalogs **every reusable component pattern** identified in the reference images and maps them to SalesInject product needs. Always consult this before designing from scratch — reuse over reinvent.

---

## 🖼 Reference A — Zenly-style Geosocial App (`363a…jpg`)

**Three screens:** Santa Monica map view · Search/place list · Profile page

### Components Identified

#### 1. Map Hero Header
- **Visual:** Giant hand-underlined serif city name ("santa monica") in top-left
- **SalesInject mapping:** Scout mission title/location stamp on MapPage
- **Component name:** `<MissionLocationHeader city={...} underline />`

#### 2. Icon-Chip Action Buttons (top-right)
- **Visual:** Rounded dark pill with single icon (profile · settings)
- **SalesInject mapping:** Universal header action buttons
- **Component name:** `<IconChip icon={...} onClick={...} />`

#### 3. Avatar Map Pins
- **Visual:** Circular profile photo with soft white ring, speech-bubble tail
- **SalesInject mapping:** Influencer pin on DeckGL map
- **Component name:** `<InfluencerPin avatar={...} badge={...} />`

#### 4. Stat Chip Pin
- **Visual:** Small black pill showing `13 MPH` or stat
- **SalesInject mapping:** Influencer metric pin ("1.2M followers" / "+45% engagement")
- **Component name:** `<StatPin value={...} unit={...} />`

#### 5. Landmark Glyph Pins
- **Visual:** White rounded square with monochrome icon (shop, park, food)
- **SalesInject mapping:** Brand / venue / event markers
- **Component name:** `<LandmarkPin type="brand|venue|event" />`

#### 6. Floating Bottom Action Bar
- **Visual:** 3 dark rounded-square buttons floating at bottom center; middle one tinted colored
- **SalesInject mapping:** Mission controls (search · new scout · view paperclip)
- **Component name:** `<FloatingActionBar actions={...} />`

#### 7. Place List Row
- **Visual:** Dark row with brand logo + name + address, "X mi" on right, chip row below
- **SalesInject mapping:** Scout result list item
- **Component name:** `<ScoutResultRow logo={...} name={...} distance={...} chips={...} />`

#### 8. Inline Search-With-Suggestions
- **Visual:** Pill search field, floating avatar-chips above keyboard showing recent matches
- **SalesInject mapping:** Influencer search with recent/suggested
- **Component name:** `<SmartSearch recent={...} />`

#### 9. Tag Chips (light & accent variants)
- **Visual:** "+2 here", "closest to home", "big squads approve" — small pill badges
- **SalesInject mapping:** Mission/influencer metadata tags
- **Component name:** `<Chip variant="neutral|accent|warning" />`

#### 10. Profile Hero Block
- **Visual:** Name + handle + pop count; large photo right; city card below
- **SalesInject mapping:** Influencer profile card in Paperclip sidebar
- **Component name:** `<ProfileHero name={...} handle={...} stats={...} hero={...} />`

#### 11. Memory Strip (horizontal image carousel)
- **Visual:** "MEMORIES" label above horizontal scroll of square images
- **SalesInject mapping:** Influencer recent content preview (IG/TikTok grid)
- **Component name:** `<ContentStrip label={...} items={...} />`

#### 12. Friends List Row with +ADD
- **Visual:** Avatar + name + status/description, right side shows "mutual" or `+ ADD` chip
- **SalesInject mapping:** Saved influencers / shortlist management
- **Component name:** `<InfluencerListRow ctaLabel="+ ADD|Saved|Pitched" />`

#### 13. Mini Map Preview Card
- **Visual:** "TOP CITY los angeles" with a mini map showing pins + "+2 friends have been there"
- **SalesInject mapping:** Campaign region card showing active influencers
- **Component name:** `<CampaignRegionCard />`

---

## 🖼 Reference B — Creator CRM Mobile App (`5415…jpg`)

**Twelve screens:** Splash · Dashboard · Campaign detail · Marketing · Planned Calls · Contact · Chats · Profile · Project detail · Notifications · Instagram Chats · All campaigns

### Components Identified

#### 1. Splash Screen with Sparkle Ornament
- **Visual:** 4-point star cluster on black + hero copy "MANAGE YOUR LEADS IN ONE PLACE" + white pill CTA
- **SalesInject mapping:** Telegram Mini App onboarding / login screen
- **Component name:** `<SplashScreen ornament={...} title={...} ctaLabel={...} />`

#### 2. Greeting + Progress Header
- **Visual:** "Hi, Tomas" + "Today tasks 75%" with thin progress bar underneath
- **SalesInject mapping:** Personalized daily dashboard header
- **Component name:** `<DailyHeader name={...} progress={...} />`

#### 3. Color-Block Tile (the signature dopamine card)
- **Visual:** Solid yellow/pink/green rounded-rect cards with title + meta; arrows on edge
- **SalesInject mapping:** Agent selection cards / mission type tiles
- **Component name:** `<DopamineTile color="yellow|pink|green|lime" title icon content />`
- **CRITICAL:** This is the highest-reuse component. Already partial in current `pages/Agents.tsx`.

#### 4. Stacked Task Card with Time Blocks
- **Visual:** Pink "Today Meets" card shows 2 time-stamped items + member avatars
- **SalesInject mapping:** Today's scheduled missions
- **Component name:** `<TaskBlockCard date={...} items={...} />`

#### 5. Notifications Pill
- **Visual:** Black pill at bottom showing "Notifications(5)" with count
- **SalesInject mapping:** Paperclip activity indicator
- **Component name:** `<NotificationPill count={...} />`

#### 6. Real Estate / Property Detail Hero
- **Visual:** "Project Greenville Park" with image hero + stats row (Available flats · Views · Clients · Chats)
- **SalesInject mapping:** Campaign detail page (replace property with brand campaign)
- **Component name:** `<CampaignDetailHero image stats tabs />`

#### 7. Tab Pills Row
- **Visual:** Rounded pill tabs ("Leads", "Realtors", "Investors", "Price chart", "Tours") with one filled pink (active)
- **SalesInject mapping:** Filter tabs on scout results / campaign detail
- **Component name:** `<PillTabs options={...} value={...} />`

#### 8. Price/Metric Line Chart
- **Visual:** Dark card with "Price level 2023", green line chart, tooltip showing value
- **SalesInject mapping:** Engagement / follower growth chart for influencers
- **Component name:** `<MetricLineChart data={...} tooltip={...} />`

#### 9. Sparkline Mini-Card
- **Visual:** Small color-blocked card with a sparkline + label ("Leads activity per week")
- **SalesInject mapping:** Mini KPI widgets on dashboard
- **Component name:** `<SparklineCard label={...} color={...} data={...} />`

#### 10. Donut Chart Card
- **Visual:** Small card with "Source" label + donut + legend
- **SalesInject mapping:** Platform source breakdown (TikTok / IG / YT / X)
- **Component name:** `<DonutCard label={...} segments={...} />`

#### 11. Bar Chart Card with Variance Colors
- **Visual:** "Win&Lost deals" with alternating teal/yellow/pink bars
- **SalesInject mapping:** Pitch-success vs rejection breakdown
- **Component name:** `<VarianceBarsCard />`

#### 12. Calendar Month Strip
- **Visual:** Day-of-week header + numbered cells, active day filled pink
- **SalesInject mapping:** Mission calendar / schedule view
- **Component name:** `<MonthStrip value={...} onSelect={...} />`

#### 13. Timeline Event Card (with participants)
- **Visual:** "Team Call From 12:30 to 16:00" + stacked participant avatars
- **SalesInject mapping:** Scheduled mission timeline entry
- **Component name:** `<TimelineEvent time={...} participants={...} />`

#### 14. Expandable Contact Detail Card
- **Visual:** Green card with avatar+name collapsed → expanded shows phone, email, manager, etc.
- **SalesInject mapping:** Influencer contact detail (email, manager, rate card) — **perfect for Paperclip sidebar**
- **Component name:** `<ContactDetailCard expanded={...} />`

#### 15. Source/Channel List Row
- **Visual:** Dark row with light background chip (Facebook / Instagram / Website / Email)
- **SalesInject mapping:** Connected platforms list on profile
- **Component name:** `<ChannelRow name={...} icon={...} connected={...} />`

#### 16. Project Card (small)
- **Visual:** Rounded card with image hero + title + 3 stat rows with icons
- **SalesInject mapping:** Past campaign card on profile
- **Component name:** `<CampaignCard image={...} title={...} stats={...} />`

#### 17. Campaign Progress Bar Card
- **Visual:** Yellow card with "Campaign · Project Greenville Park" + horizontal progress slider
- **SalesInject mapping:** Active mission progress widget
- **Component name:** `<CampaignProgressCard progress={...} />`

#### 18. Table Row (dark compact)
- **Visual:** Name · Amount · Status · Contacts — dense table with status pills and icon actions
- **SalesInject mapping:** Paperclip items in detail view / CSV export preview
- **Component name:** `<DataTable rows={...} columns={...} />`

#### 19. Notification Card (color-coded)
- **Visual:** Green/white notification tiles: title bold + sub-line + "Just now" timestamp
- **SalesInject mapping:** Paperclip notification feed
- **Component name:** `<NotificationCard variant="success|info|warning" time={...} />`

#### 20. Chat Thread List Row
- **Visual:** Avatar + name + last message preview + timestamp right
- **SalesInject mapping:** Telegram DM preview / CRM inbox
- **Component name:** `<ChatRow />`

#### 21. Campaign-with-Slider Row
- **Visual:** Yellow pill row showing campaign name + slider control + chevron
- **SalesInject mapping:** Mission budget/reach slider in settings
- **Component name:** `<SliderRow label={...} value={...} onChange={...} />`

#### 22. Fixed Bottom Tab Bar with Selected-White-Pill
- **Visual:** 4 icons on dark bg, selected one wrapped in white pill with label
- **SalesInject mapping:** Current bottom nav — already close, refine to match active-state treatment
- **Component name:** Refine existing `<BottomNav />`

---

## 🗺 Implementation Priority Map

Rank components by value × effort for the next UI sprint:

### 🔥 High Priority (Reuse Wins)
1. `DopamineTile` — the signature card. Enables instantly on-brand dashboard/agents screens.
2. `SparklineCard` + `DonutCard` + `MetricLineChart` — brings the dashboard to life with Scout data.
3. `ContactDetailCard` — unblocks Paperclip sidebar influencer detail view (a Pending item in tracker).
4. `InfluencerPin` + `LandmarkPin` — completes `scout_reports → map pins` (a Pending item).
5. `NotificationCard` — Paperclip activity feed (a Pending item).

### 🟡 Medium Priority
6. `SplashScreen` with sparkle ornament
7. `CampaignDetailHero` for dedicated campaign pages
8. `ContentStrip` for influencer portfolio previews
9. `PillTabs` for filter rows
10. `FloatingActionBar` for map controls

### 🟢 Low Priority / Nice-to-have
- `MonthStrip`, `TimelineEvent`, `TaskBlockCard` — useful when scheduling is added
- `DataTable`, `CampaignProgressCard` — for v2 analytics screens
- `MiniMap Preview Card` — when multi-region campaigns exist

---

## 🎨 Design Token Summary

**Both reference images converge on the same language:**

| Token | Value | Used for |
|---|---|---|
| Background | `#0A0A0A` → `#141414` | App canvas, card surface |
| Primary accent | `#E5FF45` (acid yellow) | Primary CTAs, highlight cards |
| Success accent | `#5FF08A` (terminal green) | Positive states, activity |
| Alert accent | `#FF3D9A` (hot pink) | New items, notifications |
| Lime accent | `#C9FF4D` | Secondary highlights |
| Text primary | `#FAFAFA` | Body copy on dark |
| Text on-accent | `#0A0A0A` | Text on colored tiles |

**Typography:** Bold sans-serif for headlines (Inter Black / Satoshi Black), monospace optional for technical values ("13 MPH" style stat pins).

**Radius:** Aggressive rounding — `rounded-2xl` to `rounded-3xl` for cards, fully `rounded-full` for pills.

**Shadows:** Minimal. Depth comes from color contrast, not shadow.

---

## 🚦 Process Rule

**Before implementing ANY new UI component:**
1. Check this document — does one of the 34 patterns above cover it?
2. If yes → reuse + adapt. Document the adaptation in today's session log.
3. If no → design it, then **add it to this document** so the next session reuses it.

This is a living catalog. Update as we build.
