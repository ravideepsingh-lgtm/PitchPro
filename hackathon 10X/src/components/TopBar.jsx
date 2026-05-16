import { Circle, Grid3X3 } from 'lucide-react';

export default function TopBar() {
  return (
    <header className="top-bar">
      <div className="brand-lockup">
        <div className="brand-icon">
          <Grid3X3 size={18} />
        </div>
        <h1>PitchPro - Customer Upsell Dashboard</h1>
      </div>

      <div className="live-pill">
        <Circle size={10} fill="currentColor" strokeWidth={0} />
        Live
      </div>
    </header>
  );
}
