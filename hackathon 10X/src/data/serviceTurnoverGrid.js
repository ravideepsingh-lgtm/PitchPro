export const TURNOVER_KEYS = [
  '0 - 40L',
  '40L - 1.5Cr',
  '1.5Cr - 5Cr',
  '5Cr - 25Cr',
  '25Cr - 100Cr',
  '>100Cr',
];

const spreadsheetRows = {
  '0 - 40L': {
    customers: 66079,
    catalog: 37019,
    exporter: 995,
    featuredLeader: 2,
    industryLeader: 15,
    leader: 756,
    maximiser: 7827,
    star: 3118,
    trustseal: 15155,
  },
  '40L - 1.5Cr': {
    customers: 50111,
    catalog: 22743,
    exporter: 599,
    featuredLeader: 2,
    industryLeader: 35,
    leader: 1471,
    maximiser: 8259,
    star: 4548,
    trustseal: 11918,
  },
  '1.5Cr - 5Cr': {
    customers: 44421,
    catalog: 17340,
    exporter: 658,
    featuredLeader: 14,
    industryLeader: 106,
    leader: 2761,
    maximiser: 7665,
    star: 5618,
    trustseal: 9867,
  },
  '5Cr - 25Cr': {
    customers: 30050,
    catalog: 10294,
    exporter: 659,
    featuredLeader: 30,
    industryLeader: 242,
    leader: 3134,
    maximiser: 5056,
    star: 4246,
    trustseal: 6191,
  },
  '25Cr - 100Cr': {
    customers: 7664,
    catalog: 2493,
    exporter: 206,
    featuredLeader: 20,
    industryLeader: 115,
    leader: 1073,
    maximiser: 1120,
    star: 1170,
    trustseal: 1415,
  },
  '>100Cr': {
    customers: 2105,
    catalog: 691,
    exporter: 62,
    featuredLeader: 11,
    industryLeader: 40,
    leader: 322,
    maximiser: 294,
    star: 275,
    trustseal: 394,
  },
};

export const TABLE_COLUMNS = [
  { key: 'customers', label: 'Customers' },
  { key: 'catalog', label: 'MDC' },
  { key: 'trustseal', label: 'TS' },
  { key: 'maximiser', label: 'MAXI' },
  { key: 'star', label: 'SS' },
  { key: 'leader', label: 'LS' },
  { key: 'exporter', label: 'IVE' },
  { key: 'plPlus', label: 'PL+' },
];

export const SUMMARY_CARDS = [
  { key: 'customers', label: 'Customers', total: 219185, color: 'blue' },
  { key: 'catalog', label: 'Catalog', color: 'teal' },
  { key: 'trustseal', label: 'TrustSEAL', color: 'orange' },
  { key: 'maximiser', label: 'Maximiser', color: 'green' },
  { key: 'star', label: 'Star', color: 'purple' },
  { key: 'leader', label: 'Leader', color: 'blue' },
  { key: 'exporter', label: 'Exporter', color: 'teal' },
  { key: 'plPlus', label: 'Premium', color: 'orange' },
];

export const serviceTurnoverPivot = TURNOVER_KEYS.reduce((rows, turnoverKey) => {
  const row = spreadsheetRows[turnoverKey];

  rows[turnoverKey] = {
    ...row,
    plPlus: row.featuredLeader + row.industryLeader,
  };

  return rows;
}, {});

export const SERVICE_KEYS = TABLE_COLUMNS.map((column) => column.key);

export function getServiceTotal(serviceKey) {
  const card = SUMMARY_CARDS.find((item) => item.key === serviceKey);

  if (card?.total) {
    return card.total;
  }

  return TURNOVER_KEYS.reduce(
    (total, turnoverKey) => total + (serviceTurnoverPivot[turnoverKey]?.[serviceKey] ?? 0),
    0,
  );
}

export function getGridCount(serviceKey, turnoverKey) {
  return serviceTurnoverPivot[turnoverKey]?.[serviceKey] ?? 0;
}

export function formatCount(value) {
  return new Intl.NumberFormat('en-IN').format(value);
}

export function formatCompactCount(value) {
  if (value >= 100000) {
    return `${formatShort(value / 100000)}L`;
  }

  if (value >= 1000) {
    return `${formatShort(value / 1000)}K`;
  }

  return formatCount(value);
}

function formatShort(value) {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}
