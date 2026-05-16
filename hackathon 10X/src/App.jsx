import { Suspense, lazy, useState } from 'react';
import TopBar from './components/TopBar';
import InteractiveGrid from './components/InteractiveGrid';
import './index.css';

const DetailPage = lazy(() => import('./components/DetailPage'));

function App() {
  const [selectedCard, setSelectedCard] = useState(null);

  if (selectedCard) {
    return (
      <div className="app-container">
        <Suspense fallback={<div className="detail-loading">Loading segment data...</div>}>
          <DetailPage selectedCard={selectedCard} onBack={() => setSelectedCard(null)} />
        </Suspense>
      </div>
    );
  }

  return (
    <div className="app-container">
      <TopBar />

      <InteractiveGrid selectedCard={selectedCard} onSelect={setSelectedCard} />
    </div>
  );
}

export default App;
