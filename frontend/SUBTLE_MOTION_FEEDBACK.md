# Subtle Motion & Feedback System

This document describes the subtle motion and feedback system implemented across the SalesInject frontend to create visually engaging, responsive interactions.

## Overview

The system adds subtle micro-interactions and feedback mechanisms throughout the frontend to create a more engaging, responsive user experience. It implements CSS-based micro-interactions, reusable interaction components, and performance optimizations.

## Architecture

### Design Tokens & CSS Variables

Defined in `frontend/src/index.css`:
```css
/* Interaction Variables for Subtle Motion & Feedback System */
--transition-fast: 150ms ease-in-out;
--transition-medium: 300ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
--hover-lift: translateY(-2px);
--active-press: translateY(0);
--hover-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
--active-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
--ripple-color: rgba(255, 255, 255, 0.3);
--pulse-delay: 2s;
```

### Base Interaction Styles

Applied globally to interactive elements:
- Transitions: All interactive elements use `--transition-medium` for smooth state changes
- Hover Lift: Elements lift 2px on hover with subtle shadow
- Active Press: Elements return to baseline on press with reduced shadow
- Focus States: Visible 2px outline for accessibility
- Ripple Effect: Material-design inspired click feedback
- Scroll Reveal: Sections animate in on scroll

## Reusable Components

Located in `frontend/src/components/`:
1. **HoverLift.tsx** - Applies lift-on-hover effect
2. **RippleEffect.tsx** - Adds click ripple feedback
3. **PulseAnimation.tsx** - Applies subtle pulsing animation

## Usage Guidelines

### HoverLift
```tsx
import { HoverLift } from '@/components/HoverLift';

<HoverLift liftAmount={3}>
  <Button>Click Me</Button>
</HoverLift>
```

### RippleEffect
```tsx
import { RippleEffect } from '@/components/RippleEffect';

<RippleEffect onClick={handleAction}>
  <Button>Action</Button>
</RippleEffect>
```

### PulseAnimation
```tsx
import { PulseAnimation } from '@/components/PulseAnimation';

<PulseAnimation className="cta-pulse" pulseScale={1.05} pulseDuration="3s">
  <Button>Primary CTA</Button>
</PulseAnimation>
```

## Implementation Details

### Landing Page
- Navigation buttons with hover lift
- Hero section buttons with micro-interactions
- Stats cards with individual hover effects
- "How It Works" and Features sections with scroll reveal
- Final CTA with pulse animation
- Section wrappers with scroll reveal animation

### Mission Feed
- Mission card with hover lift and active press
- Claim button with ripple effect
- Skeleton loading states with shimmer animation

### Map Page
- Loading skeleton with pulse spinner
- Interactive map markers with hover scale effect
- Floating controls with hover lift
- Bottom navigation items with hover feedback

### Onboarding Flow
- Input fields with focus/hover states
- Navigation buttons with hover lift
- Progress indicator with animated filling
- Option cards with hover lift

### Bottom Navigation & Live Ticker
- Navigation items with hover lift and active states
- Live ticker with smooth text movement
- Ticker items with hover scale effect
- Animated ticker icon with float animation

## Performance & Accessibility

### Prefers-Reduced-Motion Support
The system respects user motion preferences through media queries that reduce or disable animations when requested.

### Will-Change Properties
Elements expected to change use `will-change: transform` or `will-change: opacity` for better rendering performance.

### Accessibility Features
- Proper focus outlines on all interactive elements
- Sufficient color contrast maintained
- Keyboard navigation fully functional
- Screen reader compatible

## Testing

Unit tests for interaction components are located in:
`frontend/src/__tests__/interaction.test.tsx`

Manual testing should verify:
- Hover effects on all buttons, cards, and interactive elements
- Click/press feedback on all interactive elements
- Ripple effects where implemented
- Scroll reveal animations
- Loading states and skeleton screens
- Pulse animations on CTAs
- Bottom navigation interactions
- Live ticker animations
- Prefers-reduced-motion media query
- Various viewport sizes (mobile, tablet, desktop)
- Performance with browser dev tools (checking for jank, layout thrashing)