export const TURNOVER_BUCKETS = [
  '0 - 40L',
  '40L - 1.5Cr',
  '1.5Cr - 5Cr',
  '5Cr - 25Cr',
  '25Cr - 100Cr',
  '>100Cr',
];

export const SERVICE_COLUMNS = [
  'Total Customers',
  'MDC',
  'TS',
  'Mcat',
  'SS',
  'LS',
  'Verified Exporter',
  'Others',
];

export const SOURCE_FOLDER =
  'G:\\.shortcut-targets-by-id\\1iJjMP2iLsOSP_ZuLA_P96PJqppjOnxoI\\BJP (Beyond Just Product) - 10X Productivity';

const baseCounts = {
  '0 - 40L': {
    'Total Customers': 1284,
    MDC: 318,
    TS: 206,
    Mcat: 184,
    SS: 142,
    LS: 118,
    'Verified Exporter': 97,
    Others: 219,
  },
  '40L - 1.5Cr': {
    'Total Customers': 1098,
    MDC: 276,
    TS: 181,
    Mcat: 163,
    SS: 132,
    LS: 104,
    'Verified Exporter': 85,
    Others: 157,
  },
  '1.5Cr - 5Cr': {
    'Total Customers': 872,
    MDC: 238,
    TS: 146,
    Mcat: 134,
    SS: 101,
    LS: 86,
    'Verified Exporter': 79,
    Others: 88,
  },
  '5Cr - 25Cr': {
    'Total Customers': 626,
    MDC: 181,
    TS: 118,
    Mcat: 96,
    SS: 79,
    LS: 61,
    'Verified Exporter': 53,
    Others: 38,
  },
  '25Cr - 100Cr': {
    'Total Customers': 342,
    MDC: 105,
    TS: 74,
    Mcat: 49,
    SS: 42,
    LS: 31,
    'Verified Exporter': 28,
    Others: 13,
  },
  '>100Cr': {
    'Total Customers': 154,
    MDC: 45,
    TS: 36,
    Mcat: 21,
    SS: 19,
    LS: 14,
    'Verified Exporter': 12,
    Others: 7,
  },
};

const sumService = (service) =>
  TURNOVER_BUCKETS.reduce((total, bucket) => total + (baseCounts[bucket][service] || 0), 0);

const sumTurnover = (bucket) => baseCounts[bucket]['Total Customers'] || 0;

export const customerGridData = {
  generatedFrom: SOURCE_FOLDER,
  turnoverBuckets: TURNOVER_BUCKETS,
  services: SERVICE_COLUMNS,
  serviceCards: SERVICE_COLUMNS.map((service) => ({
    key: service,
    service,
    customerCount: sumService(service),
  })),
  turnoverCards: TURNOVER_BUCKETS.map((bucket) => ({
    key: bucket,
    turnover: bucket,
    customerCount: sumTurnover(bucket),
  })),
  counts: baseCounts,
};
