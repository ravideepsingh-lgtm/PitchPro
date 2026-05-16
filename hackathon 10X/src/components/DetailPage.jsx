import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  ArrowLeft,
  BarChart3,
  CalendarClock,
  CheckCircle2,
  LoaderCircle,
  MapPin,
  PhoneCall,
  ShieldCheck,
  Trophy,
  Users,
  X,
} from 'lucide-react';
import { getClientSegment, getClientSegmentLeads } from '../data/clientSegmentData';
import { formatCount } from '../data/serviceTurnoverGrid';

const leadColumns = [
  'Glid',
  'Company',
  'City',
  'Vintage',
  'Location',
  'BL Active',
  'BL Consumed',
  'Major Cities',
  'A Rank',
  'Call Success',
  'GST',
  'IEC',
  'TAN',
  'Action',
];

const iconMap = {
  dlp: Users,
  blDau: CalendarClock,
  engagement: BarChart3,
  majorCities: MapPin,
  rank: Trophy,
  callSuccess: PhoneCall,
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';
const ANALYZE_API_URL = `${API_BASE_URL}/api/seller/analyze`;

const loadingMessages = [
  'Analysing seller data...',
  'Loading business signals...',
  'Checking engagement patterns...',
  'Preparing agentic insights...',
  'Almost there...',
];

const formatAnalysisLabel = (key) =>
  key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());

const scoreLabelMap = {
  profile_strength: 'Profile Strength',
  profile_strength_score: 'Profile Strength',
  engagement_score: 'Engagement Score',
  friction_penalty: 'Friction Penalty',
  prime_segment_boost: 'Seller Segment Score',
  segment_boost: 'Seller Segment Score',
  seller_segment_score: 'Seller Segment Score',
  total_sss: 'Seller Sentiment Score',
};

const scoreContextMap = {
  profile_strength: 'based on Compliance & Trust, Business Scalability, Vintage & Company Type',
  profile_strength_score: 'based on Compliance & Trust, Business Scalability, Vintage & Company Type',
  engagement_score: 'based on buylead engagement and call success %',
  friction_penalty: 'based on irrelevancy feedback and complaints',
  prime_segment_boost: 'based on category, products and locations',
  segment_boost: 'based on category, products and locations',
  seller_segment_score: 'based on category, products and locations',
};

const getScoreLabel = (key) => scoreLabelMap[key] ?? formatAnalysisLabel(key);

const getDecisionTone = (decision) => {
  const normalizedDecision = String(decision || '').trim().toLowerCase();

  if (normalizedDecision === 'upsell') return 'positive';
  if (normalizedDecision.includes('hold') || normalizedDecision.includes('do not upsell')) return 'negative';
  if (normalizedDecision.includes('conditional') || normalizedDecision.includes('monitor')) return 'warning';

  return 'warning';
};

const renderListItems = (items, emptyLabel) => {
  if (!Array.isArray(items) || items.length === 0) {
    return <li className="analysis-muted">{emptyLabel}</li>;
  }

  return items.map((item, index) => <li key={`${item}-${index}`}>{String(item)}</li>);
};

function AnalysisResult({ response }) {
  const analysis = response?.final_analysis ?? {};
  const scoreBreakdown = analysis.score_breakdown ?? {};
  const scoreEntries = Object.entries(scoreBreakdown).filter(([key]) => key !== 'total_sss');
  const totalScore = scoreBreakdown.total_sss ?? analysis.seller_sentiment_score ?? 0;
  const scorePercent = Math.max(0, Math.min(Number(totalScore) || 0, 100));
  const decision = analysis.decision ?? 'Pending';
  const decisionTone = getDecisionTone(decision);
  const scoreDisplay = analysis.seller_sentiment_score ?? scoreBreakdown.total_sss ?? 'N/A';

  return (
    <div className="analysis-result">
      <div className={`analysis-hero analysis-decision-${decisionTone}`}>
        <div>
          <h2>{decision}</h2>
          {decisionTone === 'positive' && (
            <p>
              {analysis.current_plan || 'Current plan unavailable'} to{' '}
              {analysis.recommended_next_tier || 'recommended tier unavailable'}
            </p>
          )}
        </div>
      </div>

      <div className="analysis-score-panel">
        <div className="analysis-score-header">
          <span>Seller sentiment score</span>
          <strong>{scoreDisplay === 'N/A' ? scoreDisplay : `${scoreDisplay}/100`}</strong>
        </div>
        <div className="analysis-score-track" aria-label={`Seller sentiment score ${scorePercent} out of 100`}>
          <span style={{ width: `${scorePercent}%` }} />
        </div>
        <div className="analysis-tag-row">
          <span>{analysis.sentiment_class || 'Sentiment unavailable'}</span>
          <span>{analysis.seller_intent_type || 'Intent unavailable'}</span>
        </div>
      </div>

      <div className="analysis-metric-grid">
        {scoreEntries.map(([key, value]) => (
          <div className="analysis-metric" key={key}>
            <span>{getScoreLabel(key)}</span>
            <div className="analysis-metric-value">
              <strong>{value ?? 'N/A'}</strong>
              {scoreContextMap[key] && <em>{scoreContextMap[key]}</em>}
            </div>
          </div>
        ))}
      </div>

      <div className="analysis-two-column">
        <section className="analysis-section">
          <div className="analysis-section-title">
            <CheckCircle2 size={17} />
            <h3>What's Good</h3>
          </div>
          <ul>{renderListItems(analysis.why_upsell, 'No positive reasons returned by the API.')}</ul>
        </section>

        <section className="analysis-section">
          <div className="analysis-section-title">
            <AlertTriangle size={17} />
            <h3>Risks</h3>
          </div>
          <ul>{renderListItems(analysis.why_not_risks, 'No blocking risks returned by the API.')}</ul>
        </section>
      </div>

      <section className="analysis-section">
        <div className="analysis-section-title">
          <ShieldCheck size={17} />
          <h3>Recommendation</h3>
        </div>
        <p className="analysis-recommendation">{analysis.final_recommendation || 'No final recommendation returned.'}</p>
      </section>
    </div>
  );
}

export default function DetailPage({ selectedCard, onBack }) {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [analysisRow, setAnalysisRow] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisError, setAnalysisError] = useState('');
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const turnoverLabel = selectedCard.turnoverKey ?? 'All pricing slabs';
  const segment = getClientSegment(selectedCard);
  const trustRows = segment?.trust ?? [];
  const detailCards = segment?.cards ?? [];
  const leadRows = selectedCategory ? getClientSegmentLeads(selectedCard, selectedCategory.dataKey) : [];
  const visibleLeadRows = leadRows.slice(0, 10);

  useEffect(() => {
    if (!analysisRow || !isAnalyzing) return undefined;

    const intervalId = window.setInterval(() => {
      setLoadingMessageIndex((currentIndex) => (currentIndex + 1) % loadingMessages.length);
    }, 1800);

    return () => window.clearInterval(intervalId);
  }, [analysisRow, isAnalyzing]);

  useEffect(() => {
    if (!analysisRow) return undefined;

    const controller = new AbortController();

    const minimumLoaderTime = new Promise((resolve) => {
      window.setTimeout(resolve, 5000);
    });

    const analysisRequest = fetch(ANALYZE_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ glid: Number(analysisRow.glid), dry_run: false }),
      signal: controller.signal,
    }).then(async (response) => {
      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        throw new Error(errorBody?.detail || `Analyze request failed with status ${response.status}`);
      }

      const apiResponse = await response.json();
      console.log('Analyze API response:', apiResponse);

      return apiResponse;
    });

    Promise.allSettled([analysisRequest, minimumLoaderTime])
      .then(([requestResult]) => {
        if (requestResult.status === 'rejected') {
          throw requestResult.reason;
        }

        setAnalysisResult(requestResult.value);
      })
      .catch((error) => {
        if (error.name !== 'AbortError') {
          setAnalysisError(error.message || 'The seller analysis API did not return a response. Please try again.');
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsAnalyzing(false);
        }
      });

    return () => controller.abort();
  }, [analysisRow]);

  const startAnalysis = (row) => {
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setAnalysisError('');
    setLoadingMessageIndex(0);
    setAnalysisRow(row);
  };

  const closeAnalysisModal = () => {
    setAnalysisRow(null);
    setIsAnalyzing(false);
    setAnalysisResult(null);
    setAnalysisError('');
  };

  return (
    <main className="detail-page">
      <header className="detail-header">
        <button type="button" className="back-button" onClick={onBack} aria-label="Back to dashboard">
          <ArrowLeft size={20} />
        </button>

        <div className="detail-meta-line">
          <span className="detail-service-name">{selectedCard.label}</span>
          <div className="detail-meta-line">
            <span>( Turnover : {turnoverLabel} )</span>
            <span>{formatCount(selectedCard.count)} sellers</span>
          </div>
        </div>

        <div className="trust-summary" aria-label="Trust values">
          {trustRows.map((item) => (
            <button
              key={item.label}
              type="button"
              className={`trust-chip ${selectedCategory?.id === `trust-${item.label}` ? 'selected' : ''}`}
              onClick={() =>
                setSelectedCategory({
                  id: `trust-${item.label}`,
                  dataKey: item.dataKey,
                  group: '',
                  label: item.label,
                  value: item.value,
                  count: item.count,
                })
              }
            >
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </button>
          ))}
        </div>
      </header>

      <section className="detail-card-grid" aria-label="Segment detail cards">
        {detailCards.map((template, templateIndex) => {
          const Icon = iconMap[template.key] ?? Users;
          const rows = template.rows;

          return (
            <motion.article
              key={template.key}
              className="detail-card"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: templateIndex * 0.03 }}
            >
              <div className="detail-card-icon" aria-hidden="true">
                <Icon size={18} />
              </div>

              <h2>{template.title}</h2>

              <div className="detail-row-list">
                {rows.map((row) => (
                  <button
                    key={row.label}
                    type="button"
                    className={`detail-row ${selectedCategory?.id === `${template.key}-${row.label}` ? 'selected' : ''}`}
                    onClick={() =>
                      setSelectedCategory({
                        id: `${template.key}-${row.label}`,
                        dataKey: row.dataKey,
                        group: template.title,
                        label: row.label,
                        value: row.value,
                        count: row.count,
                      })
                    }
                  >
                    <p>{row.label}</p>
                    <strong>{row.value}</strong>
                  </button>
                ))}
              </div>
            </motion.article>
          );
        })}
      </section>

      {selectedCategory && (
        <motion.section
          className="lead-list-section"
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.22 }}
        >
          <div className="lead-list-header">
            <div>
              <h2>{[selectedCategory.group, selectedCategory.label].filter(Boolean).join(' | ')}</h2>
            </div>
            <strong>Showing 10 sellers out of {formatCount(selectedCategory.count)} sellers</strong>
          </div>

          <div className="lead-table-wrap">
            <table className="lead-table">
              <thead>
                <tr>
                  {leadColumns.map((column) => (
                    <th key={column}>{column}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {visibleLeadRows.map((row) => (
                  <tr key={row.glid}>
                    <td>{row.glid}</td>
                    <td>{row.company}</td>
                    <td>{row.city}</td>
                    <td>{row.vintage}</td>
                    <td>{row.location}</td>
                    <td>{row.blActive}</td>
                    <td>{row.blConsumed}</td>
                    <td>{row.majorCities}</td>
                    <td>{row.aRank}</td>
                    <td>{row.callSuccess}</td>
                    <td>{row.gst}</td>
                    <td>{row.iec}</td>
                    <td>{row.tan}</td>
                    <td>
                      <button type="button" className="analyze-button" onClick={() => startAnalysis(row)}>
                        Analyze
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.section>
      )}

      {analysisRow && (
        <div className="analysis-modal-overlay">
          <motion.div
            className="analysis-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="analysis-modal-title"
            initial={{ opacity: 0, y: 16, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.2 }}
          >
            <button type="button" className="analysis-modal-close" onClick={closeAnalysisModal} aria-label="Close analysis popup">
              <X size={18} />
            </button>

            <span className="analysis-kicker">Upsell Analysis</span>
            <p className="analysis-seller-line">
              GLUSER ID {analysisRow.glid} | {analysisRow.company}
            </p>

            {isAnalyzing && (
              <div className="analysis-loader" aria-live="polite">
                <LoaderCircle size={34} />
                <strong>{loadingMessages[loadingMessageIndex]}</strong>
                <span>Sending GLID {analysisRow.glid} to the analysis agent.</span>
              </div>
            )}

            {!isAnalyzing && analysisError && <p className="analysis-error">{analysisError}</p>}

            {!isAnalyzing && analysisResult && (
              <AnalysisResult response={analysisResult} />
            )}
          </motion.div>
        </div>
      )}
    </main>
  );
}
