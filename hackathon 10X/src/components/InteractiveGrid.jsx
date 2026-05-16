import { motion } from 'framer-motion';
import {
  BadgeCheck,
  BarChart3,
  Boxes,
  Crown,
  Gem,
  ShieldCheck,
  Sparkles,
  Star,
  Users,
} from 'lucide-react';
import {
  SUMMARY_CARDS,
  TABLE_COLUMNS,
  TURNOVER_KEYS,
  formatCompactCount,
  formatCount,
  getGridCount,
  getServiceTotal,
} from '../data/serviceTurnoverGrid';

const iconMap = {
  customers: Users,
  catalog: Star,
  trustseal: Sparkles,
  maximiser: BadgeCheck,
  star: Gem,
  leader: Boxes,
  exporter: BarChart3,
  plPlus: Crown,
};

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.04 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0, transition: { duration: 0.2 } },
};

function isSelectedSummary(selectedCard, serviceKey) {
  return selectedCard?.type === 'summary' && selectedCard.serviceKey === serviceKey;
}

function isSelectedCell(selectedCard, serviceKey, turnoverKey) {
  return (
    selectedCard?.type === 'cell' &&
    selectedCard.serviceKey === serviceKey &&
    selectedCard.turnoverKey === turnoverKey
  );
}

export default function InteractiveGrid({ selectedCard, onSelect }) {
  return (
    <motion.main
      className="dashboard-shell"
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      <section className="summary-card-grid" aria-label="Service totals">
        {SUMMARY_CARDS.map((card) => {
          const Icon = iconMap[card.key] ?? ShieldCheck;
          const total = getServiceTotal(card.key);

          return (
            <motion.article
              key={card.key}
              className={`summary-card ${card.color} ${isSelectedSummary(selectedCard, card.key) ? 'selected' : ''}`}
              variants={itemVariants}
            >
              <div className="summary-card-header">
                <span>{card.label}</span>
                <Icon size={20} strokeWidth={2.2} />
              </div>

              <button
                type="button"
                className="metric-button summary-value"
                onClick={() =>
                  onSelect({
                    type: 'summary',
                    serviceKey: card.key,
                    label: card.label,
                    count: total,
                  })
                }
              >
                {formatCompactCount(total)}
              </button>
            </motion.article>
          );
        })}
      </section>

      <motion.section className="turnover-table-wrap" variants={itemVariants}>
        <table className="turnover-table">
          <thead>
            <tr>
              <th>Turnover</th>
              {TABLE_COLUMNS.map((column) => (
                <th key={column.key}>{column.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {TURNOVER_KEYS.map((turnoverKey) => (
              <tr key={turnoverKey}>
                <th scope="row">
                  <span className="turnover-label">
                    <span aria-hidden="true" />
                    {turnoverKey}
                  </span>
                </th>
                {TABLE_COLUMNS.map((column) => {
                  const count = getGridCount(column.key, turnoverKey);

                  return (
                    <td key={column.key}>
                      <button
                        type="button"
                        className={`metric-button table-value ${isSelectedCell(selectedCard, column.key, turnoverKey) ? 'selected' : ''}`}
                        onClick={() =>
                          onSelect({
                            type: 'cell',
                            serviceKey: column.key,
                            label: column.label,
                            turnoverKey,
                            count,
                          })
                        }
                      >
                        {formatCount(count)}
                      </button>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </motion.section>
    </motion.main>
  );
}
