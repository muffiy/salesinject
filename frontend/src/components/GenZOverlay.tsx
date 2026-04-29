
interface FilterOption {
  id: string;
  icon?: string;
  label: string;
  count?: number;
}

interface GenZFilterBarProps {
  options: FilterOption[];
  active: string;
  onChange: (id: string) => void;
}

export function GenZFilterBar({ options, active, onChange }: GenZFilterBarProps) {
  return (
    <div className="genz-filter-bar">
      {options.map((opt) => (
        <button
          key={opt.id}
          className={`genz-pill ${active === opt.id ? 'active' : ''}`}
          onClick={() => onChange(opt.id)}
        >
          {opt.icon && <span className="genz-pill-icon">{opt.icon}</span>}
          <span>{opt.label}</span>
          {opt.count !== undefined && (
            <span className="genz-pill-count">{opt.count}</span>
          )}
        </button>
      ))}
    </div>
  );
}

// ─── Floating Controls ────────────────────────────────────────────────

interface FloatAction {
  id: string;
  icon: string;
  label: string;
  active?: boolean;
  onClick: () => void;
}

interface GenZFloatingControlsProps {
  actions: FloatAction[];
  position?: 'top-right' | 'top-left';
}

export function GenZFloatingControls({ actions, position = 'top-right' }: GenZFloatingControlsProps) {
  return (
    <div className={`genz-float-group ${position}`}>
      {actions.map((a) => (
        <button
          key={a.id}
          className={`genz-float-btn ${a.active ? 'active' : ''}`}
          onClick={a.onClick}
          aria-label={a.label}
          title={a.label}
        >
          {a.icon}
        </button>
      ))}
    </div>
  );
}

// ─── Bottom Action Bar ───────────────────────────────────────────────

interface CategoryOption {
  id: string;
  icon: string;
  label: string;
}

interface GenZBottomBarProps {
  options: CategoryOption[];
  active: string;
  onChange: (id: string) => void;
}

export function GenZBottomBar({ options, active, onChange }: GenZBottomBarProps) {
  return (
    <div className="genz-bottom-bar">
      {options.map((opt) => (
        <button
          key={opt.id}
          className={`genz-pill ${active === opt.id ? 'active' : ''}`}
          onClick={() => onChange(opt.id)}
        >
          <span className="genz-pill-icon">{opt.icon}</span>
          <span>{opt.label}</span>
        </button>
      ))}
    </div>
  );
}

// ─── Bottom Sheet ────────────────────────────────────────────────────

interface BottomSheetAction {
  id: string;
  icon: string;
  label: string;
}

interface GenZBottomSheetProps {
  title: string;
  actions: BottomSheetAction[];
  activeAction: string;
  onActionChange: (id: string) => void;
  triggerLabel: string;
  onTrigger: () => void;
  collapsed: boolean;
  onToggle: () => void;
}

export function GenZBottomSheet({
  title,
  actions,
  activeAction,
  onActionChange,
  triggerLabel,
  onTrigger,
  collapsed,
  onToggle,
}: GenZBottomSheetProps) {
  return (
    <div className={`genz-bottom-sheet ${collapsed ? 'collapsed' : ''}`}>
      <div className="genz-sheet-handle" onClick={onToggle} />
      {!collapsed && (
        <>
          <h2 className="genz-sheet-title">{title}</h2>
          <div className="genz-action-grid">
            {actions.map((a) => (
              <button
                key={a.id}
                className={`genz-action-btn ${activeAction === a.id ? 'active' : ''}`}
                onClick={() => onActionChange(a.id)}
              >
                <span className="genz-action-icon">{a.icon}</span>
                <span>{a.label}</span>
              </button>
            ))}
          </div>
          <button className="genz-trigger" onClick={onTrigger}>
            {triggerLabel}
          </button>
        </>
      )}
    </div>
  );
}

// ─── Marker Badge (Gen-Z styled pill label) ──────────────────────────

interface GenZMarkerBadgeProps {
  label: string;
  selected?: boolean;
  icon?: string;
  color?: string;
}

export function GenZMarkerBadge({ label, selected, icon, color }: GenZMarkerBadgeProps) {
  return (
    <div className={`genz-marker-badge ${selected ? 'selected' : ''}`}>
      <div
        className="genz-marker-dot"
        style={color ? { background: color, boxShadow: `0 0 10px ${color}` } : undefined}
      />
      {icon && <span className="genz-marker-icon">{icon}</span>}
      <span className="genz-marker-label">{label}</span>
    </div>
  );
}