# 📚 SalesInject Knowledge Base

This directory contains comprehensive documentation for the SalesInject project, an AI-powered Telegram Mini App platform for influencer marketing.

## 📋 Core Documents

### 1. **Hosting Guide** (`hosting_guide.md`)
Complete deployment and operations manual for hosting SalesInject on a production VPS. Covers:
- Server requirements and setup
- Docker deployment with one-command script
- SSL/HTTPS configuration
- Monitoring, backup, and maintenance
- Troubleshooting common issues

### 2. **Deployment Cheat Sheet** (`deployment_cheatsheet.md`)
Quick reference card with essential commands for daily operations, backups, and troubleshooting.

### 3. **Project Business & Architecture Guide** (`project_business_and_architecture_guide.md`)
Strategic overview of the SalesInject platform:
- Business model and market opportunity (MENA focus)
- Technical architecture (React/FastAPI/PostgreSQL/Redis)
- Growth strategy and financial projections
- Competitive analysis

### 4. **Project Tracker** (`project_tracker.md`)
Live status of development progress:
- Completed phases and milestones
- Current work in progress
- Next steps backlog
- Developer notes

### 5. **Project Memories** (`memories.md`)
Chronological log of development decisions, challenges, and solutions. Useful for understanding the evolution of the codebase.

### 6. **UI/UX Memories** (`ui_ux_memories.md`)
Specialized log of frontend design decisions, component development, and user experience improvements. Focused on the visual and interactive aspects of the platform.

## 📁 Sessions Archive

The `sessions/` directory contains detailed session notes:

### General Development Sessions
- `session_2026-04-24.md` - Development session notes
- `session_2026-04-25.md` - Development session notes

### UI/UX Focused Sessions
UI/UX sessions are stored in `sessions/ui-ux/` with date-based naming (`session_YYYY-MM-DD.md`). Use `session_template.md` as a starting point.

## 📚 References

The `references/` directory contains curated design and architecture references:

### 1. **Gen-Z Landing Page Inspiration** (`gen_z_landing_page_inspiration.md`)
10 high-end app landing page references for SalesInject design direction:
- Color palettes and visual systems
- Creator economy app patterns
- 3D visualization inspiration
- Pricing/tier showcase structures

### 2. **Design Folder Components** (`design_folder_components.md`)
**CRITICAL FOR UI IMPLEMENTATION:** Extraction of 34+ reusable UI components from the design reference images:
- Component catalog with visual descriptions
- Direct mapping to SalesInject product screens
- Implementation priority ranking
- Design tokens (colors, radius, typography)
- Process rule: Always check this before building new components

## 🚀 Quick Start

### For New Developers:
1. Read `project_business_and_architecture_guide.md` to understand the project
2. Check `project_tracker.md` for current status
3. Review `memories.md` for historical context

### For UI/UX Development:
1. **Read first:** `references/design_folder_components.md` (component catalog)
2. **Then read:** `references/gen_z_landing_page_inspiration.md` (design direction)
3. **Create session log:** Copy `sessions/ui-ux/session_template.md` → `sessions/ui-ux/session_YYYY-MM-DD.md`
4. **Log after each task:** Update `ui_ux_memories.md` with what you built

### For Deployment:
1. Follow `hosting_guide.md` for production setup
2. Use `deployment_cheatsheet.md` for quick commands
3. Refer to troubleshooting sections if issues arise

## 🔄 Maintenance

- **Update documentation** when making significant changes to architecture or deployment
- **Add session notes** after major development sessions
- **Update project tracker** when completing milestones
- **Review hosting guide** before production deployments
- **Refresh references** if new design inspiration is found (link in `gen_z_landing_page_inspiration.md`)

## 📞 Support

- GitHub Repository: [muffiy/salesinject](https://github.com/muffiy/salesinject)
- Check `hosting_guide.md` troubleshooting section
- Review session notes for similar past issues

---

*Last Updated: 2026-04-25*
*Documentation Version: 3.0*
