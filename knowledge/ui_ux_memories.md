# SalesInject UI/UX Memories

Chronological log of UI/UX design and frontend development decisions, challenges, and solutions.

## Core UI/UX Directives
- **Platform**: Telegram Mini App (mobile-first, vertical layout)
- **Design System**: Tailwind CSS with custom components
- **Map Visualization**: DeckGL for interactive geospatial data
- **Components**: Paperclip sidebar, agent cards, task panels, map pins
- **State Management**: React hooks + TanStack Query for server state
- **Theming**: Light/dark mode support (future)

## Conversation Log

### [2026-04-25] — UI/UX Agent Setup
- **Target**: Establish dedicated UI/UX agent with memory logging
- **Created**: `knowledge/ui_ux_memories.md` and `knowledge/sessions/ui-ux/` directory
- **Agent Configuration**: `.agents/ui-ux.md` with focus on frontend development
- **Integration**: Updated `knowledge/index.md` to include UI/UX documentation

### [2026-04-25] — Design Token & Landing Page Update
- **Target**: Update design tokens to match reference palette and improve landing page for deployment
- **Actions**: Updated tailwind.config.js with brand colors, updated CSS variables (war-*), created SplashScreen component, replaced Landing.tsx, fixed TypeScript build errors, resolved CSS build issue with noise texture
- **Result**: Landing page now uses modern splash screen with sparkle ornament, design tokens aligned with reference images, production build passes successfully

---

*This file will be updated after each UI/UX development session.*