import { motion } from 'framer-motion';
import { TURNOVER_KEYS, formatCount, getGridCount } from '../data/serviceTurnoverGrid';

function getPanelTitle(selectedCard) {
  if (selectedCard.type === 'summary') {
    return selectedCard.label;
  }

  return `${selectedCard.label} / ${selectedCard.turnoverKey}`;
}

export default function DataPanel({ selectedCard }) {
  if (!selectedCard) return null;

  const isServiceSummary = selectedCard.type === 'summary';
  const turnoverBreakup = isServiceSummary
    ? TURNOVER_KEYS.map((turnoverKey) => ({
        turnoverKey,
        count: getGridCount(selectedCard.serviceKey, turnoverKey),
      }))
    : [];

  return (
    <motion.div
      className="glass-panel data-panel"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      key={`${selectedCard.type}-${selectedCard.serviceKey}-${selectedCard.turnoverKey ?? 'all'}`}
    >
      <div className="data-panel-header">
        <div>
          <span className="panel-kicker">Selected metric</span>
          <h2>{getPanelTitle(selectedCard)}</h2>
        </div>
        <strong>{formatCount(selectedCard.count)}</strong>
      </div>

      <div className="data-panel-content">
        <div className="selected-data-grid">
          <div className="selected-data-card">
            <span>Service key</span>
            <strong>{selectedCard.label}</strong>
          </div>
          <div className="selected-data-card">
            <span>Customer base</span>
            <strong>{selectedCard.turnoverKey ?? 'All turnover'}</strong>
          </div>
          <div className="selected-data-card">
            <span>Customer count</span>
            <strong>{formatCount(selectedCard.count)}</strong>
          </div>
        </div>

        {isServiceSummary && (
          <div className="turnover-breakup">
            {turnoverBreakup.map((item) => (
              <div key={item.turnoverKey} className="breakup-row">
                <span>{item.turnoverKey}</span>
                <strong>{formatCount(item.count)}</strong>
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
