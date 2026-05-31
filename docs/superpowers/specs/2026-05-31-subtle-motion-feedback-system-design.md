# Subtle Motion & Feedback System Design Specification

## Overview
This document describes the implementation of a subtle motion and feedback system across the SalesInject frontend to create visually engaging, responsive interactions that enhance user experience through tactile feedback and refined micro-interactions.

## Architecture
The system implements a layered approach:
1. **CSS Variables Foundation** - Defines reusable animation primitives
2. **Base Interaction Styles** - Applies consistent hover, active, and focus states
3. **Reusable Components** - Encapsulates common interaction patterns
4. **Page-Specific Enhancements** - Applies interactions to key user journeys
5. **Performance Optimizations** - Ensures smooth experience across devices

## Design Tokens & CSS Variables

Added to `:root` in `frontend/src/index.css`:
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

## Base Interaction Styles

Applied globally to interactive elements:
- **Transitions**: All interactive elements use `--transition-medium` for smooth state changes
- **Hover Lift**: Elements lift 2px on hover with subtle shadow
- **Active Press**: Elements return to baseline on press with reduced shadow
- **Focus States**: Visible 2px outline for accessibility
- **Ripple Effect**: Material-design inspired click feedback
- **Scroll Reveal**: Sections animate in on scroll

## Reusable Components

Created in `frontend/src/components/`:
1. **HoverLift.tsx** - Applies lift-on-hover effect
2. **RippleEffect.tsx** - Adds click ripple feedback
3. **PulseAnimation.tsx** - Applies subtle pulsing animation

Exported via `frontend/src/components/index.ts`

## Page-Specific Enhancements

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
- StoryCard component with hover effects

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
- Splash screen with title pulse animation
- Permission gate with hover effects on all interactive elements

### Bottom Navigation & Live Ticker
- Navigation items with hover lift and active states
- Live ticker with smooth text movement
- Ticker items with hover scale effect
- Animated ticker icon with float animation

## Performance & Accessibility Features

### Prefers-Reduced-Motion Support
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
    scroll-behavior: auto !important;
  }
  
  /* Disable non-essential animations */
  .pulse-loader, .ticker-content, .progress-fill {
    animation: none !important;
  }
  
  /* Reduce interaction intensity */
  .btn-primary:hover, .btn-secondary:hover, .onboarding-option:hover {
    transform: translateY(-1px) !important;
  }
}
```

### Will-Change Properties
Elements expected to change use `will-change: transform` or `will-change: opacity` for better rendering performance.

### Accessibility
- Proper focus outlines on all interactive elements
- Sufficient color contrast maintained
- Keyboard navigation fully functional
- Screen reader compatible

## Implementation Summary

### Files Modified
- `frontend/src/index.css` - Core CSS variables and base styles
- `frontend/src/pages/Landing.tsx` - Landing page enhancements
- `frontend/src/pages/MissionFeed.tsx` - Mission feed interactions
- `frontend/src/pages/MapPage.tsx` - Map page interactions
- `frontend/src/pages/Onboarding.tsx` - Onboarding flow interactions
- `frontend/src/components/BottomNavigation.tsx` - Bottom navigation enhancements
- `frontend/src/components/LiveTicker.tsx` - Live ticker enhancements
- `frontend/src/components/DeckGLMap.tsx` - Map marker interactions
- `frontend/src/components/GenZOverlay.tsx` - Overlay component interactions
- `frontend/src/components/SplashScreen.tsx` - Splash screen animations
- `frontend/src/components/PermissionGate.tsx` - Permission gate interactions
- `frontend/src/components/StoryCard.tsx` - Story card interactions

### Files Created
- `frontend/src/components/RippleEffect.tsx` - Reusable ripple effect
- `frontend/src/components/HoverLift.tsx` - Reusable hover lift
- `frontend/src/components/PulseAnimation.tsx` - Reusable pulse animation

### Component Updates
- `frontend/src/components/index.ts` - Added exports for new components

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

## Testing Approach

1. **Visual Verification** - Manual inspection of all enhanced components
2. **Interaction Testing** - Verified hover, active, focus states work correctly
3. **Animation Testing** - Confirmed scroll reveals, pulses, and ripples function
4. **Performance Testing** - Checked for jank and layout thrashing
5. **Accessibility Testing** - Verified keyboard navigation and screen reader compatibility
6. **Reduced Motion Testing** - Confirmed prefers-reduced-motion media query works

## Success Criteria

- [x] All interactive elements have appropriate hover/active/focus states
- [x] Scroll reveal animations trigger correctly on page sections
- [x] Loading states provide visual feedback during async operations
- [x] Pulse animations draw attention to key CTAs without being distracting
- [x] Ripple effects provide satisfying click feedback
- [x] Reusable components reduce code duplication
- [x] System respects user motion preferences
- [x] Performance remains smooth across device types
- [x] Accessibility standards are maintained